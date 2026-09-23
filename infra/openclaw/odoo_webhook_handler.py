#!/usr/bin/env python3
"""
FraWo Webhook Handler — v3 (2026-09-23, Claude Code / Odoo #1581)
Läuft auf CT150, Port 19001 (LAN-only)
- /odoo-task: Odoo → triggert ServAssi bei neuen DevOps-Aufgaben
- /alertmanager-hook: Prometheus Alertmanager → triggert ServAssi bei Server-Alarmen
- /klausi-chatter/<secret>: Odoo → Chatter-Erwähnungen
    * @Klausi / @Jarvis / @OpenClaw → ServAssi (OpenClaw-Agent, wie bisher)
    * @Ollama                      → lokales LLM auf dem StudioPC, Antwort
                                     erscheint als "🤖 Ollama Mitarbeiter" im
                                     selben Chatter (eigener Odoo-Nutzer)

v3-Änderungen (Odoo #1581, Freigabe Wolf 23.09.2026):
- KEIN zweiter Webhook: gleicher Eingang, gleiches ACK/Dedupe, nur eine
  zusätzliche Route im Handler.
- Alle Geheimnisse kommen aus /etc/frawo/ollama-chatter.env (root, 0600) statt
  aus dem Quelltext. Fehlt ein Pflichtwert, startet der Dienst NICHT
  (fail closed) — lieber laut aus als leise unsicher.
- 🔴 Fehlerkorrektur im bestehenden @Klausi-Zweig: Odoos nativer Webhook
  liefert `_model`/`_id` des AUSLÖSERS (immer mail.message), der gemeinte
  Vorgang steht in `model`/`res_id`. Bisher wurde `_model`/`_id` bevorzugt —
  der Agent bekam also "mail.message #20597" statt "project.task #1581"
  genannt. Reihenfolge umgedreht.
- Schleifenschutz: Nachrichten, die der Ollama-Nutzer selbst geschrieben hat
  (Partner 160), lösen nichts aus.

v2 (2026-09-06, Jarvis): ACK sofort, Trigger asynchron + serialisiert, Dedupe.
"""
import hashlib
import html as html_mod
import json
import logging
import os
import re
import subprocess
import threading
import time
import urllib.error
import urllib.request
import xmlrpc.client
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("odoo-webhook")

# --- Konfiguration --------------------------------------------------------
# Werte kommen aus der systemd-EnvironmentFile /etc/frawo/ollama-chatter.env.


def _need(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        raise SystemExit(
            f"Pflichtwert {name} fehlt. Erwartet in /etc/frawo/ollama-chatter.env "
            f"(siehe systemd-Unit odoo-webhook.service)."
        )
    return val


TELEGRAM_ID = os.environ.get("FRAWO_TELEGRAM_ID", "5924907152")

SECRET = _need("FRAWO_TASK_SECRET")
ALERT_SECRET = _need("FRAWO_ALERT_SECRET")
KLAUSI_SECRET = _need("FRAWO_CHATTER_SECRET")

ODOO_URL = _need("ODOO_URL")
ODOO_DB = _need("ODOO_DB")
ODOO_LOGIN = _need("ODOO_LOGIN")
ODOO_APIKEY = _need("ODOO_APIKEY")

OLLAMA_URL = _need("OLLAMA_URL").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "frawo-mitarbeiter")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "240"))

# Partner-ID des Odoo-Nutzers "🤖 Ollama Mitarbeiter" — eigene Beiträge dürfen
# niemals eine neue Runde auslösen.
OLLAMA_PARTNER_ID = int(os.environ.get("OLLAMA_PARTNER_ID", "160"))

# --- Dedupe ---------------------------------------------------------------
DEDUPE_TTL = {
    "alert": 1800,   # 30 min: gleicher Alarm (alertname@instance) nur 1x
    "task": 600,     # 10 min: gleicher Odoo-Task nur 1x
    "chatter": 300,  # 5 min: gleiche Chatter-Message nur 1x (ServAssi)
    "ollama": 300,   # 5 min: gleiche Chatter-Message nur 1x (Ollama)
}
_dedupe_lock = threading.Lock()
_recent: dict[str, float] = {}


def is_duplicate(kind: str, key: str) -> bool:
    """True wenn (kind,key) innerhalb der TTL schon gesehen wurde."""
    full = f"{kind}:{key}"
    ttl = DEDUPE_TTL.get(kind, 600)
    now = time.time()
    with _dedupe_lock:
        for k in [k for k, t in _recent.items() if now - t > 3600]:
            del _recent[k]
        seen = _recent.get(full)
        if seen is not None and now - seen < ttl:
            return True
        _recent[full] = now
        return False


# --- Agent-Trigger (asynchron, serialisiert) ------------------------------
_trigger_lock = threading.Lock()

AGENT_PROMPT_TEMPLATE = """NEUER DEVOPS-TASK #{task_id} von Wolf:

**Titel:** {name}
**Beschreibung:** {description}

---
Deine Aufgabe als IT-Mitarbeiter (ServAssi):
1. Recherchiere das Problem/Ziel (nutze Odoo, HA, AzuraCast, SSH — was du brauchst)
2. Setze den Task auf Stage "In Recherche" (stage_id=3) in Odoo
3. Schicke Wolf einen klaren Vorschlag via Telegram:
   - Was du gefunden hast
   - Was du tun willst (konkret)
   - Erwartetes Ergebnis
4. WARTE auf Wolfs Antwort ("mach", "ja", "go" o.ä.)
5. Führe erst nach Freigabe aus
6. Melde Ergebnis + markiere Task als Erledigt (stage_id=6) nach Verifikation

SICHERHEITSREGEL: Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.
"""

ALERT_PROMPT_TEMPLATE = """SERVER-ALARM (von Alertmanager, automatisch, dedupliziert):

{alert_summary}

---
Deine Aufgabe als IT-Mitarbeiter (ServAssi):
1. Prüfe sofort die tatsächliche Ursache (SSH/Exec auf den betroffenen Server, nicht raten)
2. Schicke Wolf eine kurze Einschätzung + 2-4 konkrete Handlungsoptionen mit deiner Empfehlung
3. Bei eindeutig risikoarmen Fällen: sag was du tust und mach es direkt
4. Bei Produktivsystemen/Löschungen/Neustarts von Kernservern: auf Wolfs Antwort warten
5. Nach Freigabe ausführen, verifizieren, kurz zurückmelden

SICHERHEITSREGEL: Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.
"""

KLAUSI_PROMPT_TEMPLATE = """ODOO-CHATTER — jemand hat dich erwähnt (Partner-ID {author_id}, bei Bedarf in Odoo nachschlagen):

**Wo:** {record_name} (Modell: {model}, ID: {res_id})
**Nachricht:** {body}

---
Deine Aufgabe als IT-Mitarbeiter (ServAssi):
1. Verstehe die Frage/das Anliegen
2. Recherchiere was nötig ist (Odoo, HA, AzuraCast, SSH — was du brauchst)
3. Antworte DIREKT im Odoo-Chatter dieses Datensatzes (Modell {model}, ID {res_id}) —
   das ist hier der Hauptkanal, nicht Telegram
4. Bei einfachen Auskünften: antworte sofort im Chatter
5. Bei größeren/riskanten Aktionen: schlage im Chatter vor und warte auf Freigabe
   (Wolf antwortet dann im selben Chatter-Thread)
6. Zusätzlich eine kurze Telegram-Notiz an Wolf, dass du geantwortet hast

SICHERHEITSREGEL: Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.
"""


def _run_agent(message: str, label: str) -> bool:
    try:
        result = subprocess.run(
            [
                "docker", "exec", "openclaw",
                "openclaw", "agent",
                "--session-id", "main",
                "--message", message,
                "--channel", "telegram",
                "--to", TELEGRAM_ID,
                "--deliver",
            ],
            timeout=180,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            log.info(f"Agent triggered successfully for {label}")
            return True
        log.error(f"Agent failed for {label}: {result.stderr[-500:]}")
        return False
    except subprocess.TimeoutExpired:
        log.info(f"Agent started (timeout OK — runs async) for {label}")
        return True
    except Exception as e:
        log.error(f"Error triggering agent for {label}: {e}")
        return False


def trigger_agent_async(message: str, label: str) -> None:
    """Startet den Agent-Trigger im Hintergrund; serialisiert via Lock,
    1 Retry nach 30s bei Fehlschlag. HTTP-Antwort hängt NICHT daran."""
    def worker():
        with _trigger_lock:
            ok = _run_agent(message, label)
            if not ok:
                log.info(f"Retry in 30s for {label}")
                time.sleep(30)
                _run_agent(message, f"{label} (retry)")
    threading.Thread(target=worker, daemon=True).start()


# --- Ollama-Mitarbeiter ---------------------------------------------------

OLLAMA_SYSTEM = """Du bist "Ollama Mitarbeiter" der FraWo GbR — ein schriftlicher
Zuarbeiter im Aufgabensystem (Odoo). Du antwortest im Chatter einer Aufgabe.

Sprache: Deutsch, sachlich, ohne Fachjargon. Wolf hat keine IT-Ausbildung.

Was du darfst: lesen, recherchieren, einordnen, entwerfen, strukturiert berichten.
Was du NICHT darfst und auch nicht behaupten sollst: Buchungen, Bestellungen,
Mails nach draußen, Freigaben erteilen, Server oder Netzwerk ändern, etwas
löschen, eine Aufgabe abschließen. Du hast dafür technisch keine Rechte.

Wenn dir Angaben fehlen, sag das und stelle GENAU EINE Rückfrage.
Erfinde niemals Zahlen, Dateipfade, Geräte oder Messwerte. Was du nicht aus dem
mitgelieferten Text weißt, ist unbekannt — dann schreibst du das.

Antworte IMMER in genau diesen sechs Abschnitten, jeder mit einer Überschrift
in dieser Schreibweise und ohne weitere Überschriften:

Auftrag
Befund
Aktion
Nachweis
Status
Naechster Schritt

Kurz halten: zusammen höchstens etwa 200 Wörter. Keine Einleitung, keine
Grußformel, keine Wiederholung der Frage."""


def _mentions(text_low: str, name_pattern: str) -> bool:
    """Erkennt eine Erwähnung robust.

    Odoos Erwähnungs-Auswahl schreibt den vollen Anzeigenamen samt Emoji in den
    Text — aus "@Ollama" wird "@🤖 Ollama Mitarbeiter", aus "@OpenClaw" wird
    "@🦞 OpenClaw". Eine schlichte Textsuche nach "@ollama" geht dabei leer aus.
    Deshalb: nach dem @ bis zu sechs Zeichen überspringen, die keine Buchstaben
    oder Ziffern sind (Emoji, Leerzeichen).
    """
    return re.search(r"@[^a-z0-9]{0,6}" + name_pattern, text_low) is not None


def _strip_html(raw: str) -> str:
    """Odoo liefert HTML. Für das Modell brauchen wir lesbaren Fließtext."""
    text = re.sub(r"(?i)<br\s*/?>", "\n", raw or "")
    text = re.sub(r"(?i)</(p|div|li|ul|ol|tr|h[1-6])>", "\n", text)
    text = re.sub(r"(?i)<li[^>]*>", "- ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html_mod.unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _to_html(text: str) -> str:
    """Modellantwort (Klartext) in schlichtes, sicheres Odoo-HTML wandeln."""
    out = []
    in_list = False
    for line in (text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(("- ", "* ", "• ")):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append("<li>%s</li>" % html_mod.escape(line[2:].strip()))
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        bare = line.rstrip(":")
        if bare in ("Auftrag", "Befund", "Aktion", "Nachweis", "Status",
                    "Naechster Schritt", "Nächster Schritt"):
            out.append("<p><b>%s</b><br>" % html_mod.escape(bare))
            out.append("__OFFEN__")
            continue
        esc = html_mod.escape(line)
        if out and out[-1] == "__OFFEN__":
            out[-1] = esc + "</p>"
        else:
            out.append("<p>%s</p>" % esc)
    if in_list:
        out.append("</ul>")
    # Übrig gebliebene Platzhalter = Überschrift ohne Text darunter: Absatz zu.
    return "".join("</p>" if p == "__OFFEN__" else p for p in out)


class OdooRPC:
    """Sehr kleiner XML-RPC-Client. Meldet sich als eigener Dienstnutzer an;
    dieser Zugang hat ausschließlich Leserechte auf Projekte/Aufgaben und darf
    Chatter-Beiträge schreiben. Alles andere weist Odoo selbst ab."""

    def __init__(self):
        self.uid = None

    def _login(self):
        if self.uid:
            return self.uid
        common = xmlrpc.client.ServerProxy(
            f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(ODOO_DB, ODOO_LOGIN, ODOO_APIKEY, {})
        if not uid:
            raise RuntimeError("Odoo-Anmeldung als %s fehlgeschlagen" % ODOO_LOGIN)
        self.uid = uid
        return uid

    def call(self, model, method, args, kwargs=None):
        uid = self._login()
        proxy = xmlrpc.client.ServerProxy(
            f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
        return proxy.execute_kw(ODOO_DB, uid, ODOO_APIKEY, model, method,
                                args, kwargs or {})


def _gather_context(rpc: OdooRPC, model: str, res_id: int) -> str:
    """Liest den gemeinten Vorgang plus die letzten Chatter-Beiträge."""
    parts = []
    if model == "project.task":
        rows = rpc.call("project.task", "read", [[res_id]], {
            "fields": ["name", "description", "stage_id", "project_id",
                       "date_deadline"]})
        if rows:
            rec = rows[0]
            parts.append("Aufgabe #%s: %s" % (res_id, rec.get("name") or ""))
            proj = rec.get("project_id")
            if proj:
                parts.append("Projekt: %s" % proj[1])
            stage = rec.get("stage_id")
            if stage:
                parts.append("Stufe: %s" % stage[1])
            if rec.get("date_deadline"):
                parts.append("Frist: %s" % rec["date_deadline"])
            desc = _strip_html(rec.get("description") or "")
            if desc:
                parts.append("Beschreibung:\n%s" % desc[:2500])
    else:
        rows = rpc.call(model, "read", [[res_id]], {"fields": ["display_name"]})
        if rows:
            parts.append("Datensatz %s #%s: %s" % (
                model, res_id, rows[0].get("display_name") or ""))

    msgs = rpc.call("mail.message", "search_read", [[
        ["model", "=", model], ["res_id", "=", res_id],
        ["message_type", "in", ["comment", "email"]],
    ]], {"fields": ["date", "author_id", "body"], "limit": 6,
         "order": "date desc"})
    if msgs:
        lines = []
        for m in reversed(msgs):
            who = (m.get("author_id") or [0, "System"])[1]
            body = _strip_html(m.get("body") or "")[:700]
            if body:
                lines.append("[%s] %s: %s" % (m.get("date"), who, body))
        if lines:
            parts.append("Bisheriger Verlauf (älteste zuerst):\n" + "\n".join(lines))
    return "\n\n".join(parts)


def _ask_ollama(system: str, prompt: str) -> str:
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "options": {"temperature": 0.2, "num_predict": 700},
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/chat", data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return (data.get("message") or {}).get("content", "").strip()


def _post(rpc: OdooRPC, model: str, res_id: int, body_html: str, note: bool = False):
    rpc.call(model, "message_post", [res_id], {
        "body": body_html,
        "message_type": "comment",
        "subtype_xmlid": "mail.mt_note" if note else "mail.mt_comment",
    })


def handle_ollama_async(model: str, res_id: int, record_name: str,
                        question: str, author_id: int) -> None:
    """Fragt das lokale Modell und schreibt die Antwort in denselben Chatter —
    unter dem eigenen Odoo-Nutzer. Läuft im Hintergrund, die HTTP-Antwort an
    Odoo ist längst raus."""
    def worker():
        label = f"{model}#{res_id}"
        rpc = OdooRPC()
        try:
            context = _gather_context(rpc, model, res_id)
        except Exception as e:
            log.error(f"Ollama: Odoo-Kontext für {label} nicht lesbar: {e}")
            return
        prompt = (
            "Vorgang: %s\n\n%s\n\n---\nFrage an dich (Partner-ID %s):\n%s"
            % (record_name, context, author_id, question)
        )
        try:
            answer = _ask_ollama(OLLAMA_SYSTEM, prompt)
        except (urllib.error.URLError, OSError) as e:
            log.warning(f"Ollama nicht erreichbar für {label}: {e}")
            try:
                _post(rpc, model, res_id,
                      "<p>🤖 <b>Ollama Mitarbeiter</b> ist gerade nicht erreichbar "
                      "(StudioPC vermutlich aus). Die Frage bleibt unbeantwortet — "
                      "einfach erneut <code>@Ollama</code> schreiben, wenn der "
                      "Rechner läuft.</p>", note=True)
            except Exception as e2:
                log.error(f"Ollama: Ausfallhinweis nicht zustellbar: {e2}")
            return
        except Exception as e:
            log.error(f"Ollama-Aufruf fehlgeschlagen für {label}: {e}")
            return

        if not answer:
            log.warning(f"Ollama lieferte leere Antwort für {label}")
            return
        body = _to_html(answer[:6000])
        body += ('<p style="color:#888;font-size:90%%">🤖 Automatische Antwort von '
                 '%s (lokales Modell, CT150). Keine Freigabe, keine Buchung, '
                 'kein Abschluss.</p>' % OLLAMA_MODEL)
        try:
            _post(rpc, model, res_id, body)
            log.info(f"Ollama-Antwort gepostet auf {label}")
        except Exception as e:
            log.error(f"Ollama: Antwort nicht zustellbar für {label}: {e}")

    threading.Thread(target=worker, daemon=True).start()


def format_alerts(payload: dict) -> str:
    lines = []
    for alert in payload.get("alerts", []):
        status = alert.get("status", "unknown")
        labels = alert.get("labels", {})
        ann = alert.get("annotations", {})
        icon = "🚨" if status == "firing" else "✅"
        lines.append(
            f"{icon} [{status}] {labels.get('alertname', '?')} "
            f"(instance: {labels.get('instance', '?')}, severity: {labels.get('severity', '?')})\n"
            f"   {ann.get('summary', '')}\n"
            f"   {ann.get('description', '')}"
        )
    return "\n\n".join(lines) if lines else "(keine Alert-Details im Payload)"


def alert_dedupe_key(payload: dict) -> str:
    parts = sorted(
        f"{a.get('labels', {}).get('alertname', '?')}@{a.get('labels', {}).get('instance', '?')}"
        for a in payload.get("alerts", [])
    )
    return "|".join(parts) or "empty"


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        log.info(fmt % args)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        return json.loads(body)

    def _respond(self, code: int, dedup: bool = False):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true, "deduplicated": true}' if dedup else b'{"ok": true}')

    def do_POST(self):
        if self.path == "/odoo-task":
            self._handle_odoo_task()
        elif self.path == "/alertmanager-hook":
            self._handle_alertmanager()
        elif self.path == f"/klausi-chatter/{KLAUSI_SECRET}":
            self._handle_klausi_chatter()
        elif self.path.startswith("/klausi-chatter"):
            log.warning("Unauthorized /klausi-chatter attempt (falsches/fehlendes Secret im Pfad)")
            self.send_response(401)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_odoo_task(self):
        auth = self.headers.get("X-Webhook-Secret", "")
        if auth != SECRET:
            log.warning("Unauthorized /odoo-task attempt")
            self.send_response(401)
            self.end_headers()
            return

        try:
            data = self._read_json()
        except Exception as e:
            log.error(f"Invalid JSON: {e}")
            self.send_response(400)
            self.end_headers()
            return

        task_id = data.get("task_id", "?")
        if is_duplicate("task", str(task_id)):
            log.info(f"Duplicate task #{task_id} ignoriert (TTL)")
            self._respond(200, dedup=True)
            return

        name = data.get("name", "Unbekannter Task")
        description = data.get("description", "Keine Beschreibung")
        description_clean = description[:800] if description else ""

        message = AGENT_PROMPT_TEMPLATE.format(
            task_id=task_id, name=name, description=description_clean,
        )
        log.info(f"Triggering agent for task #{task_id}: {name}")
        self._respond(200)
        trigger_agent_async(message, f"task #{task_id}")

    def _handle_alertmanager(self):
        auth = self.headers.get("Authorization", "")
        if auth != f"Bearer {ALERT_SECRET}":
            log.warning("Unauthorized /alertmanager-hook attempt")
            self.send_response(401)
            self.end_headers()
            return

        try:
            data = self._read_json()
        except Exception as e:
            log.error(f"Invalid JSON: {e}")
            self.send_response(400)
            self.end_headers()
            return

        if data.get("status") != "firing":
            log.info("Alertmanager webhook: nicht 'firing', ignoriert (Alert-Bot deckt Resolved ab)")
            self._respond(200)
            return

        key = alert_dedupe_key(data)
        if is_duplicate("alert", key):
            log.info(f"Duplicate alert ignoriert (TTL): {key}")
            self._respond(200, dedup=True)
            return

        summary = format_alerts(data)
        message = ALERT_PROMPT_TEMPLATE.format(alert_summary=summary)
        log.info(f"Triggering agent for firing alert(s): {summary[:200]}")
        self._respond(200)
        trigger_agent_async(message, "alertmanager")

    def _handle_klausi_chatter(self):
        try:
            data = self._read_json()
        except Exception as e:
            log.error(f"Invalid JSON: {e}")
            self.send_response(400)
            self.end_headers()
            return

        raw_body = (data.get("body") or "")[:4000]
        author_id = int(data.get("author_id") or 0)
        record_name = data.get("record_name") or "unbekannter Datensatz"

        # 🔴 Reihenfolge: `model`/`res_id` ist der gemeinte Vorgang.
        # `_model`/`_id` beschreibt nur den Auslöser (immer mail.message).
        model = data.get("model") or data.get("_model") or "?"
        try:
            res_id = int(data.get("res_id") or data.get("_id") or 0)
        except (TypeError, ValueError):
            res_id = 0

        # Schleifenschutz: was der Ollama-Nutzer selbst schreibt, löst nichts aus.
        if author_id == OLLAMA_PARTNER_ID:
            log.info("Eigenbeitrag von Ollama ignoriert (Schleifenschutz)")
            self._respond(200, dedup=True)
            return

        text = _strip_html(raw_body)
        low = text.lower()
        # "ol{1,2}ama" fängt auch den häufigen Vertipper "@Olama" ab.
        want_ollama = _mentions(low, r"ol{1,2}ama")
        want_agent = any(_mentions(low, t) for t in ("klausi", "jarvis", "openclaw"))

        key = hashlib.sha256(
            f"{model}:{res_id}:{author_id}:{raw_body}".encode()
        ).hexdigest()[:16]

        self._respond(200)

        if want_ollama and res_id:
            if is_duplicate("ollama", key):
                log.info(f"Duplicate @Ollama-Erwähnung ignoriert (TTL): {record_name}")
            else:
                log.info(f"Ollama-Lauf für {model}#{res_id} ({record_name})")
                handle_ollama_async(model, res_id, record_name, text, author_id)

        if want_agent:
            if is_duplicate("chatter", key):
                log.info(f"Duplicate chatter event ignoriert (TTL): {record_name}")
            else:
                message = KLAUSI_PROMPT_TEMPLATE.format(
                    author_id=author_id, body=text, record_name=record_name,
                    model=model, res_id=res_id,
                )
                log.info(f"Triggering agent for chatter mention on {record_name} "
                         f"by partner {author_id}")
                trigger_agent_async(message, f"klausi-chatter on {record_name}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 19001), WebhookHandler)
    log.info("Webhook handler v3 listening on :19001 "
             "(/odoo-task, /alertmanager-hook, /klausi-chatter) — "
             "ACK sofort, Dedupe aktiv, @Ollama-Route scharf")
    server.serve_forever()

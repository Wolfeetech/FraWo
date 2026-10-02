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

v3.1 (2026-09-30, Jarvis / Odoo #1581):
- Alarmmeldungen an Wolf sind laienverständlich und auf eine Abschlussmeldung
  begrenzt. Technische Diagnose bleibt intern.
- Ein Agentenlauf darf bis zu 15 Minuten dauern. Der alte äußere 180-s-Abbruch
  erzeugte Retries, obwohl der Lauf noch arbeitete, und damit Nachrichtenfluten.
- Alertmanager-Wiederholungen desselben Vorfalls werden anhand Fingerprint bzw.
  Startzeit dauerhaft dedupliziert; kein neues Ereignis an TTL-Grenzen.
- Alte Alarme laufen nach sechs Stunden bzw. zwei erfolglosen Agentenläufen
  nachvollziehbar als ``expired`` aus, statt unbegrenzt erneut zu feuern.
- Chatter-Ereignisse werden dauerhaft anhand der Odoo-``mail.message``-ID
  dedupliziert. Eine erneute Webhook-Zustellung erzeugt auch Stunden später
  keinen zweiten Agentenlauf.
- Chatter-Antworten bleiben im Odoo-Datensatz. Telegram bekommt genau eine
  knappe Abschlussnotiz, keine technischen Zwischenstände oder Dedupe-Berichte.
- Jeder Webhook-Vorfall läuft in einer eigenen Agentensitzung. Technische
  Ereignisse blähen Wolfs normale Telegram-Unterhaltung dadurch nicht mehr auf.
"""
import hashlib
import html as html_mod
import json
import logging
import os
import re
import sqlite3
import subprocess
import threading
import time
import urllib.error
import urllib.request
import xmlrpc.client
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from html.parser import HTMLParser

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

OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "240"))
AGENT_TIMEOUT = int(os.environ.get("FRAWO_AGENT_TIMEOUT", "900"))
ALERT_MAX_AGE = int(os.environ.get("FRAWO_ALERT_MAX_AGE", "21600"))
QUEUE_DB = os.environ.get(
    "FRAWO_QUEUE_DB", "/var/lib/frawo/odoo-webhook-queue.sqlite3")

# Getrennte Rollen statt eines stillen Fallbacks:
# - Routine-Lama (OptiPlex): 24/7, kurze Chatter-Zuarbeit.
# - Power-Lama (StudioPC): nur bei ausdrücklicher Bitte "Power"; dafür ist
#   ein stärkeres Modell und mehr Zeit vorgesehen. Fällt der StudioPC aus,
#   wird NICHT heimlich auf die Routine-Qualität zurückgefallen.
OLLAMA_ROUTINE_ZIELE = [(_need("OLLAMA_URL").rstrip("/"),
                         os.environ.get("OLLAMA_MODEL", "frawo-mitarbeiter-fast"))]
_power_url = os.environ.get("OLLAMA_POWER_URL", "").strip().rstrip("/")
_power_model = os.environ.get("OLLAMA_POWER_MODEL", "").strip()
OLLAMA_POWER_ZIELE = [(_power_url, _power_model)] if _power_url and _power_model else []

# Partner-ID des Odoo-Nutzers "🤖 Ollama Mitarbeiter" — eigene Beiträge dürfen
# niemals eine neue Runde auslösen.
OLLAMA_PARTNER_ID = int(os.environ.get("OLLAMA_PARTNER_ID", "160"))
OLLAMA_POWER_PARTNER_ID = int(os.environ.get("OLLAMA_POWER_PARTNER_ID", "0"))

# --- Dedupe ---------------------------------------------------------------
DEDUPE_TTL = {
    "alert": 21600,  # 6 h; persistent wird zusätzlich der Vorfall-Schlüssel genutzt
    "task": 600,     # 10 min: gleicher Odoo-Task nur 1x
    "chatter": 300,  # Fallback ohne message_id; normal dauerhaft persistent
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


# --- Persistente Agenten-Inbox ---------------------------------------------
# Ereignisse werden VOR dem HTTP-ACK atomar in SQLite (WAL + FULL) abgelegt.
# Der Worker ist Teil dieses Dienstes; kein Cron und kein weiterer Alarmkanal.
_queue_wake = threading.Event()


def _queue_connection():
    os.makedirs(os.path.dirname(QUEUE_DB), mode=0o700, exist_ok=True)
    conn = sqlite3.connect(QUEUE_DB, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    return conn


def init_queue():
    with _queue_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
              id TEXT PRIMARY KEY, kind TEXT NOT NULL, label TEXT NOT NULL,
              message TEXT NOT NULL, state TEXT NOT NULL,
              attempts INTEGER NOT NULL DEFAULT 0, created REAL NOT NULL,
              next_attempt REAL NOT NULL DEFAULT 0, delivered REAL,
              last_error TEXT
            )
        """)
        # Ein Neustart darf ein gerade laufendes Ereignis nicht verschwinden lassen.
        conn.execute("UPDATE events SET state='pending', next_attempt=0, "
                     "last_error='Worker nach Dienstneustart erneut eingeplant' "
                     "WHERE state='running'")


def enqueue_agent_event(kind: str, key: str, message: str, label: str) -> bool:
    """Speichert genau ein Ereignis pro Dedupe-Zeitfenster dauerhaft.

    True bedeutet neu gespeichert; False bedeutet bereits dauerhaft vorhanden.
    Eine Ausnahme muss zum HTTP-503 führen – ohne Persistenz kein ACK.
    """
    now = time.time()
    if kind in {"alert", "chatter"}:
        # Alertmanager-Fingerprint/Startzeit und Odoos mail.message-ID bleiben
        # stabil. Eine Zeitfenstergrenze darf daraus keinen neuen Agentenlauf
        # und keine neue Nachricht an Wolf machen.
        event_id = hashlib.sha256(f"{kind}:{key}".encode()).hexdigest()
    else:
        ttl = DEDUPE_TTL.get(kind, 600)
        bucket = int(now // ttl)
        event_id = hashlib.sha256(f"{kind}:{key}:{bucket}".encode()).hexdigest()
    with _queue_connection() as conn:
        cur = conn.execute(
            "INSERT OR IGNORE INTO events "
            "(id,kind,label,message,state,created,next_attempt) VALUES "
            "(?,?,?,?, 'pending', ?, 0)",
            (event_id, kind, label, message, now),
        )
        inserted = cur.rowcount == 1
    if inserted:
        _queue_wake.set()
        log.info("Persistente Inbox: %s gespeichert (%s)", label, event_id[:12])
    else:
        log.info("Persistente Inbox: Duplicate ignoriert (%s)", event_id[:12])
    return inserted

AGENT_PROMPT_TEMPLATE = """NEUER DEVOPS-TASK #{task_id} von Wolf:

**Titel:** {name}
**Beschreibung:** {description}

---
Deine Aufgabe als IT-Mitarbeiter (ServAssi):
1. Recherchiere das Problem/Ziel (nutze Odoo, HA, AzuraCast, SSH — was du brauchst)
2. Setze den Task auf Stage "In Recherche" (stage_id=3) in Odoo
3. Arbeite intern und schreibe Details in den Odoo-Chatter, nicht nach Telegram.
4. Schicke Wolf am Ende höchstens zwei kurze Sätze in Alltagssprache: worum es
   geht und genau welche Entscheidung nötig ist. Keine Fachbegriffe oder Liste.
5. WARTE auf Wolfs Antwort ("mach", "ja", "go" o.ä.)
6. Führe erst nach Freigabe aus
7. Melde Ergebnis + markiere Task als Erledigt (stage_id=6) nach Verifikation

SICHERHEITSREGEL: Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.
"""

ALERT_PROMPT_TEMPLATE = """SERVER-ALARM (von Alertmanager, automatisch, dedupliziert):

{alert_summary}

---
Deine Aufgabe als IT-Mitarbeiter (ServAssi):
1. Prüfe die tatsächliche Ursache direkt am betroffenen System. Nicht raten.
2. Arbeite intern und nutze alle sicheren, risikoarmen Möglichkeiten selbständig.
3. Schicke Wolf während der Prüfung KEINE technischen Zwischenstände und KEINE
   Wiederholungen. Nutze das Message-Tool erst für die eine Abschlussmeldung.
4. Schreibe ohne IT-Fachbegriffe, Abkürzungen, Messwerte, Befehle, IP-Adressen
   oder interne Queue-/Monitoring-Details, außer Wolf fragt ausdrücklich danach.
5. Die Abschlussmeldung hat genau dieses kurze Muster:

   **Problem:** Was ist für Wolf wahrnehmbar ausgefallen oder passiert?
   **Ursache:** Warum ist es passiert? Wenn noch unbekannt: ehrlich so sagen.
   **Automatisch getan:** Was wurde automatisch versucht oder behoben?
   **Ergebnis:** ✅ Behoben / ⏳ läuft noch / ❌ nicht automatisch lösbar
   **Du musst:** „Nichts.“ oder genau EINE konkrete Entscheidung/Handlung.

6. Frage Wolf nur, wenn du wirklich alle sicheren Möglichkeiten ausgeschöpft
   hast oder eine riskante Aktion (Produktivsystem, Löschen, Kernserver-Neustart)
   seine Entscheidung braucht. Keine Optionsliste, wenn eine klare Empfehlung
   möglich ist.
7. Wenn derselbe Vorfall schon bearbeitet wurde und live kein Fehler mehr aktiv
   ist, sende höchstens: „Keine neue Störung. Die verspätete Meldung wurde
   verworfen. Du musst nichts tun.“

SICHERHEITSREGEL: Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.
"""

KLAUSI_PROMPT_TEMPLATE = """ODOO-CHATTER — jemand hat dich erwähnt (Partner-ID {author_id}, bei Bedarf in Odoo nachschlagen):

**Wo:** {record_name} (Modell: {model}, ID: {res_id})
**Nachricht:** {body}

---
Deine Aufgabe als IT-Mitarbeiter (ServAssi):
1. Verstehe die Frage/das Anliegen
2. Recherchiere was nötig ist (Odoo, HA, AzuraCast, SSH — was du brauchst)
3. Antworte genau einmal DIREKT im Odoo-Chatter dieses Datensatzes
   (Modell {model}, ID {res_id}). Das ist der Hauptkanal.
4. Sende keine technischen Zwischenstände, Dedupe-Berichte, Memory-Diagnosen
   oder Wiederholungen an Wolf.
5. Bei größeren/riskanten Aktionen: schlage im Chatter kurz die empfohlene
   Vorgehensweise vor und warte dort auf Freigabe.
6. Telegram bekommt am Ende genau eine Notiz mit höchstens zwei kurzen Sätzen:
   worum es ging und ob Wolf etwas entscheiden muss. Keine Belegliste.

SICHERHEITSREGEL: Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.
"""


def _run_agent(message: str, label: str, event_id: str) -> bool:
    try:
        result = subprocess.run(
            [
                "docker", "exec", "openclaw",
                "openclaw", "agent",
                "--session-id", f"frawo-hook-{event_id[:16]}",
                "--message", message,
                "--channel", "telegram",
                "--to", TELEGRAM_ID,
                "--deliver",
                "--timeout", str(AGENT_TIMEOUT),
            ],
            timeout=AGENT_TIMEOUT + 30,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            log.info(f"Agent triggered successfully for {label}")
            return True
        log.error(f"Agent failed for {label}: {result.stderr[-500:]}")
        return False
    except subprocess.TimeoutExpired:
        # Ohne Rückgabecode ist die Zustellung nicht belegt. Das Ereignis
        # bleibt in der Inbox und wird mit Backoff erneut versucht.
        log.error(f"Agent-Trigger Timeout für {label}")
        return False
    except Exception as e:
        log.error(f"Error triggering agent for {label}: {e}")
        return False


def run_queue_once() -> bool:
    """Liefert höchstens ein fälliges Ereignis aus; Rückgabe = Arbeit getan."""
    now = time.time()
    with _queue_connection() as conn:
        # Chatter-IDs bleiben als dauerhaftes Zustellregister erhalten. Die
        # kleinen Datensätze verhindern auch nach Wochen eine Wiederholung.
        conn.execute(
            "DELETE FROM events WHERE state='delivered' AND kind != 'chatter' "
            "AND delivered < ?", (now - 7 * 86400,))
        row = conn.execute(
            "SELECT id,kind,label,message,attempts,created FROM events "
            "WHERE state='pending' AND next_attempt <= ? "
            "ORDER BY created LIMIT 1", (now,)).fetchone()
        if not row:
            return False
        event_id, kind, label, message, attempts, created = row
        if kind == "alert" and (now - created > ALERT_MAX_AGE or attempts >= 2):
            conn.execute(
                "UPDATE events SET state='expired', last_error=? WHERE id=?",
                ("Alarm ist veraltet oder nach zwei Versuchen nicht zustellbar",
                 event_id),
            )
            log.warning("Persistente Inbox: alter Alarm verworfen (%s)",
                        event_id[:12])
            return True
        conn.execute("UPDATE events SET state='running' WHERE id=?", (event_id,))

    ok = _run_agent(message, label, event_id)
    now = time.time()
    with _queue_connection() as conn:
        if ok:
            conn.execute("UPDATE events SET state='delivered', delivered=?, "
                         "last_error=NULL WHERE id=?", (now, event_id))
            log.info("Persistente Inbox: zugestellt (%s)", event_id[:12])
        else:
            attempts += 1
            delay = min(3600, 30 * (2 ** min(attempts - 1, 6)))
            conn.execute("UPDATE events SET state='pending', attempts=?, "
                         "next_attempt=?, last_error=? WHERE id=?",
                         (attempts, now + delay,
                          "Agent nicht angenommen; erneuter Versuch geplant", event_id))
            log.error("Persistente Inbox: Zustellung fehlgeschlagen (%s), "
                      "Retry in %ss", event_id[:12], delay)
    return True


def queue_worker() -> None:
    while True:
        try:
            did_work = run_queue_once()
        except Exception as e:
            log.exception("Persistente Inbox: Workerfehler: %s", e)
            did_work = False
        _queue_wake.wait(0.2 if did_work else 5)
        _queue_wake.clear()


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

Gib die Überschriften genau so aus, jeweils ohne Markdown-Zeichen und mit
Doppelpunkt, beispielsweise "Auftrag:". Keine #, keine Tabellen, keine
Codeblöcke.

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


def _is_power_mention(raw_body: str, partner_id: int) -> bool:
    if not partner_id:
        return False

    class PartnerMentionParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.found = False

        def handle_starttag(self, tag, attrs):
            attributes = dict(attrs)
            self.found = self.found or (
                tag == "a"
                and attributes.get("data-oe-model") == "res.partner"
                and attributes.get("data-oe-id") == str(partner_id)
            )

    parser = PartnerMentionParser()
    parser.feed(raw_body or "")
    return parser.found


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
        line = re.sub(r"^#{1,6}\s*", "", line.strip())
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
                parts.append("Beschreibung:\n%s" % desc[:1400])
    else:
        rows = rpc.call(model, "read", [[res_id]], {"fields": ["display_name"]})
        if rows:
            parts.append("Datensatz %s #%s: %s" % (
                model, res_id, rows[0].get("display_name") or ""))

    msgs = rpc.call("mail.message", "search_read", [[
        ["model", "=", model], ["res_id", "=", res_id],
        ["message_type", "in", ["comment", "email"]],
    ]], {"fields": ["date", "author_id", "body"], "limit": 4,
         "order": "date desc"})
    if msgs:
        lines = []
        for m in reversed(msgs):
            who = (m.get("author_id") or [0, "System"])[1]
            body = _strip_html(m.get("body") or "")[:450]
            if body:
                lines.append("[%s] %s: %s" % (m.get("date"), who, body))
        if lines:
            parts.append("Bisheriger Verlauf (älteste zuerst):\n" + "\n".join(lines))
    return "\n\n".join(parts)


class KeinRechenknoten(Exception):
    """Kein einziger Ollama-Knoten hat geantwortet."""


def _erreichbar(url: str) -> bool:
    """Kurzer Klopftest, damit ein abgeschalteter Rechner die Antwort nicht
    erst nach dem vollen Zeitlimit scheitern lässt."""
    try:
        with urllib.request.urlopen(url + "/api/tags", timeout=4) as resp:
            return resp.status == 200
    except Exception:
        return False


def _ask_ollama(system: str, prompt: str, power: bool = False):
    """Fragt die gewählte Rolle. Gibt (Antwort, Modellname) zurück."""
    versucht = []
    ziele = OLLAMA_POWER_ZIELE if power else OLLAMA_ROUTINE_ZIELE
    rolle = "Power-Lama" if power else "Routine-Lama"
    if not ziele:
        raise KeinRechenknoten(f"{rolle} ist nicht konfiguriert")
    for url, model in ziele:
        if not _erreichbar(url):
            versucht.append(f"{url} (aus)")
            continue
        payload = json.dumps({
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            "options": {"temperature": 0.2, "num_predict": 700},
        }).encode("utf-8")
        req = urllib.request.Request(
            f"{url}/api/chat", data=payload,
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return (data.get("message") or {}).get("content", "").strip(), model
    raise KeinRechenknoten(", ".join(versucht) or f"{rolle} nicht erreichbar")


def _post(rpc: OdooRPC, model: str, res_id: int, body_html: str, note: bool = True):
    rpc.call(model, "message_post", [res_id], {
        "body": body_html,
        "message_type": "comment",
        "subtype_xmlid": "mail.mt_note" if note else "mail.mt_comment",
    })


def handle_ollama_async(model: str, res_id: int, record_name: str,
                        question: str, author_id: int, power: bool = False) -> None:
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
            answer, used_model = _ask_ollama(OLLAMA_SYSTEM, prompt, power=power)
        except (KeinRechenknoten, urllib.error.URLError, OSError) as e:
            log.warning(f"Kein Ollama-Knoten erreichbar für {label}: {e}")
            try:
                _post(rpc, model, res_id,
                      "<p>🤖 <b>Ollama Mitarbeiter</b> konnte nicht antworten: " +
                      ("Power-Lama (StudioPC)" if power else "Routine-Lama (OptiPlex)") +
                      " ist gerade nicht erreichbar. Die Frage bleibt offen — "
                      "bitte später erneut erwähnen.</p>", note=True)
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
                 'kein Abschluss.</p>' % used_model)
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
    parts = []
    for alert in payload.get("alerts", []):
        labels = alert.get("labels", {})
        incident = alert.get("fingerprint") or (
            f"{labels.get('alertname', '?')}@{labels.get('instance', '?')}"
        )
        # startsAt trennt einen späteren neuen Vorfall vom heutigen Vorfall.
        parts.append(f"{incident}@{alert.get('startsAt', '?')}")
    parts.sort()
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
        name = data.get("name", "Unbekannter Task")
        description = data.get("description", "Keine Beschreibung")
        description_clean = description[:800] if description else ""

        message = AGENT_PROMPT_TEMPLATE.format(
            task_id=task_id, name=name, description=description_clean,
        )
        try:
            inserted = enqueue_agent_event("task", str(task_id), message,
                                           f"task #{task_id}")
        except Exception as e:
            log.exception("Task konnte nicht persistent eingereiht werden: %s", e)
            self.send_response(503)
            self.end_headers()
            return
        self._respond(200, dedup=not inserted)

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
        summary = format_alerts(data)
        message = ALERT_PROMPT_TEMPLATE.format(alert_summary=summary)
        try:
            inserted = enqueue_agent_event("alert", key, message, "alertmanager")
        except Exception as e:
            log.exception("Alarm konnte nicht persistent eingereiht werden: %s", e)
            self.send_response(503)
            self.end_headers()
            return
        self._respond(200, dedup=not inserted)

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
        # Bei Odoos Webhook auf mail.message ist `_id` die stabile ID der
        # auslösenden Chatter-Nachricht. `message_id` erlaubt denselben Vertrag
        # für gezielte Tests oder spätere Odoo-Payloads.
        message_id = data.get("message_id") or data.get("_id")

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

        if message_id:
            key = f"mail.message:{message_id}"
        else:
            # Rückwärtskompatibler Fallback für Payloads ohne Nachrichten-ID.
            key = hashlib.sha256(
                f"{model}:{res_id}:{author_id}:{raw_body}".encode()
            ).hexdigest()[:16]

        agent_inserted = None
        agent_message = None
        if want_agent:
            agent_message = KLAUSI_PROMPT_TEMPLATE.format(
                author_id=author_id, body=text, record_name=record_name,
                model=model, res_id=res_id,
            )
            try:
                agent_inserted = enqueue_agent_event(
                    "chatter", key, agent_message,
                    f"klausi-chatter on {record_name}")
            except Exception as e:
                log.exception("Chatter konnte nicht persistent eingereiht werden: %s", e)
                self.send_response(503)
                self.end_headers()
                return

        self._respond(200, dedup=(want_agent and not agent_inserted))

        if want_ollama and res_id:
            if is_duplicate("ollama", key):
                log.info(f"Duplicate @Ollama-Erwähnung ignoriert (TTL): {record_name}")
            else:
                log.info(f"Ollama-Lauf für {model}#{res_id} ({record_name})")
                power = _is_power_mention(raw_body, OLLAMA_POWER_PARTNER_ID)
                handle_ollama_async(
                    model, res_id, record_name, text, author_id, power=power)



if __name__ == "__main__":
    init_queue()
    threading.Thread(target=queue_worker, daemon=True,
                     name="persistente-agent-inbox").start()
    server = ThreadingHTTPServer(("0.0.0.0", 19001), WebhookHandler)
    log.info("Webhook handler v3 listening on :19001 "
             "(/odoo-task, /alertmanager-hook, /klausi-chatter) — "
             "ACK sofort, Dedupe aktiv, @Ollama-Route scharf")
    server.serve_forever()

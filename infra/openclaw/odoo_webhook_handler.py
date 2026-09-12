#!/usr/bin/env python3
"""
FraWo Webhook Handler — v2 (2026-09-06, Jarvis)
Läuft auf CT150, Port 19001 (LAN-only)
- /odoo-task: Odoo → triggert ServAssi bei neuen DevOps-Aufgaben
- /alertmanager-hook: Prometheus Alertmanager → triggert ServAssi bei Server-Alarmen
- /klausi-chatter: Odoo → triggert ServAssi bei @Klausi/@Jarvis im Chatter

v2-Änderungen (Fix für Alarm-Spam vom 2026-09-06):
- HTTP-Antwort (200 ACK) kommt SOFORT, Agent-Trigger läuft asynchron im Thread.
  (Vorher: Handler blockierte bis 60s → Alertmanager-Timeout (~10s) → Retry-Loop
   → 5x derselbe Alarm + kollidierende Agent-Sessions.)
- Dedupe: gleicher Alert/Task/Chatter-Event innerhalb TTL wird ignoriert.
- Trigger-Serialisierung: nur EIN openclaw-agent-Aufruf gleichzeitig (Lock),
  verhindert "assistant turn failed" durch parallele Turns in Session main.
- ThreadingHTTPServer statt Single-Thread-Server.
"""
import hashlib
import json
import subprocess
import logging
import threading
import time
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("odoo-webhook")

TELEGRAM_ID = "5924907152"
SECRET = "frawo-odoo-webhook-2026"
ALERT_SECRET = "frawo-alertmanager-webhook-2026"
KLAUSI_SECRET = "frawo-klausi-chatter-2026"

# --- Dedupe ---------------------------------------------------------------
DEDUPE_TTL = {
    "alert": 1800,   # 30 min: gleicher Alarm (alertname@instance) nur 1x
    "task": 600,     # 10 min: gleicher Odoo-Task nur 1x
    "chatter": 300,  # 5 min: gleiche Chatter-Message nur 1x
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

        # Odoo-natives Webhook-Format: _model/_id statt model/res_id
        body = (data.get("body") or "")[:1500]
        author_id = data.get("author_id", "?")
        record_name = data.get("record_name", "unbekannter Datensatz")
        model = data.get("_model") or data.get("model", "?")
        res_id = data.get("_id") or data.get("res_id", "?")

        chatter_key = hashlib.sha256(
            f"{model}:{res_id}:{author_id}:{body}".encode()
        ).hexdigest()[:16]
        if is_duplicate("chatter", chatter_key):
            log.info(f"Duplicate chatter event ignoriert (TTL): {record_name}")
            self._respond(200, dedup=True)
            return

        message = KLAUSI_PROMPT_TEMPLATE.format(
            author_id=author_id, body=body, record_name=record_name,
            model=model, res_id=res_id,
        )
        log.info(f"Triggering agent for chatter mention on {record_name} by partner {author_id}")
        self._respond(200)
        trigger_agent_async(message, f"klausi-chatter on {record_name}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", 19001), WebhookHandler)
    log.info("Webhook handler v2 listening on :19001 (/odoo-task, /alertmanager-hook, /klausi-chatter) — ACK sofort, Dedupe aktiv")
    server.serve_forever()

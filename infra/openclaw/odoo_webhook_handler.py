#!/usr/bin/env python3
"""
Odoo → ServAssi Webhook Handler
Läuft auf CT150, Port 19001 (LAN-only)
Empfängt Task-Events von Odoo und triggert openclaw agent
"""
import json
import subprocess
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("odoo-webhook")

TELEGRAM_ID = "5924907152"
SECRET = "frawo-odoo-webhook-2026"

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


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        log.info(fmt % args)

    def do_POST(self):
        if self.path != "/odoo-task":
            self.send_response(404)
            self.end_headers()
            return

        auth = self.headers.get("X-Webhook-Secret", "")
        if auth != SECRET:
            log.warning("Unauthorized webhook attempt")
            self.send_response(401)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
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
            task_id=task_id,
            name=name,
            description=description_clean,
        )

        log.info(f"Triggering agent for task #{task_id}: {name}")

        try:
            result = subprocess.run(
                [
                    "docker", "exec", "openclaw",
                    "openclaw", "agent",
                    "--session", "main",
                    "--message", message,
                    "--channel", "telegram",
                    "--to", TELEGRAM_ID,
                    "--deliver",
                ],
                timeout=60,
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                log.info(f"Agent triggered successfully for task #{task_id}")
                self.send_response(200)
            else:
                log.error(f"Agent failed: {result.stderr}")
                self.send_response(500)
        except subprocess.TimeoutExpired:
            log.info(f"Agent started (timeout OK — runs async) for task #{task_id}")
            self.send_response(200)
        except Exception as e:
            log.error(f"Error triggering agent: {e}")
            self.send_response(500)

        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok": true}')


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 19001), WebhookHandler)
    log.info("Odoo webhook handler listening on :19001")
    server.serve_forever()

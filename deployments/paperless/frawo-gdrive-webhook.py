#!/usr/bin/env python3
"""
Nimmt Google-Drive-Push-Benachrichtigungen entgegen ("irgendetwas hat sich
geändert") und stößt sofort den Abholvorgang aus 00_INBOX/_Dokumente-
zur-Pruefung an — kein Zeittakt, echtes "der Postbote klingelt".

Läuft als systemd-Dienst dauerhaft auf stock-pve, Port 8001. Erreichbar
von aussen nur über den Cloudflare-Tunnel (proxmox-anker) unter
paperless-hook.frawo-tech.de. Siehe OPERATIONS/PAPERLESS_OPERATIONS.md.
"""
import http.server
import os
import subprocess
import sys
import threading
import time

SHARED_SECRET = os.environ.get("GDRIVE_WEBHOOK_SECRET", "")
PULL_SCRIPT = "/usr/local/bin/frawo-gdrive-inbox-pull.sh"
LOG = "/var/log/frawo-gdrive-webhook.log"

if not SHARED_SECRET:
    print("GDRIVE_WEBHOOK_SECRET nicht gesetzt.", file=sys.stderr)
    sys.exit(1)

_lock = threading.Lock()


def log(msg):
    with open(LOG, "a") as f:
        f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%S')} {msg}\n")


def run_pull():
    with _lock:
        try:
            result = subprocess.run([PULL_SCRIPT], capture_output=True, text=True, timeout=120)
            log(f"pull ausgeführt, exit={result.returncode} stderr={result.stderr[:300]}")
        except Exception as e:
            log(f"pull fehlgeschlagen: {e}")


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # eigenes Logging statt Konsolen-Spam

    def do_POST(self):
        token = self.headers.get("X-Goog-Channel-Token", "")
        state = self.headers.get("X-Goog-Resource-State", "")
        # Google schickt beim Anlegen des Kanals einmalig state=sync — ignorieren.
        self.send_response(200)
        self.end_headers()
        if token != SHARED_SECRET:
            log(f"abgelehnt: falscher Token (state={state})")
            return
        if state == "sync":
            log("sync-Bestätigung erhalten (Kanal aktiv)")
            return
        log(f"Benachrichtigung erhalten (state={state}) — starte Abholung")
        threading.Thread(target=run_pull, daemon=True).start()

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")


if __name__ == "__main__":
    # 0.0.0.0, weil cloudflared auf proxmox-anker über das LAN zugreift.
    # Zugriff per Host-Firewall auf anker-pve (10.1.0.92) beschränkt.
    server = http.server.ThreadingHTTPServer(("0.0.0.0", 8001), Handler)
    log("Webhook-Empfaenger gestartet auf Port 8001")
    server.serve_forever()

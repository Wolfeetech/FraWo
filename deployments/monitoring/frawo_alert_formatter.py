#!/usr/bin/env python3
"""
FraWo Alert Formatter — Verständliche 4-Zeilen-Alarme (Odoo Task #1541)
Alertmanager → frawo_alert_formatter → Ollama (Formulierung) → Telegram
                                     ↳ Fallback (Deterministisch)

Architektur:
- Alertmanager sendet Webhook an localhost:9087/alert.
- Jede kritische Meldung enthält deterministische Fakten (Summary, Description,
  Heißt, Zu tun, Vor Ort).
- Skript versucht Ollama (Primär: OptiPlex, Fallback: StudioPC) zur lesefreundlichen
  Formulierung im standardisierten 4-Zeilen-Format abzufragen (Timeout 6s).
- Fällt Ollama aus oder antwortet nicht regelkonform, wird SOFORT die deterministische
  Rohfassung versendet. Ein Alarm wird NIEMALS verschluckt!
- Telegram-Versand erfolgt direkt an Wolfs Chat-ID.
"""

import json
import logging
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger("frawo-alert-formatter")

# --- Konfiguration aus Umgebungsvariablen ------------------------------------
LISTEN_HOST = os.environ.get("ALERT_FORMATTER_HOST", "127.0.0.1")
LISTEN_PORT = int(os.environ.get("ALERT_FORMATTER_PORT", "9087"))

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "5924907152").strip()

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://10.1.0.227:11434").rstrip("/")
OLLAMA_FALLBACK_URL = os.environ.get("OLLAMA_FALLBACK_URL", "http://10.0.0.156:11434").rstrip("/")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "frawo-mitarbeiter-fast:latest")
OLLAMA_TIMEOUT = float(os.environ.get("OLLAMA_TIMEOUT", "6.0"))


def build_raw_message(alert: dict) -> str:
    """Erzeugt die deterministische 4-Zeilen-Meldung direkt aus den Prometheus-Annotations."""
    status = alert.get("status", "firing")
    ann = alert.get("annotations", {})
    labels = alert.get("labels", {})

    alertname = labels.get("alertname", "Server-Alarm")
    summary = ann.get("summary", alertname)
    desc = ann.get("description", "Keine Detailbeschreibung verfügbar.")
    heisst = ann.get("heisst", "Dienst oder Funktion beeinträchtigt.")
    zu_tun = ann.get("zu_tun", "Nichts sofort.")
    vor_ort = ann.get("vor_ort", "nein")
    dashboard = ann.get("dashboard", "")

    if status == "resolved":
        msg = f"✅ BEHOBEN: {summary}\n{desc}"
    else:
        # Standard-Präfix falls noch kein Emoji im Summary ist
        prefix = "" if any(summary.startswith(e) for e in ["🚨", "🔴", "📻", "⚠️", "⚡", "💾"]) else "🚨 "
        msg = (
            f"{prefix}{summary}\n"
            f"{desc}\n"
            f"Heißt:       {heisst}\n"
            f"Zu tun:      {zu_tun}\n"
            f"Vor Ort:     {vor_ort}"
        )

    if dashboard and status != "resolved":
        msg += f"\n\n📊 Live ansehen: {dashboard}"

    return msg


def query_ollama(url: str, prompt: str) -> str:
    """Ruft Ollama synchron mit kurzem Timeout auf."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 350
        }
    }
    req = urllib.request.Request(
        f"{url}/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
        if resp.status == 200:
            res_data = json.loads(resp.read().decode("utf-8"))
            return res_data.get("response", "").strip()
    return ""


def formulate_with_ollama(alert: dict) -> str | None:
    """Lässt Ollama die Meldung sprachlich glätten; gibt None bei Fehler zurück."""
    status = alert.get("status", "firing")
    if status == "resolved":
        return None  # Resolved-Meldungen bleiben direkt deterministisch und schnell

    ann = alert.get("annotations", {})
    labels = alert.get("labels", {})

    alertname = labels.get("alertname", "Server-Alarm")
    summary = ann.get("summary", alertname)
    desc = ann.get("description", "")
    heisst = ann.get("heisst", "Dienst oder Funktion beeinträchtigt.")
    zu_tun = ann.get("zu_tun", "Nichts sofort.")
    vor_ort = ann.get("vor_ort", "nein")

    prompt = (
        "Du bist IT-Mitarbeiter für Wolf bei FraWo. "
        "Formuliere den folgenden Server-Alarm für Wolfs Telegram in genau 4 Zeilen zusammen. "
        "Halte dich strikt an diese Zeilen:\n\n"
        "<Emoji> <Kurztitel>\n"
        "<Was passiert ist in 1 Satz>\n"
        "Heißt:       <Konsequenz im Klartext>\n"
        "Zu tun:      <Erster Handgriff oder 'Nichts sofort.'>\n"
        "Vor Ort:     <ja/nein>\n\n"
        f"Fakten:\n"
        f"- Titel: {summary}\n"
        f"- Was ist passiert: {desc}\n"
        f"- Heißt: {heisst}\n"
        f"- Zu tun: {zu_tun}\n"
        f"- Vor Ort: {vor_ort}\n\n"
        "Gib NUR das 4-Zeilen-Muster aus. Keine Einleitung, keine Begrüßung."
    )

    # Versuch über verfügbare Ollama-Instanzen
    for target in [OLLAMA_URL, OLLAMA_FALLBACK_URL]:
        if not target:
            continue
        try:
            t0 = time.time()
            text = query_ollama(target, prompt)
            elapsed = time.time() - t0
            # Validierung: Enthält alle Pflichtbestandteile?
            low = text.lower()
            if ("heißt:" in low or "heisst:" in low) and "zu tun:" in low and "vor ort:" in low:
                log.info("Ollama (%s) formulierte Meldung in %.2fs", target, elapsed)
                dashboard = ann.get("dashboard", "")
                if dashboard:
                    text += f"\n\n📊 Live ansehen: {dashboard}"
                return text
            else:
                log.warning("Ollama (%s) lieferte unvollständiges Format: %s", target, repr(text[:120]))
        except Exception as e:
            log.warning("Ollama (%s) nicht erreichbar oder Timeout: %s", target, e)

    return None


def send_telegram(text: str) -> bool:
    """Sendet Nachricht per Telegram Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        log.error("Telegram-Token oder Chat-ID nicht konfiguriert!")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "disable_web_page_preview": True
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )

    for attempt in range(1, 3):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    log.info("Telegram-Alarm erfolgreich zugestellt an %s", TELEGRAM_CHAT_ID)
                    return True
        except Exception as e:
            log.error("Telegram Sendeversuch %d fehlgeschlagen: %s", attempt, e)
            time.sleep(1)

    return False


def process_alertmanager_payload(data: dict):
    """Verarbeitet eingehende Alertmanager-Meldungen."""
    alerts = data.get("alerts", [])
    log.info("Verarbeite %d Alarm(e) von Alertmanager", len(alerts))

    for alert in alerts:
        # 1. Versuche Ollama Formulierung
        formatted = formulate_with_ollama(alert)
        if not formatted:
            # 2. Fallback: Deterministische Rohmeldung (Garantie: kein Alarm geht verloren)
            formatted = build_raw_message(alert)
            log.info("Verwende deterministische Rohmeldung für %s", alert.get("labels", {}).get("alertname"))

        send_telegram(formatted)


class AlertHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/alert":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len)
            try:
                data = json.loads(post_body.decode("utf-8"))
                process_alertmanager_payload(data)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                log.error("Fehler beim Verarbeiten des Alertmanager-Payloads: %s", e)
                self.send_response(500)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Ruhiges Logging über unser Logging-Framework statt stderr
        pass


def main():
    log.info("Starte FraWo Alert Formatter auf %s:%d", LISTEN_HOST, LISTEN_PORT)
    server = HTTPServer((LISTEN_HOST, LISTEN_PORT), AlertHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        log.info("FraWo Alert Formatter beendet.")


if __name__ == "__main__":
    main()

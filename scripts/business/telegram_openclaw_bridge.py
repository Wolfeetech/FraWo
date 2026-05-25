#!/usr/bin/env python3
import os
import sys
import json
import time
import urllib.request
import urllib.parse
import logging
import traceback
import re

# Configuration and Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "telegram_config.json")
OPENCLAW_URL = os.environ.get("OPENCLAW_URL", "http://127.0.0.1:5555/api/chat")

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(BASE_DIR, "telegram_bridge.log"), encoding='utf-8')
    ]
)
logger = logging.getLogger("TelegramBridge")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        logger.error(f"Konfigurationsdatei nicht gefunden: {CONFIG_PATH}")
        return None
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden von telegram_config.json: {e}")
        return None

def call_telegram_api(token, method, payload=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = None
    headers = {}
    if payload:
        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="POST" if payload else "GET")
        with urllib.request.urlopen(req, timeout=40) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        # Avoid logging raw token in stack trace if it is in the exception URL
        err_msg = str(e).replace(token, "SECRET_TOKEN")
        raise RuntimeError(f"Telegram API Fehler ({method}): {err_msg}")

def main():
    logger.info("Starte Telegram-zu-OpenClaw Bridge...")
    
    config = load_config()
    if not config:
        logger.error("Bridge kann ohne Konfiguration nicht gestartet werden. Beende.")
        sys.exit(1)
        
    token = config.get("telegram_bot_token", "").strip()
    if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
        logger.warning("=" * 60)
        logger.warning("HINWEIS: Bitte trage deinen echten Telegram Bot Token in")
        logger.warning(f"  {CONFIG_PATH}")
        logger.warning("ein, damit die Bridge die Verbindung aufbauen kann.")
        logger.warning("=" * 60)
    
    authorized_chat_ids = set(config.get("authorized_chat_ids", []))
    logger.info(f"Autorisierte Chat-IDs geladen: {list(authorized_chat_ids)}")
    
    offset = 0
    consecutive_errors = 0
    
    while True:
        # Reload config in every loop so changes in whitelist/token take effect dynamically
        new_config = load_config()
        if new_config:
            config = new_config
            token = config.get("telegram_bot_token", "").strip()
            authorized_chat_ids = set(config.get("authorized_chat_ids", []))
            
        if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.debug("Warte auf Konfiguration des Telegram Bot Tokens...")
            time.sleep(10)
            continue
            
        try:
            # Poll for updates
            payload = {
                "offset": offset,
                "timeout": 30,
                "limit": 10
            }
            
            updates_resp = call_telegram_api(token, "getUpdates", payload)
            consecutive_errors = 0  # Reset error counter on success
            
            if not updates_resp.get("ok"):
                logger.error(f"Fehlerhafte getUpdates Antwort: {updates_resp}")
                time.sleep(5)
                continue
                
            updates = updates_resp.get("result", [])
            for update in updates:
                update_id = update.get("update_id")
                offset = update_id + 1
                
                message = update.get("message")
                if not message:
                    continue
                    
                chat = message.get("chat", {})
                chat_id = chat.get("id")
                text = message.get("text", "").strip()
                
                if not chat_id or not text:
                    continue
                    
                from_user = message.get("from", {})
                username = from_user.get("username", "Unknown")
                first_name = from_user.get("first_name", "")
                
                logger.info(f"Nachricht empfangen von {first_name} (@{username}) [ID: {chat_id}]: {text[:100]}...")
                
                # Check authorization
                # Note: if authorized_chat_ids is empty, we block all except the rejection logic,
                # which tells the user their chat_id so they can add it.
                if chat_id not in authorized_chat_ids:
                    logger.warning(f"Unbefugter Zugriff von {first_name} (@{username}) [ID: {chat_id}] blockiert!")
                    
                    reject_text = (
                        f"❌ <b>Zugriff verweigert</b>\n\n"
                        f"Dieser OpenClaw-Bot ist privat und reagiert nur auf autorisierte Benutzer.\n\n"
                        f"<b>Deine Telegram Chat-ID:</b> <code>{chat_id}</code>\n\n"
                        f"Bitte füge diese ID in deine <code>telegram_config.json</code> unter "
                        f"<code>authorized_chat_ids</code> hinzu, um diesen Bot freizuschalten."
                    )
                    try:
                        call_telegram_api(token, "sendMessage", {
                            "chat_id": chat_id,
                            "text": reject_text,
                            "parse_mode": "HTML"
                        })
                    except Exception as e:
                        logger.error(f"Fehler beim Senden der Ablehnung: {e}")
                    continue
                
                # Handle start command
                if text.lower() == "/start":
                    welcome_text = (
                        f"🤖 <b>FraWo OpenClaw Lead-Agent ist online!</b>\n\n"
                        f"Hallo {first_name}, ich bin bereit für deine Befehle.\n"
                        f"Ich kann System-Audits durchführen, Container steuern und Skripte verwalten.\n\n"
                        f"Schreibe mir einfach eine ganz normale Nachricht."
                    )
                    try:
                        call_telegram_api(token, "sendMessage", {
                            "chat_id": chat_id,
                            "text": welcome_text,
                            "parse_mode": "HTML"
                        })
                    except Exception as e:
                        logger.error(f"Fehler beim Senden von /start: {e}")
                    continue
                
                # Send typing action
                try:
                    call_telegram_api(token, "sendChatAction", {
                        "chat_id": chat_id,
                        "action": "typing"
                    })
                except Exception as e:
                    logger.error(f"Fehler beim Senden der Schreib-Aktion: {e}")
                
                # Forward to OpenClaw
                logger.info(f"Leite Nachricht an OpenClaw weiter ({OPENCLAW_URL})...")
                ai_reply = ""
                try:
                    openclaw_payload = {"message": text}
                    req = urllib.request.Request(
                        OPENCLAW_URL,
                        data=json.dumps(openclaw_payload).encode("utf-8"),
                        headers={"Content-Type": "application/json"}
                    )
                    with urllib.request.urlopen(req, timeout=360) as response:
                        resp_data = json.loads(response.read().decode("utf-8"))
                        ai_reply = resp_data.get("response", "")
                except Exception as e:
                    logger.error(f"Fehler bei OpenClaw Verbindung: {e}")
                    ai_reply = f"⚠️ Fehler bei der Verbindung zum OpenClaw-Agenten: {e}"
                
                if not ai_reply:
                    ai_reply = "⚠️ Keine Antwort vom Agenten erhalten."
                
                # Format and send reply back to Telegram
                logger.info(f"Sende Antwort an {first_name} [ID: {chat_id}]...")
                try:
                    formatted_reply = ai_reply
                    # Convert basic markdown elements to HTML for clean rendering
                    formatted_reply = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", formatted_reply)
                    formatted_reply = re.sub(r"`(.*?)`", r"<code>\1</code>", formatted_reply)
                    
                    call_telegram_api(token, "sendMessage", {
                        "chat_id": chat_id,
                        "text": formatted_reply,
                        "parse_mode": "HTML"
                    })
                except Exception as e:
                    logger.error(f"Fehler beim Senden der HTML-Antwort: {e}")
                    try:
                        call_telegram_api(token, "sendMessage", {
                            "chat_id": chat_id,
                            "text": ai_reply
                        })
                    except Exception as ex:
                        logger.error(f"Fallback-Antwort fehlgeschlagen: {ex}")
            
        except Exception as e:
            consecutive_errors += 1
            logger.error(f"Fehler im Telegram Poll-Loop (Fehler {consecutive_errors}): {e}")
            sleep_time = min(60, 2 ** consecutive_errors)
            logger.info(f"Warte {sleep_time} Sekunden vor dem nächsten Versuch...")
            time.sleep(sleep_time)
            
        time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Bridge vom Benutzer beendet.")
        sys.exit(0)

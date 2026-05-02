#!/usr/bin/env python3
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Configuration
PORT = 5555
OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "frawo-pro:latest"

import logging
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("openclaw_server.log")
    ]
)
logger = logging.getLogger("OpenClawAPI")

import subprocess
import time

# --- Skill Catalog ---
SKILLS = {
    "health_audit": {
        "cmd": ["python", "scripts/platform_health_audit.py"],
        "desc": "Führt einen kompletten System-Audit durch (Netzwerk, Dienste, PBS)."
    },
    "fix_network": {
        "cmd": ["powershell", "-ExecutionPolicy", "Bypass", "-File", "scripts/fix_network_metrics.ps1"],
        "desc": "Repariert gängige Netzwerk-Metrik-Probleme auf dem StudioPC."
    },
    "sync_tasks": {
        "cmd": ["python", "scripts/sync_lane_c_to_odoo.py"],
        "desc": "Synchronisiert Lane-C Aufgaben (Security/PBS) mit dem Odoo Backend."
    },
    "kiosk_check": {
        "cmd": ["python", "scripts/control_surface_actions_check.py"],
        "desc": "Überprüft die Funktionalität des Surface Go Portals."
    },
    "refresh_context": {
        "cmd": ["bash", "scripts/refresh_live_context.sh"],
        "desc": "Aktualisiert den KI-Kontext durch Einlesen der neuesten Logs und Status."
    }
}

AGENT_SYSTEM_PROMPT = """
ZUSÄTZLICHE FÄHIGKEITEN:
Du hast Zugriff auf operative 'Skills' (Skripte). Um ein Problem zu lösen, kannst du ein Skript aufrufen.
Format für Skill-Aufruf: [RUN: skill_name]

Verfügbare Skills:
- health_audit: Systemweiter Check.
- fix_network: Netzwerk-Reparatur.
- sync_tasks: Odoo Task-Synchronisation.
- kiosk_check: Portal-Validierung.
- refresh_context: Kontext-Update.

WENN du einen Skill aufrufst, wird das Ergebnis automatisch in die Konversation eingefügt. 
Antworte erst mit dem Aufruf und warte auf das Ergebnis, bevor du die finale Lösung präsentierst.
"""

class OpenClawAPIHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        logger.info("%s - - %s" % (self.address_string(), format % args))

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, HEAD')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "online",
                "model": OLLAMA_MODEL,
                "backend": "ollama",
                "agent_version": "3.1-agentic",
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        content_length = int(self.headers.get('Content-Length', 0))
        
        try:
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body) if body else {}
        except Exception as e:
            logger.error(f"Error decoding request body: {e}")
            self.send_error(400, f"Invalid JSON or encoding: {e}")
            return

        if parsed.path == "/api/chat":
            self.handle_chat(data)
        else:
            self.send_error(404)

    def call_ollama(self, prompt, system_extension=""):
        full_system = f"{AGENT_SYSTEM_PROMPT}\n{system_extension}"
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "system": full_system,
            "stream": False
        }
        
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read().decode())

    def handle_chat(self, data):
        message = data.get("message", "")
        logger.info(f"Agent Request: {message[:100]}...")
        
        try:
            import urllib.request
            
            # --- Turn 1: Thought & Potential Action ---
            resp_data = self.call_ollama(message)
            ai_response = resp_data.get('response', '')
            
            # Check for [RUN: skill_name]
            import re
            match = re.search(r"\[RUN:\s*(\w+)\]", ai_response)
            
            if match:
                skill_name = match.group(1)
                logger.info(f"Agent requested skill: {skill_name}")
                
                if skill_name in SKILLS:
                    skill = SKILLS[skill_name]
                    try:
                        logger.info(f"Executing: {skill['cmd']}")
                        result = subprocess.run(
                            skill['cmd'], 
                            capture_output=True, 
                            text=True, 
                            timeout=60,
                            cwd="c:\\WORKSPACE\\FraWo" # Explicit CWD
                        )
                        output = f"Result of {skill_name}:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                    except Exception as e:
                        output = f"Error executing {skill_name}: {str(e)}"
                    
                    logger.info(f"Skill result: {output[:100]}...")
                    
                    # --- Turn 2: Final Answer with Result ---
                    final_prompt = f"{message}\n\n[SYSTEM: {output}]"
                    final_resp_data = self.call_ollama(final_prompt, system_extension="Integriere das Ergebnis des Skills in deine finale Antwort.")
                    ai_response = final_resp_data.get('response', '⚠️ Fehler bei der Finalisierung.')
                else:
                    ai_response += f"\n\n(Hinweis: Skill '{skill_name}' ist nicht im Katalog registriert.)"
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": ai_response,
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Error in agent chat: {e}\n{error_details}")
            
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "response": f"⚠️ OpenClaw Agent Fehler: {str(e)}",
                "details": error_details if "--debug" in sys.argv else None,
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())

def run():
    logger.info(f"Starting OpenClaw AGENT on port {PORT} (Ollama: {OLLAMA_MODEL})...")
    try:
        server = HTTPServer(('0.0.0.0', PORT), OpenClawAPIHandler)
        server.serve_forever()
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()



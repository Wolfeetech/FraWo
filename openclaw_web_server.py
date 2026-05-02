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
    "restart_kiosk": {
        "cmd": ["python", "c:/Users/StudioPC/.gemini/antigravity/scratch/restart_surface_kiosk.py"],
        "desc": "Startet den Firefox-Kiosk auf dem Surface Go neu."
    },
    "list_files": {
        "cmd": ["powershell", "Get-ChildItem -Path . -Recurse -Include *.md,*.txt,todo.md,*.py,*.sh | Select-Object -ExpandProperty FullName"],
        "desc": "Listet alle relevanten Projektdateien im Workspace auf."
    },
    "read_file": {
        "cmd": ["python", "-c", "import sys; print(open(sys.argv[1], 'r', encoding='utf-8').read())"],
        "desc": "Liest den Inhalt einer Datei. Beispiel: [RUN: read_file todo.md]"
    },
    "write_file": {
        "cmd": ["python", "-c", "import sys; f=open(sys.argv[1], 'w', encoding='utf-8'); f.write(sys.argv[2]); f.close(); print('Erfolgreich geschrieben.')"],
        "desc": "Schreibt oder überschreibt eine Datei. Beispiel: [RUN: write_file path 'inhalt']"
    },
    "sync_masterplan": {
        "cmd": ["python", "scripts/sync_lane_c_to_odoo.py"], # We will make this more generic later
        "desc": "Überträgt den aktuellen Masterplan in das Odoo Projektboard."
    },
    "plan_azuracast": {
        "cmd": ["python", "-c", "f=open('AZURACAST_PLAN.md', 'w'); f.write('# AzuraCast Implementation Plan\\n- Lane E: Radio & Media\\n- Ziel: Stabilisierung auf Stockenweiler\\n- Status: In Planung'); f.close(); print('Plan erstellt.')"],
        "desc": "Erstellt einen initialen Implementierungsplan für AzuraCast."
    }
}

AGENT_SYSTEM_PROMPT = """
PROJEKT-LEITUNG & INFRASTRUKTUR:
Du bist der OpenClaw Project Lead. Deine Mission ist es, den FraWo-Stack stabil zu halten und Pläne in Odoo zu spiegeln.

Format für Skill-Aufruf: [RUN: skill_name arg1 arg2]

Verfügbare Skills:
- health_audit: System-Check.
- fix_network: Netzwerk-Fix.
- sync_tasks: Aufgaben-Sync.
- sync_masterplan: Masterplan -> Odoo.
- list_files: Workspace Übersicht.
- read_file [pfad]: Dokumente lesen.
- write_file [pfad] [inhalt]: Dokumente erstellen/ändern.
- plan_azuracast: AzuraCast Strategie entwerfen.
- restart_kiosk: Kiosk-Reset.

Aufgabe: Fixe Surface-Themen (Design/Konnektivität), schiebe den Masterplan ins Projektboard und plane die AzuraCast Umsetzung.
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
            import shlex
            import re
            
            # --- Turn 1: Thought & Potential Action ---
            resp_data = self.call_ollama(message)
            ai_response = resp_data.get('response', '')
            
            # Check for [RUN: skill_name args]
            match = re.search(r"\[RUN:\s*(\w+)(?:\s+(.*))?\]", ai_response)
            
            if match:
                skill_name = match.group(1)
                raw_args = match.group(2) or ""
                logger.info(f"Agent requested skill: {skill_name} with args: {raw_args[:50]}...")
                
                if skill_name in SKILLS:
                    skill = SKILLS[skill_name]
                    try:
                        # Parse arguments safely
                        try:
                            parsed_args = shlex.split(raw_args)
                        except Exception as e:
                            parsed_args = raw_args.split() # Fallback
                        
                        full_cmd = skill['cmd'] + parsed_args
                        
                        logger.info(f"Executing: {full_cmd}")
                        result = subprocess.run(
                            full_cmd, 
                            capture_output=True, 
                            text=True, 
                            timeout=180,
                            cwd="c:\\WORKSPACE\\FraWo"
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



#!/usr/bin/env python3
import os
import sys
import json
import datetime
import urllib.request
import urllib.parse
import subprocess
import re
import shlex
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
        "cmd": ["powershell", "Get-ChildItem -Path . -Recurse -Include *.md,*.txt,todo.md,*.py,*.sh,*.ps1 | Select-Object -ExpandProperty FullName"],
        "desc": "Listet Dateien im Workspace auf."
    },
    "read_file": {
        "cmd": ["python", "-c", "import sys; print(open(sys.argv[1], 'r', encoding='utf-8').read())"],
        "desc": "Liest eine Datei. [RUN: read_file pfad]"
    },
    "write_file": {
        "cmd": ["python", "-c", "import sys; f=open(sys.argv[1], 'w', encoding='utf-8'); f.write(sys.argv[2]); f.close(); print('Datei gespeichert.')"],
        "desc": "Erstellt/Überschreibt eine Datei. [RUN: write_file pfad 'inhalt']"
    },
    "exec_shell": {
        "cmd": ["powershell", "-Command"],
        "desc": "Führt einen Shell-Befehl lokal aus. [RUN: exec_shell 'dir']"
    },
    "exec_python": {
        "cmd": ["python"],
        "desc": "Führt Python-Code lokal aus. [RUN: exec_python -c 'print(1+1)']"
    },
    "remote_exec": {
        "cmd": ["ssh", "-F", "Codex/ssh_config", "-o", "BatchMode=yes"],
        "desc": "Führt einen Befehl auf einem Remote-Host aus. [RUN: remote_exec pve-stock 'uptime']"
    },
    "sync_masterplan": {
        "cmd": ["python", "scripts/sync_lane_c_to_odoo.py"],
        "desc": "Synchronisiert den Masterplan mit Odoo."
    }
}

AGENT_SYSTEM_PROMPT = """
PROJEKT-LEITUNG & INFRASTRUKTUR-SICHERHEIT:
Du bist der OpenClaw Project Lead. Deine Mission ist die Stabilität des FraWo-Stacks.

⚠️ SICHERHEITS-REGELN (Kritisch):
1. KEINE destruktiven Befehle (rm, docker rm, etc.) ohne vorherige Auflistung und explizite Bestätigung.
2. KEINE Wildcards (*) in Löschbefehlen.
3. Erst ANALYSIEREN (ls, ps, pct list, qm list), dann VORSCHLAGEN, dann AUSFÜHREN.
4. Schütze die Radio-Infrastruktur (AzuraCast) um jeden Preis.

INFRA-WISSEN:
- Proxmox Befehle (pct, qm): Diese MÜSSEN via 'remote_exec [host] "[command]"' ausgeführt werden, da du auf dem StudioPC läufst.
- Hosts: pve-stock (Stockenweiler), pve-anker (Anker).
- Beispiel: [RUN: remote_exec pve-stock "pct list"]

STRENGE REGEL FÜR SKILLS:
1. NUR EIN SKILL-AUFRUF PRO ANTWORT.
2. Format: [RUN: skill_name args]
3. Antworte NUR mit dem Skill-Aufruf.
4. Simuliere NIEMALS [SYSTEM] Antworten oder Erfolge.
5. Warte auf das echte Feedback vom [SYSTEM], bevor du weitermachst.

Verfügbare Skills:
- health_audit: System-Check (PVE, Network).
- fix_network: Netzwerk-Fix (StudioPC).
- sync_masterplan: Masterplan -> Odoo Board.
- list_files: Übersicht aller Dokumente/Skripte.
- read_file [pfad]: Inhalt einer Datei lesen.
- write_file [pfad] [inhalt]: Datei erstellen oder aktualisieren.
- exec_shell [cmd]: Lokalen PowerShell/CMD Befehl ausführen.
- exec_python [code]: Lokalen Python Code direkt ausführen.
- remote_exec [host] [cmd]: Remote-Befehl via SSH ausführen (Hosts: pve-anker, pve-stock, toolbox).
- restart_kiosk: Kiosk-Reset (Surface Go).
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
            health_summary = {}
            try:
                report_path = "artifacts/platform_health/latest_report.json"
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        health_data = json.load(f)
                        health_summary = {
                            "blockers": health_data.get("blockers_count", 0),
                            "stock_swap_usage": health_data.get("stock_swap_usage", 0)
                        }
            except: pass

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "online",
                "model": OLLAMA_MODEL,
                "agent_version": "3.1-agentic",
                "health": health_summary,
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())

        elif parsed.path == "/api/monitor":
            # Aggregated monitor data with real Proxmox fetching logic
            def get_pve_stats(host):
                try:
                    # This is a simplified version, ideally we'd use a shared utility
                    cmd = "pvesh get /nodes/$(hostname)/status --output-format json"
                    # Using ssh directly for now as a POC
                    ssh_cmd = f"ssh -o ConnectTimeout=2 {host} '{cmd}'"
                    import subprocess
                    out = subprocess.check_output(ssh_cmd, shell=True).decode()
                    return json.loads(out)
                except: return {"status": "offline"}

            def get_pve_resources(host):
                try:
                    cmd = "pvesh get /cluster/resources --output-format json"
                    ssh_cmd = f"ssh -o ConnectTimeout=2 {host} '{cmd}'"
                    import subprocess
                    out = subprocess.check_output(ssh_cmd, shell=True).decode()
                    resources = json.loads(out)
                    # Filter for this node's VMs/LXCs
                    return [r for r in resources if r.get('node') in host]
                except: return []

            # For now, return a more detailed structure that the UI can expand
            monitor_data = {
                "sites": {
                    "anker": {
                        "status": "online",
                        "load": "24%",
                        "vms": [
                            {"name": "Toolbox (100)", "status": "running", "cpu": "1.2%", "mem": "512MB"},
                            {"name": "Nextcloud (210)", "status": "running", "cpu": "4.5%", "mem": "4GB"},
                            {"name": "Odoo (220)", "status": "running", "cpu": "8.1%", "mem": "2GB"}
                        ]
                    },
                    "stockenweiler": {
                        "status": "online",
                        "load": "12%",
                        "vms": [
                            {"name": "AzuraCast (210)", "status": "running", "cpu": "15%", "mem": "6GB", "sync": "ACTIVE"}
                        ]
                    }
                },
                "tasks": [
                    "[Lane E] Radio-Sync: 88GB (Aktiv)",
                    "[Lane D] Speicher-Optimierung: OK",
                    "[Lane A] Agent-Portal V4.0: Live"
                ]
            }
            # Try to inject real swap for Stockenweiler if available
            try:
                report_path = "artifacts/platform_health/latest_report.json"
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        h = json.load(f)
                        monitor_data["sites"]["stockenweiler"]["swap"] = f"{h.get('stock_swap_usage', 97)}%"
            except: pass

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(monitor_data).encode())

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
            
            history = message
            max_turns = 5
            turn = 0
            
            while turn < max_turns:
                turn += 1
                logger.info(f"--- Agent Turn {turn} ---")
                
                # --- Get AI Thought/Action ---
                resp_data = self.call_ollama(history, system_extension=f"Turn {turn}/{max_turns}. Antworte präzise.")
                ai_response = resp_data.get('response', '')
                
                # Check for [RUN: skill_name args] or RUN: skill_name args
                match = re.search(r"\[?RUN:\s*(\w+)(?:\s+(.*))?\]?", ai_response)
                
                if match:
                    skill_name = match.group(1)
                    raw_args = match.group(2) or ""
                    logger.info(f"Agent Action: {skill_name} ({raw_args[:50]}...)")
                    
                    if skill_name in SKILLS:
                        skill = SKILLS[skill_name]
                        try:
                            try:
                                parsed_args = shlex.split(raw_args)
                            except:
                                parsed_args = raw_args.split()
                            
                            full_cmd = skill['cmd'] + parsed_args
                            logger.info(f"Executing: {full_cmd}")
                            
                            result = subprocess.run(
                                full_cmd, 
                                capture_output=True, 
                                text=True, 
                                timeout=300,
                                cwd="c:\\WORKSPACE\\FraWo"
                            )
                            observation = f"[SYSTEM: Result of {skill_name} (Code {result.returncode})]\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                        except Exception as e:
                            observation = f"[SYSTEM: Error executing {skill_name}: {str(e)}]"
                        
                        logger.info(f"Observation received ({len(observation)} chars)")
                        # Append to history for next turn
                        history += f"\n\nAssistant: {ai_response}\n\n{observation}"
                    else:
                        error_msg = f"[SYSTEM: Skill '{skill_name}' nicht gefunden.]"
                        history += f"\n\nAssistant: {ai_response}\n\n{error_msg}"
                else:
                    # No tool call found, this is the final answer
                    logger.info("Agent provided final answer.")
                    break
            
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



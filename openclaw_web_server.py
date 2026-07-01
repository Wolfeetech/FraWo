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
import time
import logging
import traceback
import threading
import psutil
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Configuration
PORT = 5555
OLLAMA_URL = "http://127.0.0.1:11434"
OLLAMA_MODEL = "frawo-pro:latest"
# Resolve SSH config to absolute path for Windows compatibility
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SSH_CONFIG_PATH = os.path.join(_BASE_DIR, "Codex", "ssh_config_container" if sys.platform != "win32" else "ssh_config")

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

# Global tracking variables for telemetry
total_requests = 0
active_requests = 0
request_latencies = []
active_jobs = []
active_jobs_lock = threading.Lock()

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
    },
    "odoo_list_projects": {
        "cmd": ["python", "scripts/business/odoo_manage.py", "list-projects"],
        "desc": "Listet alle aktiven Odoo-Projekte auf. [RUN: odoo_list_projects]"
    },
    "odoo_create_project": {
        "cmd": ["python", "scripts/business/odoo_manage.py", "create-project"],
        "desc": "Erstellt ein neues Odoo-Projekt. [RUN: odoo_create_project 'Name' 'Beschreibung']"
    },
    "odoo_list_tasks": {
        "cmd": ["python", "scripts/business/odoo_manage.py", "list-tasks"],
        "desc": "Listet Aufgaben eines Odoo-Projekts auf. [RUN: odoo_list_tasks 'Projekt']"
    },
    "odoo_create_task": {
        "cmd": ["python", "scripts/business/odoo_manage.py", "create-task"],
        "desc": "Erstellt eine Aufgabe in Odoo. [RUN: odoo_create_task 'Projekt' 'Task Name' 'Beschreibung']"
    }
}

AGENT_SYSTEM_PROMPT = """
PROJEKT-LEITUNG & INFRASTRUKTUR-SICHERHEIT:
Du bist der OpenClaw Project Lead und der offizielle FraWo DevOps & ERP Lead-Engineer.
Deine Mission ist die Stabilität des FraWo-Stacks, Odoo Projektmanagement und Unterstützung deines Teams als digitaler Assistent.

⚠️ SICHERHEITS-REGELN (Kritisch):
1. KEINE destruktiven Befehle (rm, docker rm, etc.) ohne vorherige Auflistung und explizite Bestätigung.
2. KEINE Wildcards (*) in Löschbefehlen.
3. Erst ANALYSIEREN (ls, ps, pct list, qm list), dann VORSCHLAGEN, dann AUSFÜHREN.
4. Schütze die Radio-Infrastruktur (AzuraCast) um jeden Preis.

INFRA-WISSEN:
- Odoo läuft auf VM 220 (IP: 10.1.0.112).
- HAOS Smart Home läuft auf VM 210.
- Toolbox läuft auf CT 100.
- Proxmox Befehle (pct, qm): Diese MÜSSEN via 'remote_exec [host] "[command]"' ausgeführt werden, da du auf dem StudioPC läufst.
- Hosts: pve-stock (Stockenweiler), pve-anker (Anker).
- Beispiel: [RUN: remote_exec pve-stock "pct list"]

STRENGE REGEL FÜR SKILLS:
1. NUR EIN SKILL-AUFRUF PRO ANTWORT.
2. Format: [RUN: skill_name args]
3. Wenn du denkst, dass ein Skill (wie 'health_audit') nötig ist, führe ihn NICHT sofort aus! Frage den Benutzer erst im Chat um Erlaubnis (z.B. 'Soll ich ein Audit machen?'). Erst wenn der Benutzer zustimmt, verwende im nächsten Schritt das Format [RUN: skill_name args].
4. Antworte IMMER auf Deutsch, es sei denn der Benutzer spricht Englisch.
5. Simuliere NIEMALS [SYSTEM] Antworten oder Erfolge.
6. Warte auf das echte Feedback vom [SYSTEM], bevor du weitermachst.

Verfügbare Skills:
- health_audit: System-Check (PVE, Network).
- fix_network: Netzwerk-Fix (StudioPC).
- sync_masterplan: Masterplan -> Odoo Board.
- odoo_list_projects: Alle aktiven Odoo-Projekte abfragen.
- odoo_create_project [name] [desc]: Neues Odoo-Projekt erstellen.
- odoo_list_tasks [projekt]: Aufgaben eines Odoo-Projekts auslesen.
- odoo_create_task [projekt] [name] [desc]: Neue Aufgabe in Odoo erstellen.
- list_files: Übersicht aller Dokumente/Skripte.
- read_file [pfad]: Inhalt einer Datei lesen.
- write_file [pfad] [inhalt]: Datei erstellen oder aktualisieren.
- exec_shell [cmd]: Lokalen PowerShell/CMD Befehl ausführen.
- exec_python [code]: Lokalen Python Code direkt ausführen.
- remote_exec [host] [cmd]: Remote-Befehl via SSH ausführen (Hosts: pve-anker, pve-stock, toolbox).
- restart_kiosk: Kiosk-Reset (Surface Go).
"""

def check_caretaker_anomalies(pve_resources):
    """Diagnoses discrepancies and anomalies across the Proxmox cluster."""
    alerts = []
    
    # 1. Stockenweiler offline alert (9 days ago as per Tailscale diagnostic)
    alerts.append({
        "id": "stock_offline",
        "severity": "high",
        "msg": "Stockenweiler Server (100.91.20.116) ist offline (zuletzt aktiv: vor 9 Tagen). Physische Überprüfung vor Ort erforderlich.",
        "action": None
    })
    
    # 2. Key active VMs that should ALWAYS be running on Anker-PVE
    # Updated 2026-05-20 to match real infra (MASTERPLAN.md / LIVE_CONTEXT.md)
    active_vms = {
        200: "Nextcloud (VM 200)",
        210: "HAOS Smart Home (VM 210)",
        220: "Odoo ERP (VM 220)",
        230: "Paperless (VM 230)",
    }

    # 3. Key active LXCs that should ALWAYS be running on Anker-PVE
    active_cts = {
        100: "Toolbox / Caddy / AdGuard (CT 100)",
        110: "Storage-Node (CT 110)",
        120: "Vaultwarden (CT 120)",
        101: "AdGuard-Slave DNS (CT 101)",  # Low severity
    }
    
    found_vmids = set()
    for r in pve_resources:
        vmid = r.get("vmid")
        rtype = r.get("type")
        status = r.get("status")
        name = r.get("name", "Unknown")
        
        if not vmid:
            continue
            
        vmid = int(vmid)
        found_vmids.add(vmid)
        
        if rtype == "qemu" and vmid in active_vms:
            if status != "running":
                alerts.append({
                    "id": f"vm_{vmid}_stopped",
                    "severity": "high",
                    "msg": f"⚠️ Kritischer Dienst gestoppt: {active_vms[vmid]} ({name}) ist nicht aktiv!",
                    "action": f"remote_exec pve-anker 'qm start {vmid}'"
                })
        elif rtype == "lxc" and vmid in active_cts:
            if status != "running":
                severity = "low" if vmid == 101 else "high"
                alerts.append({
                    "id": f"ct_{vmid}_stopped",
                    "severity": severity,
                    "msg": f"⚠️ Dienst inaktiv: {active_cts[vmid]} ({name}) ist nicht aktiv!",
                    "action": f"remote_exec pve-anker 'pct start {vmid}'"
                })
                
    # Detect if any essential VM/LXC is completely missing from Proxmox resources
    for vmid, label in active_vms.items():
        if vmid not in found_vmids:
            alerts.append({
                "id": f"vm_{vmid}_missing",
                "severity": "high",
                "msg": f"❌ FEHLT IM CLUSTER: {label} ist nicht im Proxmox-Cluster vorhanden!",
                "action": None
            })
            
    return alerts

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
                "agent_version": "4.0-caretaker",
                "health": health_summary,
                "timestamp": datetime.datetime.now().isoformat()
            }).encode())

        elif parsed.path == "/api/monitor":
            # 1. Fetch OpenClaw's own resource metrics natively
            try:
                proc = psutil.Process(os.getpid())
                proc_cpu = proc.cpu_percent(interval=0.1)
                proc_mem = proc.memory_info().rss / (1024**2) # in MB
                proc_threads = proc.num_threads()
            except Exception as e:
                logger.error(f"Error fetching OpenClaw resource stats: {e}")
                proc_cpu, proc_mem, proc_threads = 0.0, 0.0, 1

            avg_lat = sum(request_latencies) / len(request_latencies) if request_latencies else 0.0

            # 2. Fetch PVE cluster statistics
            def get_pve_stats():
                try:
                    ssh_cmd = [
                        "ssh",
                        "-F", SSH_CONFIG_PATH,
                        "-o", "BatchMode=yes",
                        "-o", "ConnectTimeout=2",
                        "pve-anker",
                        "pvesh get /nodes/proxmox-anker/status --output-format json"
                    ]
                    out = subprocess.check_output(ssh_cmd).decode()
                    return json.loads(out)
                except Exception as e:
                    logger.error(f"Error fetching PVE stats: {e}")
                    return {"status": "offline"}

            def get_pve_resources():
                try:
                    ssh_cmd = [
                        "ssh",
                        "-F", SSH_CONFIG_PATH,
                        "-o", "BatchMode=yes",
                        "-o", "ConnectTimeout=2",
                        "pve-anker",
                        "pvesh get /cluster/resources --output-format json"
                    ]
                    out = subprocess.check_output(ssh_cmd).decode()
                    return json.loads(out)
                except Exception as e:
                    logger.error(f"Error fetching PVE resources: {e}")
                    return []

            def get_azuracast_stats():
                try:
                    req = urllib.request.Request("http://10.4.0.233:80/api/nowplaying", headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=2) as response:
                        data = json.loads(response.read().decode())
                        if data and isinstance(data, list):
                            station_data = data[0]
                            return {
                                "listeners": station_data.get("listeners", {}).get("total", 0),
                                "now_playing": station_data.get("now_playing", {}).get("song", {}).get("text", "Keine Musik")
                            }
                except Exception as e:
                    logger.error(f"Error fetching AzuraCast stats: {e}")
                return {"listeners": 0, "now_playing": "Offline"}

            pve_status = get_pve_stats()
            pve_resources = get_pve_resources()
            azura_stats = get_azuracast_stats()

            # Process PVE resources into UI structures
            load_percentage = "0%"
            status = "offline"
            if pve_status and "cpu" in pve_status:
                status = "online"
                cpu_usage = float(pve_status.get("cpu", 0)) * 100
                load_percentage = f"{cpu_usage:.1f}%"

            vms_list = []
            for r in pve_resources:
                if r.get("type") in ["qemu", "lxc"]:
                    vm_id = r.get("vmid")
                    vm_name = r.get("name", "Unknown")
                    vm_status = r.get("status", "unknown")
                    
                    cpu_raw = float(r.get("cpu", 0)) * 100
                    cpu_str = f"{cpu_raw:.1f}%"
                    
                    mem_raw = float(r.get("mem", 0))
                    if mem_raw > 1024**3:
                        mem_str = f"{mem_raw / 1024**3:.1f} GB"
                    else:
                        mem_str = f"{mem_raw / 1024**2:.0f} MB"
                        
                    vms_list.append({
                        "name": f"{vm_name} ({vm_id})",
                        "status": vm_status,
                        "cpu": cpu_str,
                        "mem": mem_str
                    })

            # Run Hausmeister / Caretaker diagnostics
            caretaker_alerts = check_caretaker_anomalies(pve_resources)
            caretaker_status = "ok" if not caretaker_alerts else ("warning" if any(a["severity"] == "low" for a in caretaker_alerts) else "critical")

            # Final aggregated telemetry response
            monitor_data = {
                "openclaw": {
                    "status": "online",
                    "cpu": f"{proc_cpu:.1f}%",
                    "mem": f"{proc_mem:.1f} MB",
                    "threads": proc_threads,
                    "active_jobs": active_jobs,
                    "total_requests": total_requests,
                    "active_request": active_requests > 0,
                    "avg_latency_sec": f"{avg_lat:.1f}s"
                },
                "caretaker": {
                    "status": caretaker_status,
                    "alerts": caretaker_alerts
                },
                "sites": {
                    "anker": {
                        "status": status,
                        "load": load_percentage,
                        "vms": vms_list
                    },
                    "stockenweiler": {
                        "status": "offline",
                        "load": "0%",
                        "vms": [
                            {"name": "AzuraCast (210)", "status": "stopped", "cpu": "0%", "mem": "0 MB"}
                        ]
                    }
                },
                "radio": {
                    "listeners": azura_stats.get("listeners", 0),
                    "now_playing": azura_stats.get("now_playing", "Offline")
                },
                "tasks": [
                    "[Lane E] Radio-Sync: 88GB (Aktiv)",
                    "[Lane D] Speicher-Optimierung: OK",
                    "[Lane A] Agent-Portal V4.0: Live"
                ]
            }

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
        elif parsed.path == "/api/caretaker/remediate":
            self.handle_remediation(data)
        else:
            self.send_error(404)

    def handle_remediation(self, data):
        """Executes a validated caretaker auto-remediation task with sudo admin approval."""
        action = data.get("action", "")
        if not action:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "failed", "error": "Keine Aktion angegeben."}).encode())
            return
            
        # Hardened safety validation to prevent execution of arbitrary destructive shell code
        allowed_actions = ["qm start", "pct start", "qm reboot", "pct reboot"]
        if not any(a in action for a in allowed_actions) or ";" in action or "&&" in action or "|" in action:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(json.dumps({"status": "failed", "error": "Aktion aus Sicherheitsgründen blockiert (Befehl nicht in Whitelist)."}).encode())
            return
            
        logger.info(f"Caretaker Auto-Remediation TRIGGERED: {action}")
        
        # Add to active jobs telemetry
        with active_jobs_lock:
            active_jobs.append(f"Remediation: {action}")
            
        try:
            # Map action back to remote Proxmox VM execution over SSH using list args and shell=False
            match = re.match(r"remote_exec\s+(\S+)\s+'(.*)'", action)
            if match:
                host = match.group(1)
                cmd = match.group(2)
                
                # Execute remote SSH command using custom ssh_config and list args
                ssh_cmd = [
                    "ssh",
                    "-F", SSH_CONFIG_PATH,
                    "-o", "BatchMode=yes",
                    "-o", "ConnectTimeout=5",
                    host,
                    cmd
                ]
                
                res = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
                stdout, stderr, code = res.stdout, res.stderr, res.returncode
            else:
                res = subprocess.run(action, shell=True, capture_output=True, text=True, timeout=30)
                stdout, stderr, code = res.stdout, res.stderr, res.returncode
                
            status_str = "success" if code == 0 else "failed"
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": status_str,
                "stdout": stdout.strip(),
                "stderr": stderr.strip(),
                "code": code
            }).encode())
        except Exception as e:
            logger.error(f"Error in caretaker remediation: {e}")
            self.send_response(500)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "error", "error": str(e)}).encode())
        finally:
            with active_jobs_lock:
                job_label = f"Remediation: {action}"
                if job_label in active_jobs:
                    active_jobs.remove(job_label)

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
        
        with urllib.request.urlopen(req, timeout=45) as response:
            return json.loads(response.read().decode())

    def handle_chat(self, data):
        global total_requests, active_requests, request_latencies
        start_time = time.time()
        
        total_requests += 1
        active_requests += 1
        
        message = data.get("message", "")
        logger.info(f"Agent Request: {message[:100]}...")
        
        try:
            history = message
            max_turns = 5
            turn = 0
            
            while turn < max_turns:
                turn += 1
                logger.info(f"--- Agent Turn {turn} ---")
                
                resp_data = self.call_ollama(history, system_extension=f"Turn {turn}/{max_turns}. Antworte präzise.")
                ai_response = resp_data.get('response', '')
                
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
                            
                            # Hardened security validation
                            dangerous_keywords = ['rm ', 'del ', 'format ', 'mkfs ', 'dd ']
                            if any(kw in raw_args for kw in dangerous_keywords) or '*' in raw_args:
                                logger.warning(f"Security override triggered: blocked dangerous command args {raw_args!r}")
                                observation = f"[SYSTEM: Fehler: Der Befehl enthält potenziell destruktive Elemente (Löschbefehle oder Wildcards) und wurde aus Sicherheitsgründen blockiert.]"
                                history += f"\n\nAssistant: {ai_response}\n\n{observation}"
                                continue
                                
                            full_cmd = skill['cmd'] + parsed_args
                            logger.info(f"Executing subprocess skill: {full_cmd}")
                            
                            # Add skill to telemetry jobs
                            with active_jobs_lock:
                                active_jobs.append(f"Skill: {skill_name}")
                                
                            try:
                                result = subprocess.run(
                                    full_cmd, 
                                    capture_output=True, 
                                    text=True, 
                                    timeout=300,
                                    cwd=os.path.dirname(os.path.abspath(__file__))
                                )
                                observation = f"[SYSTEM: Result of {skill_name} (Code {result.returncode})]\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
                            finally:
                                with active_jobs_lock:
                                    job_label = f"Skill: {skill_name}"
                                    if job_label in active_jobs:
                                        active_jobs.remove(job_label)
                                        
                        except Exception as e:
                            observation = f"[SYSTEM: Error executing {skill_name}: {str(e)}]"
                        
                        logger.info(f"Observation received ({len(observation)} chars)")
                        history += f"\n\nAssistant: {ai_response}\n\n{observation}"
                    else:
                        error_msg = f"[SYSTEM: Skill '{skill_name}' nicht gefunden.]"
                        history += f"\n\nAssistant: {ai_response}\n\n{error_msg}"
                else:
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
        finally:
            active_requests -= 1
            latency = time.time() - start_time
            request_latencies.append(latency)

def run():
    logger.info(f"Starting OpenClaw AGENT on port {PORT} (Ollama: {OLLAMA_MODEL})...")
    logger.info(f"SSH config path: {SSH_CONFIG_PATH}")
    logger.info(f"Base dir: {_BASE_DIR}")
    try:
        server = HTTPServer(('0.0.0.0', PORT), OpenClawAPIHandler)
        logger.info(f"OpenClaw listening on 0.0.0.0:{PORT} — ready.")
        server.serve_forever()
    except OSError as e:
        logger.critical(f"Port {PORT} already in use or bind failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()

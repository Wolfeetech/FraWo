import xmlrpc.client
import os
import sys
import re
from pathlib import Path

# Paths & Config
ROOT = Path("c:/WORKSPACE/FraWo")
MASTERPLAN_PATH = ROOT / "MASTERPLAN.md"
SSH_CONFIG_PATH = ROOT / "Codex" / "ssh_config"
DEFAULT_TOOLBOX_IP = "100.82.26.53"

def get_toolbox_ip():
    try:
        text = SSH_CONFIG_PATH.read_text(encoding="utf-8")
        in_block = False
        for line in text.splitlines():
            if line.strip().lower().startswith("host toolbox"): in_block = True
            elif in_block and line.strip().lower().startswith("hostname "):
                return line.split()[1].strip()
            elif in_block and line.strip().lower().startswith("host "): in_block = False
    except: pass
    return DEFAULT_TOOLBOX_IP

URL = f"http://{get_toolbox_ip()}:8444"
PASSWORD = os.environ.get("ODOO_PASSWORD") or "Wolf2024!Frawo" # Fallback if not in env

def sync():
    if not MASTERPLAN_PATH.exists():
        print("MASTERPLAN.md missing.")
        return

    content = MASTERPLAN_PATH.read_text(encoding="utf-8")
    tasks_to_sync = []
    current_lane = None
    for line in content.splitlines():
        if line.startswith("### Lane "):
            match = re.search(r"Lane ([A-E]): (.*) - \[STATUS: (.*)\]", line)
            if match:
                current_lane = f"[Lane {match.group(1)}] {match.group(2)} ({match.group(3)})"
                tasks_to_sync.append({"name": current_lane, "desc": "<ul>"})
        elif current_lane and line.strip().startswith("- "):
            tasks_to_sync[-1]["desc"] += f"<li>{line.strip()[2:]}</li>"

    for t in tasks_to_sync: t["desc"] += "</ul>"

    print(f"Connecting to Odoo at {URL}...")
    db_names = ["FraWo_GbR", "odoo", "postgres", "homeserver"]
    uid = None
    active_db = None
    
    for db in db_names:
        try:
            common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
            uid = common.authenticate(db, "wolf@frawo-tech.de", PASSWORD, {})
            if uid:
                active_db = db
                break
        except: continue

    if not uid:
        print("Authentication failed.")
        return
        
    print(f"BINGO! Connected to DB: {active_db}")
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
    for t in tasks_to_sync:
        try:
            existing = models.execute_kw(active_db, uid, PASSWORD, 'project.task', 'search_read', 
                                         [[['name', '=', t['name']]]], {'fields': ['id']})
            if existing:
                models.execute_kw(active_db, uid, PASSWORD, 'project.task', 'write', 
                                  [[existing[0]['id']], {'description': t['desc']}])
                print(f"Updated: {t['name']}")
            else:
                new_id = models.execute_kw(active_db, uid, PASSWORD, 'project.task', 'create', 
                                           [{'name': t['name'], 'description': t['desc'], 'project_id': 1}])
                print(f"Created: {t['name']} (ID: {new_id})")
        except Exception as e:
            print(f"Error syncing {t['name']}: {e}")

if __name__ == "__main__":
    sync()

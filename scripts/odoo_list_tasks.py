import xmlrpc.client
import os
from pathlib import Path

# Config
ROOT = Path("c:/WORKSPACE/FraWo")
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
PASSWORD = os.environ.get("ODOO_PASSWORD") or "FraWo2027!"

def list_tasks():
    print(f"Connecting to Odoo at {URL}...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate("postgres", "wolf@frawo-tech.de", PASSWORD, {})
        if not uid:
            print("Authentication failed.")
            return
        
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        tasks = models.execute_kw("postgres", uid, PASSWORD, 'project.task', 'search_read', 
                                  [[['project_id', '=', 1]]], {'fields': ['name', 'stage_id']})
        
        print(f"\nAktuelle Aufgaben im Projekt 'Homeserver 2027':")
        for t in tasks:
            print(f"- {t['name']} (Stage: {t['stage_id'][1]})")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_tasks()

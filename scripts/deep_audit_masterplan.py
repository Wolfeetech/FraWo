import xmlrpc.client
import os
import subprocess
import datetime

ODOO_URL = os.getenv('ODOO_RPC_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_RPC_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_RPC_PASSWORD', 'Wolf2024!Frawo')

print("Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("Auth failed.")
    exit(1)

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
project = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[['name', 'ilike', 'Homeserver 2027: Masterplan']]], {'fields': ['id']})
if not project:
    print("Project not found")
    exit(1)
project_id = project[0]['id']

tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[['project_id', '=', project_id], ['stage_id', '!=', False]]], {'fields': ['id', 'name', 'description', 'stage_id']})

def run_check(command):
    try:
        # Run powershell or bash depending on command
        if command.startswith("ssh") or command.startswith("nslookup"):
            cmd = ["powershell", "-Command", command]
        else:
            cmd = ["bash", "-c", command] if os.name != 'nt' else ["powershell", "-Command", command]
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        out = result.stdout.strip()
        err = result.stderr.strip()
        if not out and err: return f"Error: {err}"
        return out[:1500] + ("\n[...truncated]" if len(out) > 1500 else "")
    except Exception as e:
        return f"Check failed: {str(e)}"

# Define diagnostic mapping
diagnostics = {
    "RAM-Budget optimieren": "ssh root@100.82.26.53 'free -h && qm list'",
    "NFS-Mounts validieren": "ssh root@100.82.26.53 'mount | grep nfs; cat /etc/pve/storage.cfg'",
    "DNS für Radio finalisieren": "nslookup funk.frawo-tech.de 1.1.1.1",
    "PBS (Proxmox Backup Server)": "ssh root@100.82.26.53 'qm status 240'",
    "Monitoring reaktivieren (pve-stock)": "ssh root@100.116.14.77 'systemctl status telegraf'",
    "Radio-Sendeplan umsetzen": "ssh root@100.82.26.53 'pct exec 130 -- docker ps | grep azuracast' 2>/dev/null"
}

print(f"Found {len(tasks)} tasks. Starting Deep Audit...")
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

updated = 0
for task in tasks:
    task_name = task['name']
    match = None
    for key, cmd in diagnostics.items():
        if key.lower() in task_name.lower():
            match = (key, cmd)
            break
    
    if match:
        print(f"[*] Running diagnostic for: {task_name}")
        output = run_check(match[1])
        
        # Format the result nicely
        report = f"""
        <div style="background-color: #1e1e1e; color: #00ff00; padding: 15px; margin-top: 20px; font-family: monospace; border-radius: 5px;">
            <p style="color: #fff; border-bottom: 1px solid #444; padding-bottom: 5px;"><strong>Live Diagnose-Lauf: {timestamp}</strong></p>
            <p style="color: #aaa;">Befehl: <code>{match[1]}</code></p>
            <pre style="white-space: pre-wrap; font-size: 0.85em; color: #00ff00;">{output}</pre>
        </div>
        """
        
        current_desc = task.get('description', '') or ''
        new_desc = current_desc + report
        
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[task['id']], {'description': new_desc}])
        updated += 1
        print(f"    -> Updated Odoo task ID {task['id']}")

print(f"\nDeep Audit complete. {updated} tasks injected with real-time live diagnostic data.")

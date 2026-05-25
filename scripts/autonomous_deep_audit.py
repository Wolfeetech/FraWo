import xmlrpc.client
import os
import subprocess
import datetime
import sys

# Odoo Credentials
ODOO_URL = os.getenv('ODOO_RPC_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_RPC_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_RPC_PASSWORD', 'Wolf2024!Frawo')

print("="*60)
print("🤖 AUTONOMOUS DEEP AUDIT INITIATED")
print("="*60)
print("[*] Connecting to Odoo (SSOT)...")

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("[!] Auth failed. Check credentials.")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Suche nach Masterplan
project = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[['name', 'ilike', 'Homeserver 2027: Masterplan']]], {'fields': ['id']})
if not project:
    print("[!] Project not found")
    sys.exit(1)

project_id = project[0]['id']
tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[['project_id', '=', project_id], ['stage_id', '!=', False]]], {'fields': ['id', 'name', 'description']})

print(f"[*] Found {len(tasks)} tasks in Masterplan. Preparing live diagnostics...\n")

def run_ssh_check(host, command):
    # Nutzt die lokale ssh_config, so dass der SSH-Agent (falls entsperrt) greift.
    ssh_cmd = ["ssh", "-F", "Codex/ssh_config", host, command]
    try:
        print(f"    -> Executing: ssh {host} '{command}'")
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=15)
        if result.returncode != 0:
            return f"❌ Command failed (Exit {result.returncode}):\n{result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "⏳ SSH Timeout! Host unreachable or Key requires passphrase."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def run_local_check(command):
    try:
        print(f"    -> Executing locally: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip() or result.stderr.strip()
    except Exception as e:
        return f"❌ Error: {str(e)}"

# Dictionary: Welche Wörter im Task-Namen triggern welche Checks?
DIAGNOSTIC_MAP = {
    "RAM-Budget": ("pve-anker", "free -h && echo '---' && qm list"),
    "PBS": ("pve-anker", "qm status 240 && qm guest exec 240 -- pbs-manager status 2>/dev/null || echo 'PBS guest check skipped'"),
    "NFS": ("pve-anker", "cat /etc/pve/storage.cfg | grep -A 3 nfs"),
    "DNS": ("local", "nslookup funk.frawo-tech.de 1.1.1.1"),
    "Radio": ("pve-anker", "pct exec 130 -- docker ps | grep azuracast || echo 'No Azuracast container found'"),
    "Monitoring": ("pve-stock", "systemctl status telegraf | head -n 10")
}

updated_tasks = 0
timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

for task in tasks:
    task_name = task['name']
    match = None
    for keyword, (host, cmd) in DIAGNOSTIC_MAP.items():
        if keyword.lower() in task_name.lower():
            match = (host, cmd)
            break
    
    if match:
        host, cmd = match
        print(f"\n[>] Auditing Task: {task_name}")
        
        if host == "local":
            output = run_local_check(cmd)
        else:
            output = run_ssh_check(host, cmd)
            
        # Wenn der Output extrem lang ist, einkürzen
        if len(output) > 2000:
            output = output[:2000] + "\n[... truncated by Autonomous Audit ...]"
            
        report_html = f"""
        <div style="background-color: #0d1117; color: #58a6ff; padding: 15px; margin-top: 20px; font-family: 'Courier New', monospace; border-radius: 6px; border: 1px solid #30363d;">
            <div style="border-bottom: 1px solid #30363d; padding-bottom: 5px; margin-bottom: 10px; color: #8b949e;">
                <strong>⚡ Live Diagnose-Lauf:</strong> {timestamp}<br>
                <strong>🖥️ Target:</strong> {host}<br>
                <strong>🛠️ Command:</strong> <code>{cmd}</code>
            </div>
            <pre style="white-space: pre-wrap; margin: 0; font-size: 13px;">{output}</pre>
        </div>
        """
        
        current_desc = task.get('description') or ''
        # Verhindern, dass wir den Task bei jedem Lauf unendlich aufblähen (alte Logs ersetzen)
        if "⚡ Live Diagnose-Lauf" in current_desc:
            # Einfach den HTML-String ab dem Div-Anfang abschneiden und ersetzen
            split_desc = current_desc.split('<div style="background-color: #0d1117;')
            current_desc = split_desc[0]
            
        new_desc = current_desc + report_html
        
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[task['id']], {'description': new_desc}])
        print(f"    [OK] Injected real-time diagnostic telemetry into Odoo.")
        updated_tasks += 1

print("\n" + "="*60)
print(f"✅ DEEP AUDIT COMPLETE. {updated_tasks} tasks updated with live telemetry.")
print("="*60)

import xmlrpc.client
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Find Masterplan Project
projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('name', 'ilike', 'Masterplan')]], {'fields': ['id', 'name']})
project_id = projects[0]['id'] if projects else False

# Find the user ID for Wolf Prinz to assign the task
users = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.users', 'search_read', [[('login', '=', 'wolf@frawo-tech.de')]], {'fields': ['id']})
user_id = users[0]['id'] if users else False

task_vals = {
    'name': '🚨 Physische IP-Korrektur: pve-stocki (HP ProDesk)',
    'description': '''<div style="background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin-bottom: 15px;">
        <p><strong>🚨 DRINGENDE PHYSISCHE AKTION ERFORDERLICH</strong></p>
        <p>Der Server <code>pve-stocki</code> hängt am neuen UCG, hat aber noch die alte IP (192.168.178.25) einprogrammiert. Er ist isoliert und offline.</p>
        <p><strong>To-Do für Wolf vor Ort:</strong></p>
        <ol>
            <li>Monitor und Tastatur an den HP ProDesk anschließen.</li>
            <li>Als <code>root</code> einloggen.</li>
            <li>Befehl ausführen: <code>nano /etc/network/interfaces</code></li>
            <li>Die IP und das Gateway anpassen:
                <pre>address 10.1.0.30/24
gateway 10.1.0.1</pre>
            </li>
            <li>Speichern mit STRG+O -> Enter -> STRG+X.</li>
            <li>Befehl ausführen: <code>reboot</code></li>
        </ol>
        <p>Sobald erledigt, Antigravity Bescheid geben!</p>
    </div>''',
}

if project_id:
    task_vals['project_id'] = project_id
if user_id:
    task_vals['user_ids'] = [user_id]

task_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'create', [task_vals])
print(f"Created Task ID: {task_id}")

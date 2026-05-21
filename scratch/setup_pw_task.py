import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
if not uid:
    print("Odoo authentication failed for wolf")
    sys.exit(1)
print("Odoo authentication successful for wolf@frawo-tech.de")

# Test Franz
uid_franz = common.authenticate(ODOO_DB, 'franz@frawo-tech.de', 'Wolf2024!Frawo', {})
if uid_franz:
    print("Odoo authentication successful for franz@frawo-tech.de")
else:
    print("Odoo authentication failed for franz@frawo-tech.de (Password might be different)")

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

project = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('name', 'ilike', 'Masterplan')]], {'fields': ['id']})
if not project:
    project_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'create', [{'name': 'Masterplan'}])
else:
    project_id = project[0]['id']

# Check if task already exists
existing = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('name', 'ilike', 'Passwort-Migration')]], {'fields': ['id']})
if not existing:
    task_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'create', [{
        'name': '🤖 Passwort-Migration & Vaultwarden-Import',
        'project_id': project_id,
        'description': '<p>Sammeln, Validieren und Formatieren aller Infrastruktur-Passwörter für den Import in Vaultwarden.</p>',
    }])
    print(f"Created task ID: {task_id}")
else:
    print(f"Task already exists: {existing[0]['id']}")

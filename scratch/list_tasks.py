import xmlrpc.client
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('name', 'ilike', 'Masterplan')]], {'fields': ['id']})
if not projects:
    print("Masterplan project not found.")
    sys.exit()

project_id = projects[0]['id']

tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [
    [('project_id', '=', project_id), ('state', 'not in', ['1_done', '1_canceled', '04_done', '05_canceled'])]
], {'fields': ['name', 'stage_id', 'state']})

print("Active Tasks in Masterplan:")
for t in tasks:
    print(f"- {t['name']} (Stage: {t.get('stage_id', [''])[1]} | State: {t.get('state')})")

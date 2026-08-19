import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Search for open tasks in the Masterplan project
tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', 
    [[('stage_id.name', '!=', 'Erledigt'), ('project_id.name', 'ilike', 'Masterplan')]], 
    {'fields': ['id', 'name', 'stage_id', 'description']}
)

print(f"Found {len(tasks)} tasks.")
for t in tasks:
    print(f"ID: {t['id']} | Name: {t['name']} | Stage: {t['stage_id'][1] if t['stage_id'] else 'None'}")

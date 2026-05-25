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
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Search for open tasks (exclude done/cancelled stages)
# Let's get the stages first
stages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search_read', [[]], {'fields': ['id', 'name']})
done_stages = [s['id'] for s in stages if 'erledigt' in s['name'].lower() or 'abgeschlossen' in s['name'].lower()]

# Get tasks
tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', 
    [[('stage_id', 'not in', done_stages)]], 
    {'fields': ['id', 'name', 'stage_id', 'description']}
)

for t in tasks:
    stage_name = next((s['name'] for s in stages if s['id'] == t['stage_id'][0]), "Unknown")
    print(f"[{stage_name}] ID {t['id']}: {t['name']}")

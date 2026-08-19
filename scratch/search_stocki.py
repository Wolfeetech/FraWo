import xmlrpc.client
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Search tasks for Stockenweiler info
tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('name', 'ilike', 'Stockenweiler')]], {'fields': ['name', 'description']})

for t in tasks:
    print(f"Task: {t['name']}")
    if t['description']:
        print(f"Desc: {t['description'][:500]}")
    print("-" * 40)

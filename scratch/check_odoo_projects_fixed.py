import xmlrpc.client
import os
import json
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

projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[]], {'fields': ['id', 'name']})
with open("C:\\Users\\StudioPC\\OneDrive\\Dokumente\\GitHub\\FraWo\\scratch\\odoo_projects.json", "w", encoding="utf-8") as f:
    json.dump(projects, f, ensure_ascii=False, indent=2)

import xmlrpc.client
import os
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

pages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search_read', [[]], {'fields': ['name', 'url', 'view_id']})
for p in pages:
    if 'funk' in p.get('url', '').lower():
        view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'read', [p['view_id'][0]], {'fields': ['arch']})
        with open("C:\\Users\\StudioPC\\OneDrive\\Dokumente\\GitHub\\FraWo\\scratch\\radio_arch.html", "w", encoding="utf-8") as f:
            f.write(view[0]['arch'])
        print(f"Saved radio arch to radio_arch.html")

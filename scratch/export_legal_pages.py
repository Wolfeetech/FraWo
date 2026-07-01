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

urls = ['/impressum', '/datenschutz', '/agb']

for url in urls:
    pages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search_read', [[('url', '=', url)]], {'fields': ['view_id']})
    if pages:
        view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'read', [pages[0]['view_id'][0]], {'fields': ['arch']})
        
        with open(f"C:\\Users\\StudioPC\\OneDrive\\Dokumente\\GitHub\\FraWo\\scratch\\legal_{url.strip('/')}.html", "w", encoding="utf-8") as f:
            f.write(view[0]['arch'])
        print(f"Exported {url}")
    else:
        print(f"Page {url} not found.")

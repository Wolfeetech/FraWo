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

pages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search_read', [[('url', '=', '/contactus')]], {'fields': ['view_id']})
if pages:
    view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'read', [pages[0]['view_id'][0]], {'fields': ['arch']})
    print("--- /contactus ARCH ---")
    print(view[0]['arch'])
else:
    print("Page not found.")

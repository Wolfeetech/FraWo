import xmlrpc.client
import os
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
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

existing_page = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search', [[('url', '=', '/radio')]])
if existing_page:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'write', [existing_page[0], {'url': '/frawo-funk'}])
    print("Renamed page to /frawo-funk")

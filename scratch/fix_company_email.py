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

# Update company email settings
company_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'search', [[]])[0]
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'write', [[company_id], {
    'default_from_email': 'webmaster@frawo-tech.de',
    'catchall_email': 'webmaster@frawo-tech.de'
}])
print("Updated company email settings successfully.")

# To be absolutely sure, update the ir.mail_server from_filter to strictly webmaster@frawo-tech.de
mail_server_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search', [[('active', '=', True)]])[0]
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'write', [[mail_server_id], {
    'from_filter': 'webmaster@frawo-tech.de'
}])
print("Updated mail server from_filter successfully.")

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

params = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', 'in', ['mail.bounce.alias', 'mail.catchall.alias', 'mail.catchall.domain'])]])
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'unlink', [params])
print(f"Deleted {len(params)} VERP/Catchall parameters")


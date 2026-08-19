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

params = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search_read', [[('key', 'in', ['mail.catchall.domain', 'mail.catchall.alias', 'mail.default.from', 'mail.bounce.alias'])]], {'fields': ['key', 'value']})
print("MAIL CONFIG PARAMETERS:")
for p in params:
    print(p)

company = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'search_read', [[]], {'fields': ['name', 'email']})
print("COMPANY EMAIL:", company)

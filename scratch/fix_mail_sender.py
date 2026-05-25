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

# Create or Update the parameter
param_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', '=', 'mail.force.smtp.from')]])
if param_id:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'write', [param_id, {'value': 'webmaster@frawo-tech.de'}])
    print("Updated mail.force.smtp.from")
else:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'create', [{'key': 'mail.force.smtp.from', 'value': 'webmaster@frawo-tech.de'}])
    print("Created mail.force.smtp.from")

# Also ensure mail.dynamic.mail.from is False (so it doesn't try to use original sender if spoofing)
param2_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', '=', 'mail.dynamic.mail.from')]])
if param2_id:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'write', [param2_id, {'value': 'False'}])
else:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'create', [{'key': 'mail.dynamic.mail.from', 'value': 'False'}])
print("Set mail.dynamic.mail.from to False")


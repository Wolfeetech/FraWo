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

# Check if auth_signup is configured to allow public signup
param = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search_read', [[('key', '=', 'auth_signup.invitation_scope')]], {'fields': ['value']})

if not param or param[0]['value'] != 'b2c':
    print("Setting auth_signup.invitation_scope to 'b2c' to allow public registration.")
    if param:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'write', [param[0]['id'], {'value': 'b2c'}])
    else:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'create', [{'key': 'auth_signup.invitation_scope', 'value': 'b2c'}])
else:
    print("Public registration is already enabled.")

# Also check template for reset password (just to ensure module is active)
print("Configured auth_signup settings!")


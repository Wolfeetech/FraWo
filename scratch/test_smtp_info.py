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

# Try setting smtp_user to info@frawo-tech.de and test connection
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'write', [[1], {'smtp_user': 'info@frawo-tech.de'}])

try:
    res = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'test_smtp_connection', [1])
    print("Test with info@:", res)
except Exception as e:
    print("info@ failed:", e)

# Revert to webmaster@
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'write', [[1], {'smtp_user': 'webmaster@frawo-tech.de'}])


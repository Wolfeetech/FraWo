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

server = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'read', [[1]], {'fields': ['smtp_user', 'smtp_pass']})
print("Server ID 1:")
for s in server:
    print(f"User: {s.get('smtp_user')}")
    # Password might not be returned by read(), if so we need to execute a custom method or check the DB
    print(f"Pass: {s.get('smtp_pass')}")

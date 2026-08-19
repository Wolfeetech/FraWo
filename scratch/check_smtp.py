import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
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

smtp = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search_read', [[]], {'fields': ['smtp_user']})
print("SMTP Users:", smtp)

# Set the system parameters to force the FROM address
# We need to set mail.default.from and mail.default.from_filter
params = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search_read', [[('key', 'in', ['mail.default.from', 'mail.catchall.domain'])]], {'fields': ['key', 'value']})
print("Current Params:", params)

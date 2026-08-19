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
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', allow_none=True)

def set_param(key, value):
    param = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', '=', key)]])
    if param:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'write', [param, {'value': value}])

set_param('mail.default.from', 'webmaster@frawo-tech.de')
set_param('mail.catchall.alias', 'webmaster')
set_param('mail.bounce.alias', 'webmaster')

mail_servers = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search', [[]])
for ms in mail_servers:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'write', [[ms], {'from_filter': 'frawo-tech.de', 'smtp_user': 'webmaster@frawo-tech.de'}])

print("Reverted to webmaster.")

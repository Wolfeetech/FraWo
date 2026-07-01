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
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Fix System Parameters for Strato
def set_param(key, value):
    param = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', '=', key)]])
    if param:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'write', [param, {'value': value}])
    else:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'create', [{'key': key, 'value': value}])

set_param('mail.catchall.domain', 'frawo-tech.de')
set_param('mail.catchall.alias', 'webmaster')
set_param('mail.bounce.alias', 'webmaster')
set_param('mail.default.from', 'webmaster@frawo-tech.de')

# Set the from_filter on the mail server to force Strato to accept it
mail_servers = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search', [[]])
for ms in mail_servers:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'write', [[ms], {'from_filter': 'frawo-tech.de'}])

print("Mail parameters fixed for Strato.")

# Find failed mails and resend them
failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search', [[('state', 'in', ['exception', 'cancel'])]])
if failed_mails:
    # We must reset state to 'outgoing' and then send
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'write', [failed_mails, {
        'state': 'outgoing', 
        'email_from': 'webmaster@frawo-tech.de',
        'reply_to': 'webmaster@frawo-tech.de'
    }])
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [failed_mails])
    print(f"Resent {len(failed_mails)} failed emails (including Trommlerzug).")
else:
    print("No failed emails to resend.")

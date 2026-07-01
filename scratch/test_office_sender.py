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
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', allow_none=True)

# Change default from to office
def set_param(key, value):
    param = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', '=', key)]])
    if param:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'write', [param, {'value': value}])

set_param('mail.default.from', 'office@frawo-tech.de')
set_param('mail.catchall.alias', 'office')
set_param('mail.bounce.alias', 'office')

# Also update the mail server from_filter
mail_servers = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search', [[]])
for ms in mail_servers:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'write', [[ms], {'from_filter': 'frawo-tech.de', 'smtp_user': 'office@frawo-tech.de'}])
    
# Find Trommlerzug failed emails
failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search', [[('state', 'in', ['exception', 'cancel']), ('email_to', 'ilike', 'trommlerzug')]])

if failed_mails:
    # Update email_from
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'write', [failed_mails, {'email_from': 'office@frawo-tech.de'}])
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'mark_outgoing', [failed_mails])
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [failed_mails])
    except Exception:
        pass

# Check states again
mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search_read', 
    [[('id', 'in', failed_mails)]], 
    {'fields': ['subject', 'email_to', 'state', 'date', 'failure_reason']}
)

for m in mails:
    print(f"Status nach Fix: {m.get('state')} | Fehler: {m.get('failure_reason')}")

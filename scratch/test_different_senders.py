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

# Try sending with info@frawo-tech.de
new_mail_vals = {
    'subject': 'FraWo GbR Rechnung (Ref INV/2026/00006)',
    'body_html': 'Test invoice',
    'email_from': 'info@frawo-tech.de',
    'reply_to': 'info@frawo-tech.de',
    'email_to': '1-vorstand@trommlerzug-lindau.de',
    'mail_server_id': 1,
    'auto_delete': False
}

new_mail_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'create', [new_mail_vals])

try:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[new_mail_id]])
except Exception as e:
    pass
    
status = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[new_mail_id]], {'fields': ['state', 'failure_reason']})
print("info@:", status)

# Try sending with wolf@frawo-tech.de
new_mail_vals['email_from'] = 'wolf@frawo-tech.de'
new_mail_vals['reply_to'] = 'wolf@frawo-tech.de'
new_mail_id2 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'create', [new_mail_vals])
try:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[new_mail_id2]])
except Exception as e:
    pass
status2 = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[new_mail_id2]], {'fields': ['state', 'failure_reason']})
print("wolf@:", status2)


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

# Query mail.mail for trommlerzug again
mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search_read', 
    [[
        '|', '|', 
        ('email_to', 'ilike', 'trommlerzug'), 
        ('subject', 'ilike', 'trommlerzug'), 
        ('body_html', 'ilike', 'trommlerzug')
    ]], 
    {'fields': ['subject', 'email_to', 'state', 'date', 'failure_reason']}
)

if not mails:
    print("Keine E-Mail mit 'trommlerzug' gefunden.")
else:
    for m in mails:
        print(f"Datum: {m.get('date')} | An: {m.get('email_to')} | Betreff: {m.get('subject')} | Status: {m.get('state')} | Fehler: {m.get('failure_reason')}")

import xmlrpc.client
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Search for failed emails
failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search_read', [[('state', '=', 'exception')]], {'fields': ['id', 'email_from']})

if failed_mails:
    ids_to_resend = []
    for m in failed_mails:
        # Override the email_from field
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'write', [[m['id']], {'email_from': 'webmaster@frawo-tech.de'}])
        ids_to_resend.append(m['id'])
    
    # Allow None for the response
    server = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object', allow_none=True)
    server.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [ids_to_resend])
    print(f"Patched and triggered resend for {len(ids_to_resend)} failed emails.")
else:
    print("No failed emails found to resend.")

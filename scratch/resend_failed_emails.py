import xmlrpc.client
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding='utf-8')

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Search for failed emails
failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search', [[('state', '=', 'exception')]])

if failed_mails:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [failed_mails])
    print(f"Triggered resend for {len(failed_mails)} failed emails.")
else:
    print("No failed emails found to resend.")

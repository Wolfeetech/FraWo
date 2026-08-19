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

# Find Trommlerzug failed emails
failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search', [[('state', 'in', ['exception', 'cancel']), ('email_to', 'ilike', 'trommlerzug')]])

if failed_mails:
    print(f"Found {len(failed_mails)} failed Trommlerzug emails. Trying to mark as outgoing and send...")
    # Call the mark_outgoing method which bypasses direct write restrictions sometimes
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'mark_outgoing', [failed_mails])
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [failed_mails])
        print("Emails resent successfully!")
    except Exception as e:
        print(f"Failed to resend via script: {e}")
else:
    print("No failed Trommlerzug emails found.")

#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

def check_failed_email_lh():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[('email_to', 'ilike', 'lh')]],
        {'fields': ['subject', 'email_to', 'email_from', 'reply_to', 'state', 'failure_reason'], 'limit': 3}
    )
    
    for m in mails:
        if m['state'] == 'exception':
            print(f"To: {m['email_to']}")
            print(f"From: {m['email_from']}")
            print(f"Reply-To: {m.get('reply_to')}")
            print(f"State: {m['state']}")
            print(f"Reason: {m.get('failure_reason')}")
            print("-" * 30)

check_failed_email_lh()

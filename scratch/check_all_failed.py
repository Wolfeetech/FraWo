#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

def check_all_failed():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[('state', '=', 'exception')]],
        {'fields': ['subject', 'email_to', 'email_from', 'reply_to', 'state', 'failure_reason'], 'limit': 10, 'order': 'id desc'}
    )
    
    for m in mails:
        print(f"To: {m.get('email_to')}")
        print(f"Subj: {m.get('subject')}")
        print(f"From: {m.get('email_from')}")
        print(f"Reply: {m.get('reply_to')}")
        print(f"Reason: {m.get('failure_reason')}")
        print("-" * 30)

check_all_failed()

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
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

def check_latest_mails():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Prüfe die letzten 10 E-Mails...")
    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[]],
        {'fields': ['email_to', 'state', 'failure_reason', 'email_from', 'date'], 'limit': 10, 'order': 'id desc'}
    )
    for m in mails:
        print(f"[{m['date']}] To: {m.get('email_to')}")
        print(f"   From:  {m.get('email_from')}")
        print(f"   State: {m.get('state')}")
        if m.get('state') == 'exception':
            print(f"   Error: {m.get('failure_reason')}")
        print("-" * 40)

check_latest_mails()

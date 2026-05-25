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

def check_emails():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Checking Odoo mail queue for 'lh' and 'trommler'...")
    mails = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'mail.mail', 'search_read',
        [[]],
        {'fields': ['subject', 'email_to', 'recipient_ids', 'state', 'failure_reason', 'date'], 'order': 'id desc', 'limit': 100}
    )
    
    found = False
    for m in mails:
        to = str(m.get('email_to') or '')
        subj = str(m.get('subject') or '')
        # Simple match for lh / trommler
        if 'lh' in to.lower() or 'tromm' in to.lower() or 'tromm' in subj.lower() or 'lh' in subj.lower() or 'dobby' in subj.lower():
            found = True
            print(f"[{m['date']}] To: {to} (Partner IDs: {m.get('recipient_ids')})")
            print(f"  Subject: {subj}")
            print(f"  Status:  {m['state']}")
            if m.get('failure_reason'):
                print(f"  Reason:  {m['failure_reason']}")
            print("-" * 40)
            
    if not found:
        print("Keine passenden E-Mails (lh/trommler) in den letzten 100 ausgehenden Nachrichten gefunden.")

check_emails()

#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv
import time

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

def resend_unique():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Hole alle fehlerhaften E-Mails...")
    failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search_read', [[('state', '=', 'exception')]], {'fields': ['id', 'subject', 'body_html', 'email_to', 'email_from', 'reply_to', 'attachment_ids']})
    
    unique_emails = {}
    for m in failed_mails:
        to_addr = m.get('email_to')
        subj = m.get('subject')
        if not to_addr or not subj or to_addr == 'False':
            continue
            
        key = (to_addr.strip().lower(), subj.strip())
        if key not in unique_emails or m['id'] > unique_emails[key]['id']:
            unique_emails[key] = m

    print(f"\nGefunden: {len(unique_emails)} EINZIGARTIGE E-Mails, die versendet werden muessen:")
    
    for key, m in unique_emails.items():
        print(f"[*] Sende an: {key[0]} | Betreff: '{key[1]}'")
        new_mail_data = {
            'subject': m['subject'],
            'body_html': m['body_html'],
            'email_to': m['email_to'],
            'email_from': 'webmaster@frawo-tech.de',
            'reply_to': m.get('reply_to'),
            'attachment_ids': [(6, 0, m.get('attachment_ids', []))]
        }
        
        new_mail_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'create', [new_mail_data])
        try:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[new_mail_id]])
            print("  -> ERFOLG!")
        except Exception as e:
            # TypeError with allow_none is fine and means sent
            if 'allow_none' in str(e):
                print("  -> ERFOLG (via XML-RPC None-Return)")
            else:
                print(f"  -> FEHLER: {e}")
        time.sleep(1) # Kleine Pause fuer den SMTP

    # Cancel old failed mails so they aren't retried
    old_ids = [m['id'] for m in failed_mails]
    if old_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'write', [old_ids, {'state': 'cancel'}])
        print(f"\n[OK] {len(old_ids)} alte Fehler-Mails wurden endgueltig auf 'Abgebrochen' gesetzt.")

resend_unique()

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

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

def test_fresh_email():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Erstelle neue Test-E-Mail in Odoo...")
    mail_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'create', [{
        'subject': 'FraWo Odoo DMARC Test - Erfolgreich!',
        'body_html': '<p>Hallo Wolf,</p><p>wenn du diese E-Mail liest, hat Odoo den SMTP-Server von Strato erfolgreich ueberzeugt. Der Bounce-Fix hat funktioniert!</p>',
        'email_to': 'wolf@frawo-tech.de',
        'email_from': 'webmaster@frawo-tech.de',
    }])
    
    print(f"E-Mail erstellt mit ID: {mail_id}")
    print("Versende E-Mail...")
    try:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[mail_id]])
    except Exception as e:
        print(f"Send command exception (often happens even if sent due to None return): {e}")
        
    time.sleep(2)
    
    # Check status
    m = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[mail_id]], {'fields': ['state', 'failure_reason']})[0]
    print(f"\nFinaler Status: {m['state']}")
    if m['state'] == 'exception':
        print(f"Fehler: {m['failure_reason']}")

test_fresh_email()

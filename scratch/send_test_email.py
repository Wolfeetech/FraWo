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

def send_test_mail():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Erstelle Test-Email...")
    mail_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'create', [{
        'subject': 'FraWo GbR - Odoo SMTP Test (Final)',
        'body_html': '<p>Hallo Wolf,</p><p>Das ist ein Live-Test direkt aus Odoo, um zu pruefen, ob der SMTP-Absender jetzt sauber als webmaster@frawo-tech.de durchgeht.</p><p>Viele Gruesse,<br/>Dein FraWo Agent</p>',
        'email_to': 'wwolfitec@gmail.com',
        'email_from': 'webmaster@frawo-tech.de',
        'auto_delete': False,
    }])
    print(f"Mail ID {mail_id} erstellt. Sende nun...")
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [[mail_id]])
    print("[OK] Senden abeschlossen.")
    
    # Prüfe den Status direkt danach
    state = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'read', [[mail_id]], {'fields': ['state', 'failure_reason']})
    print(f"Status nach Senden: {state[0]['state']}, Fehler (falls vorhanden): {state[0].get('failure_reason')}")

send_test_mail()

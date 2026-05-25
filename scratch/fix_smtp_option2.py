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

def fix_and_retry_emails():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("1. Deaktiviere Odoo Bounce-Aliasse (+-Adressierung)...")
    param_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', 'in', ['mail.bounce.alias', 'mail.catchall.alias'])]])
    if param_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'unlink', [param_ids])
        print(f"[OK] {len(param_ids)} Alias-Parameter geloescht.")
    else:
        print("[OK] Alias-Parameter waren bereits geloescht.")

    print("2. Stelle sicher, dass mail.force.smtp.from auf webmaster@frawo-tech.de steht...")
    force_param = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', '=', 'mail.force.smtp.from')]])
    if not force_param:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'create', [{'key': 'mail.force.smtp.from', 'value': 'webmaster@frawo-tech.de'}])

    print("3. Suche gescheiterte E-Mails (Exception)...")
    failed_mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search', [[('state', '=', 'exception')]])
    if failed_mails:
        print(f"[{len(failed_mails)}] gescheiterte E-Mails gefunden. Versuche erneuten Versand...")
        try:
            # Resend using send method
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'send', [failed_mails])
            print("[OK] E-Mails wurden an den SMTP-Server übergeben!")
        except Exception as e:
            print(f"[FEHLER] Beim Senden aufgetreten: {e}")
            
    print("4. Ueberpruefe aktuellen Status...")
    still_failed = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search_read', [[('id', 'in', failed_mails)]], {'fields': ['email_to', 'state', 'failure_reason']})
    for m in still_failed:
        print(f"To: {m.get('email_to')} -> State: {m.get('state')}")
        if m.get('state') == 'exception':
            print(f"   Reason: {m.get('failure_reason')}")

fix_and_retry_emails()

import xmlrpc.client
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print("--- MAIL CHECK (Trommlerzug) ---")
# Query mail.mail for trommlerzug
try:
    mails = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'mail.mail', 'search_read', 
        [[
            '|', '|', 
            ('email_to', 'ilike', 'trommlerzug'), 
            ('subject', 'ilike', 'trommlerzug'), 
            ('body_html', 'ilike', 'trommlerzug')
        ]], 
        {'fields': ['subject', 'email_to', 'state', 'date', 'failure_reason']}
    )

    if not mails:
        print("Keine E-Mail mit 'trommlerzug' gefunden in mail.mail.")
    else:
        for m in mails:
            print(f"Datum: {m.get('date')} | An: {m.get('email_to')} | Betreff: {m.get('subject')} | Status: {m.get('state')} | Fehler: {m.get('failure_reason')}")
except Exception as e:
    print(f"Fehler bei mail.mail: {e}")

print("\n--- IBAN FETCH (Wolf) ---")
# Query res.partner for Wolf
wolf_partner = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner', 'search_read', [[('email', '=', 'wolf@frawo-tech.de')]], {'fields': ['id', 'name']})
if wolf_partner:
    wolf_id = wolf_partner[0]['id']
    banks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.partner.bank', 'search_read', [[('partner_id', '=', wolf_id)]], {'fields': ['acc_number']})
    if banks:
        print(f"Wolfs IBAN gefunden: {banks[0]['acc_number']}")
        
        # Update Company Footer
        company = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'search_read', [[]], {'limit': 1, 'fields': ['report_footer']})[0]
        old_footer = company.get('report_footer', '')
        # Replace the dummy IBAN with the real one
        if 'DE99 9999 9999 9999 9999 99' in old_footer:
            new_footer = old_footer.replace('DE99 9999 9999 9999 9999 99', banks[0]['acc_number'])
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'write', [[company['id']], {'report_footer': new_footer}])
            print("Company footer updated with Wolf's IBAN.")
    else:
        print("Keine Bankverbindung bei Wolf gefunden.")

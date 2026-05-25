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

def check_and_fix_company():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Prüfe Company Settings (ID 1)...")
    fields = ['name', 'email', 'catchall_email', 'bounce_email', 'catchall_formatted', 'bounce_formatted']
    company = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'read', [[1]], {'fields': fields})
    
    if company:
        c = company[0]
        print("Gefundene Werte:")
        for f in fields:
            print(f" - {f}: {c.get(f)}")
            
        print("\nKorrigiere Werte auf webmaster@frawo-tech.de...")
        # Update company fields directly if they exist
        update_data = {}
        if 'catchall_email' in c: update_data['catchall_email'] = 'webmaster@frawo-tech.de'
        if 'bounce_email' in c: update_data['bounce_email'] = 'webmaster@frawo-tech.de'
        
        if update_data:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'write', [[1], update_data])
            print(f"[OK] Company Settings korrigiert: {update_data}")
        else:
            print("Felder nicht vorhanden.")
            
check_and_fix_company()

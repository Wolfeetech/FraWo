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
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

def setup_option_a_and_mail():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("1. Setze mail.default.from hart auf webmaster...")
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'set_param', ['mail.default.from', 'webmaster@frawo-tech.de'])
    print("[OK] mail.default.from ist gesetzt.")

    print("\n2. Richte Option A fuer Service-Produkte ein (task_in_project)...")
    products = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.template', 'search_read', [[('detailed_type', '=', 'service')]], {'fields': ['id', 'name', 'service_tracking']})
    updated_count = 0
    for p in products:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'product.template', 'write', [[p['id']], {'service_tracking': 'task_in_project'}])
        print(f" -> Produkt '{p['name']}' konfiguriert.")
        updated_count += 1
    
    print(f"\n[OK] {updated_count} Dienstleistungs-Produkte erzeugen nun ein neues Projekt bei Auftragserteilung!")

setup_option_a_and_mail()

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

def get_company_info():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Hole Firmendaten für das Impressum...")
    company = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'res.company', 'read', [[1]], {'fields': ['name', 'street', 'zip', 'city', 'country_id', 'vat', 'email', 'phone', 'website']})
    
    if company:
        c = company[0]
        print(f"Name: {c.get('name')}")
        print(f"Straße: {c.get('street')}")
        print(f"PLZ Ort: {c.get('zip')} {c.get('city')}")
        print(f"Email: {c.get('email')}")
        print(f"Telefon: {c.get('phone')}")
        print(f"Website: {c.get('website')}")
        print(f"USt-ID: {c.get('vat')}")

get_company_info()

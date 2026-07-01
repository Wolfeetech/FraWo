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

def query_odoo():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    apps = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.module.module', 'search_read', [[('state', '=', 'installed')]], {'fields': ['name', 'shortdesc']})
    print("Installed Apps (CRM/Sales/Invoicing):")
    for a in apps:
        if a['name'] in ['crm', 'sale_management', 'account', 'portal', 'website_sale', 'project']:
            print(f"- {a['name']}: {a['shortdesc']}")

    stages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.stage', 'search_read', [[]], {'fields': ['name', 'sequence']})
    print("\nCRM Stages:")
    for s in sorted(stages, key=lambda x: x['sequence']):
        print(f"{s['sequence']}: {s['name']}")

    try:
        payment_providers = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'payment.provider', 'search_read', [[('state', 'in', ['enabled', 'test'])]], {'fields': ['name', 'state']})
        print("\nEnabled Payment Providers:")
        for p in payment_providers:
            print(f"- {p['name']} ({p['state']})")
    except:
        pass

query_odoo()

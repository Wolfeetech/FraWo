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

def get_lead():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    leads = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'crm.lead', 'read', [[7]], {'fields': ['name', 'contact_name', 'email_from', 'phone', 'description', 'stage_id']})
    if leads:
        l = leads[0]
        print(f"Lead: {l.get('name')}")
        print(f"Kontakt: {l.get('contact_name')} ({l.get('email_from')})")
        print(f"Telefon: {l.get('phone')}")
        print(f"Stage: {l.get('stage_id')[1] if l.get('stage_id') else 'Keine'}")
        print(f"Beschreibung:\n{l.get('description')}")
    else:
        print('Lead nicht gefunden!')

get_lead()

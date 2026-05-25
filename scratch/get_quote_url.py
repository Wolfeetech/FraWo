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

def get_quote():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    quotes = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'sale.order', 'search_read', [[('name', '=', 'S00010')]], {'fields': ['name', 'state', 'access_url', 'access_token', 'partner_id']})
    if quotes:
        q = quotes[0]
        print(f"Angebot: {q['name']}")
        print(f"Status: {q['state']}")
        print(f"Portal URL (intern): {ODOO_URL}{q.get('access_url')}?access_token={q.get('access_token', '')}")
        print(f"Portal URL (public): https://www.frawo-tech.de{q.get('access_url')}?access_token={q.get('access_token', '')}")
    else:
        print('Angebot S00010 nicht gefunden!')

get_quote()

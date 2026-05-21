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

def test_smtp():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    servers = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search_read', [[]], {'fields': ['id', 'name']})
    for s in servers:
        print(f"Testing Server: {s['name']} (ID: {s['id']})")
        try:
            res = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'test_smtp_connection', [s['id']])
            print(f"[OK] Connection test returned: {res}")
        except Exception as e:
            print(f"[FAIL] Error: {e}")

test_smtp()

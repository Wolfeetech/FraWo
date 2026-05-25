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

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

servers = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.mail_server', 'search_read', [[]], {'fields': ['name', 'smtp_user', 'smtp_host', 'sequence', 'active']})
print('SMTP Servers:')
for s in servers:
    print(f"- {s['name']}: User={s['smtp_user']} Host={s['smtp_host']} Active={s['active']}")

params = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search_read', [[('key', 'ilike', 'mail')]], {'fields': ['key', 'value']})
print('\nMail Parameters:')
for p in params:
    print(f"- {p['key']}: {p['value']}")

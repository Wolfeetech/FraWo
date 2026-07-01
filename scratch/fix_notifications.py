#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv
import time

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

def fix_notifications():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Delete catchall domain to prevent Odoo from synthesizing notifications@domain
    print("Suche nach catchall domain Parametern...")
    param_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'search', [[('key', 'in', ['mail.catchall.domain', 'mail.bounce.domain'])]])
    if param_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.config_parameter', 'unlink', [param_ids])
        print(f"[OK] {len(param_ids)} Catchall-Domain-Parameter geloescht.")
        
fix_notifications()

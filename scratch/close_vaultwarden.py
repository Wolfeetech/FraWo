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

def close_vaultwarden():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    done_stage = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search', [[('name', 'ilike', 'Erledigt')]])
    if not done_stage:
        return
    done_stage_id = done_stage[0]

    tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('name', 'ilike', 'Vaultwarden')]], {'fields': ['id', 'name']})
    for t in tasks:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'message_post', [t['id']], {'body': 'Vaultwarden wurde erfolgreich über Cloudflare Tunnel (https://vault.frawo-tech.de) angebunden und ist betriebsbereit.'})
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[t['id']], {'stage_id': done_stage_id, 'state': '1_done'}])
        print(f"[✅ CLOSED] {t['name']}")

close_vaultwarden()

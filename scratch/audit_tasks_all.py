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

def list_all_tasks():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    masterplan = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search', [[('name', 'ilike', 'Masterplan')]])
    
    tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [
        [('project_id', '=', masterplan[0])]
    ], {'fields': ['id', 'name', 'stage_id'], 'limit': 30, 'order': 'id desc'})

    for t in tasks:
        stage = t['stage_id'][1] if t.get('stage_id') else 'Neu'
        if 'Erledigt' not in stage and 'Done' not in stage and 'Abgebrochen' not in stage:
            print(f"[{t['id']}] {t['name']} (Stage: {stage})")

list_all_tasks()

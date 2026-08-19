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

def check_project():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Suche nach Projekten, die mit S00010 verknuepft sind...")
    projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('name', 'ilike', 'S00010')]], {'fields': ['id', 'name', 'task_count']})
    
    if projects:
        p = projects[0]
        print(f"\n[BINGO] Projekt automatisch erstellt: '{p['name']}'")
        print(f"        Enthaelt {p.get('task_count', 0)} Tasks.")
        
        tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('project_id', '=', p['id'])]], {'fields': ['name', 'stage_id']})
        for t in tasks:
            stage = t['stage_id'][1] if t.get('stage_id') else 'Neu'
            print(f"        -> Task: {t['name']} (Status: {stage})")
    else:
        print("\n[FEHLER] Kein Projekt fuer S00010 gefunden!")

check_project()

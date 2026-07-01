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

def list_projects_and_tasks():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search_read', [[('active', '=', True)]], {'fields': ['id', 'name', 'task_count']})
    print("=== AKTIVE PROJEKTE ===")
    for p in projects:
        print(f"[{p['id']}] {p['name']} (Offene/Gesamte Tasks: {p.get('task_count', 0)})")

    # Zeige detaillierten Stand des Masterplans (ID 21, falls existent)
    masterplan = next((p for p in projects if 'Masterplan' in p['name']), None)
    if masterplan:
        print(f"\n=== TASKS IM {masterplan['name'].upper()} ===")
        stages = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search_read', [[]], {'fields': ['id', 'name']})
        stage_map = {s['id']: s['name'] for s in stages}
        
        tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('project_id', '=', masterplan['id'])]], {'fields': ['name', 'stage_id', 'is_closed']})
        
        # Gruppieren nach Stage
        grouped = {}
        for t in tasks:
            stage_name = t['stage_id'][1] if t.get('stage_id') else 'Ohne Status'
            if stage_name not in grouped:
                grouped[stage_name] = []
            grouped[stage_name].append(t)
            
        for s_name, t_list in grouped.items():
            print(f"\n--- Stage: {s_name} ({len(t_list)} Tasks) ---")
            for t in t_list[:5]: # Zeige max 5 als Preview
                status = "[CLOSED]" if t.get('is_closed') else "[OPEN]"
                print(f"  - {status} {t['name']}")
            if len(t_list) > 5:
                print(f"  - ... und {len(t_list)-5} weitere")

list_projects_and_tasks()

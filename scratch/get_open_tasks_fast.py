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

def list_tasks():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    stages = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task.type', 'search_read',
        [[['name', 'ilike', 'Erledigt']]],
        {'fields': ['id', 'name']}
    )
    done_stage_id = stages[0]['id']

    projects = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.project', 'search', [[['name', 'ilike', 'Masterplan']]])
    master_project_id = projects[0]

    tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task', 'search_read',
        [[('project_id', '=', master_project_id), ('stage_id', '!=', done_stage_id)]],
        {'fields': ['id', 'name', 'stage_id']}
    )
    
    for t in tasks:
        print(f"{t['id']}: {t['name']}")

list_tasks()

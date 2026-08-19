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

def close_tasks(task_ids):
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

    # Read tasks to log their names
    tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task', 'search_read',
        [[('id', 'in', task_ids)]],
        {'fields': ['id', 'name']}
    )
    for t in tasks:
        print(f"Schliesse: {t['id']} - {t['name']}")

    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task', 'write',
        [task_ids, {'stage_id': done_stage_id}]
    )
    print("Fertig!")

close_tasks([198, 128, 177, 80])

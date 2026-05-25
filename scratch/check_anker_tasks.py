#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

def get_anker_tasks():
    print("[*] Connecting to Odoo...")
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        return 1

    if not uid:
        print("[FAIL] Authentication failed!")
        return 1

    print(f"[OK] Auth OK (UID: {uid})")
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Find the Masterplan project ID
    project_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.project', 'search',
        [[['name', 'ilike', 'Masterplan']]]
    )
    
    if not project_ids:
        print("[FAIL] Masterplan project not found!")
        return 1
        
    master_project_id = project_ids[0]

    # Find tag 'Anker Lounge'
    tag_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.tags', 'search',
        [[['name', 'ilike', 'Anker']]]
    )
    
    print(f"[*] Found tag IDs matching 'Anker': {tag_ids}")
    
    domain = [
        ['project_id', '=', master_project_id]
    ]
    if tag_ids:
        domain.append('|')
        domain.append(['tag_ids', 'in', tag_ids])
        domain.append(['name', 'ilike', 'Anker'])
    else:
        domain.append(['name', 'ilike', 'Anker'])

    # Retrieve all matching tasks
    tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'stage_id', 'user_ids', 'tag_ids', 'description']}
    )
    
    print(f"\n[OK] Found {len(tasks)} tasks relating to 'Anker':")
    for i, t in enumerate(tasks, 1):
        stage_name = t['stage_id'][1] if t['stage_id'] else "None"
        assignees = t['user_ids'] if 'user_ids' in t else []
        print(f"--- Task #{t['id']} ---")
        print(f"Name: {t['name']}")
        print(f"Stage: {stage_name}")
        print(f"Assignees: {assignees}")
        print(f"Description: {t['description'][:200] if t['description'] else 'No description'}")
        print()
        
    return 0

if __name__ == "__main__":
    exit(get_anker_tasks())

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

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

def search_anker():
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

    # Search all projects (both active and inactive) containing 'Anker'
    projects = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.project', 'search_read',
        [[['name', 'ilike', 'Anker'], ['active', 'in', [True, False]]]],
        {'fields': ['id', 'name', 'active']}
    )
    
    print(f"\n[OK] Found {len(projects)} projects containing 'Anker':")
    project_ids = []
    for p in projects:
        print(f"  - ID: {p['id']} | Name: {p['name']} | Active: {p['active']}")
        project_ids.append(p['id'])

    # Find tasks in these projects OR tasks with Tag 'Anker Lounge' OR tasks containing 'Anker'
    # First search for tag
    tag_ids = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.tags', 'search',
        [[['name', 'ilike', 'Anker']]]
    )
    
    # Build flat Odoo search domain
    domain = [
        ['active', 'in', [True, False]],
        '|', '|',
        ['name', 'ilike', 'Anker']
    ]
    if project_ids:
        domain.append(['project_id', 'in', project_ids])
    else:
        domain.append(['id', '=', -1])
        
    if tag_ids:
        domain.append(['tag_ids', 'in', tag_ids])
    else:
        domain.append(['id', '=', -1])

    # Let's search all tasks (both active and archived)
    tasks = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'project.task', 'search_read',
        [domain],
        {'fields': ['id', 'name', 'project_id', 'stage_id', 'tag_ids', 'description', 'active']}
    )
    
    print(f"\n[OK] Found {len(tasks)} tasks relating to 'Anker' (including archived):")
    for i, t in enumerate(tasks, 1):
        proj_name = t['project_id'][1] if t['project_id'] else "None"
        stage_name = t['stage_id'][1] if t['stage_id'] else "None"
        print(f"  {i}. [Task #{t['id']}] {t['name']}")
        print(f"     Project: {proj_name} | Stage: {stage_name} | Active: {t['active']}")
        desc_snippet = t['description'][:150] if t['description'] else 'No description'
        # Strip HTML for readability
        import re
        clean_desc = re.sub('<[^<]+?>', '', desc_snippet).strip()
        print(f"     Description: {clean_desc[:120]}")
        print()

    return 0

if __name__ == "__main__":
    exit(search_anker())

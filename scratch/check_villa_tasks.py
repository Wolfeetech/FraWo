#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def check_villa():
    print("[*] Connecting to Odoo...")
    session = connect(default_user="wolf@frawo-tech.de", prompt_for_username=False)
    
    # Search for tag 'Villa Bienert'
    tag_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.tags', 'search',
        [[['name', '=', 'Villa Bienert']]]
    )
    
    if not tag_ids:
        print("[FAIL] Tag 'Villa Bienert' not found in Odoo!")
        return 1
        
    tag_id = tag_ids[0]
    print(f"[OK] Found Tag 'Villa Bienert' (ID: {tag_id})")
    
    # Search tasks with this tag
    tasks = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'search_read',
        [[['tag_ids', 'in', [tag_id]]]],
        {'fields': ['id', 'name', 'stage_id', 'user_ids']}
    )
    
    print(f"\n[OK] Found {len(tasks)} tasks tagged with 'Villa Bienert':")
    for i, t in enumerate(tasks, 1):
        stage_name = t['stage_id'][1] if t['stage_id'] else "None"
        user_names = [u for u in t['user_ids']] if 'user_ids' in t else []
        print(f"  {i}. [Task #{t['id']}] {t['name']} | Stage: {stage_name}")
        
    return 0

if __name__ == "__main__":
    exit(check_villa())

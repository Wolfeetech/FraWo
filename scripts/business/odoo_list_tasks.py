import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    print("Verbinde mit Odoo...")
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    print("Hole Projekte...")
    projects = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search_read', [[]], {'fields': ['id', 'name']})
    
    print("\nHole Aufgaben (Tasks)...")
    tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search_read', [[]], {'fields': ['id', 'name', 'project_id', 'stage_id', 'user_ids']})
    
    print(f"\nGefundene Aufgaben: {len(tasks)}")
    
    for task in tasks:
        p_name = task['project_id'][1] if task['project_id'] else "Kein Projekt"
        s_name = task['stage_id'][1] if task['stage_id'] else "Keine Stage"
        users = []
        if 'user_ids' in task and task['user_ids']:
            # In Odoo user_ids is often a list of IDs or a many2many structure
            # Let's just print the raw value or handle it if it's a list of tuples
            users = task['user_ids']
        print(f"[{p_name}] -> [{s_name}] Task #{task['id']}: {task['name']} (Users: {users})")

if __name__ == "__main__":
    main()

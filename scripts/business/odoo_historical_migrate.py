import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
TARGET_DB = "FraWo_GbR"
SOURCE_DBS = ["Recovery_DB", "FraWo_Live"]
ODOO_USER = "admin"
ODOO_PASS = "admin"

def historical_migrate():
    print(f"Starting Historical Task Migration to {TARGET_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    
    # 1. Connect to Target and find Wolf ID
    try:
        target_session = connect(url=ODOO_URL, db=TARGET_DB, default_user=ODOO_USER)
        wolf_ids = target_session.models.execute_kw(TARGET_DB, target_session.uid, ODOO_PASS, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
        wolf_id = wolf_ids[0] if wolf_ids else 6 # Target confirmed ID
    except Exception as e:
        print(f"Failed to connect to target {TARGET_DB}: {e}")
        return

    # 2. Extract Tasks from Sources
    all_source_tasks = []
    for s_db in SOURCE_DBS:
        print(f" -> Scraping tasks from {s_db}...")
        try:
            s_session = connect(url=ODOO_URL, db=s_db, default_user=ODOO_USER)
            t_ids = s_session.models.execute_kw(s_db, s_session.uid, ODOO_PASS, 'project.task', 'search', [[]])
            if t_ids:
                ts = s_session.models.execute_kw(s_db, s_session.uid, ODOO_PASS, 'project.task', 'read', [t_ids, ['name', 'description', 'active']])
                all_source_tasks.extend(ts)
        except Exception as e:
            print(f"    SKIPPED {s_db}: {e}")

    print(f"Total source tasks found: {len(all_source_tasks)}")

    # 3. Inject unique tasks into Target
    existing_names = target_session.models.execute_kw(TARGET_DB, target_session.uid, ODOO_PASS, 'project.task', 'search_read', [[]], {'fields': ['name']})
    existing_name_set = {t['name'] for t in existing_names}

    injected_count = 0
    for task in all_source_tasks:
        if task['name'] not in existing_name_set:
            new_task = {
                'name': task['name'],
                'description': task['description'],
                'user_ids': [(4, wolf_id)],
                'active': True
            }
            target_session.models.execute_kw(TARGET_DB, target_session.uid, ODOO_PASS, 'project.task', 'create', [new_task])
            existing_name_set.add(task['name'])
            injected_count += 1

    print(f"SUCCESS: Injected {injected_count} new tasks into {TARGET_DB}.")

if __name__ == "__main__":
    historical_migrate()

import os
from odoo_rpc_client import connect

ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "admin"
ODOO_PASS = "admin"
TARGET_USER_ID = 2 # Assuming Wolf is the first non-admin user

def fix_visibility():
    print(f"Assigning ownership in {ODOO_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    # 1. Find Wolf ID
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    if not wolf_ids:
        print("Error: Could not find Wolf user.")
        return
    wolf_id = wolf_ids[0]

    # 2. Find Project
    p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', 'FraWo GbR - Heritage & History']]])
    if not p_ids:
        print("Error: Project not found.")
        return
    project_id = p_ids[0]

    # 3. Assign all tasks in this project to Wolf
    task_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[['project_id', '=', project_id]]])
    if task_ids:
        session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [task_ids, {'user_ids': [(4, wolf_id)]}])
        print(f"Assigned {len(task_ids)} tasks to Wolf (ID: {wolf_id}).")
    
    # 4. Make Wolf the manager of the project
    session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[project_id], {'user_id': wolf_id}])
    print(f"Project visibility fixed for Wolf.")

if __name__ == "__main__":
    fix_visibility()

import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "admin"
ODOO_PASS = "admin"

MAP = {
    "Heritage & Founding": ["Gründung", "Notar", "Heritage"],
    "Website & Public Edge": ["Website", "Cloudflare", "Caddy", "Lane B"],
    "Security & PBS": ["PBS", "Vaultwarden", "Sicherheit", "Lane C"],
    "Stockenweiler Migration": ["Stockenweiler", "Remote", "Lane D"],
    "FraWo Homeserver 2027": ["Homeserver", "Infrastruktur"]
}

def surgical_remap():
    print(f"Starting Final Surgical Remap in {ODOO_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    wolf_id = wolf_ids[0] if wolf_ids else None

    # 1. Ensure all projects exist as tiles
    project_ids = {}
    for p_name in MAP.keys():
        ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', p_name]]])
        if not ids:
            p_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{
                'name': p_name,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)] if wolf_id else [],
                'active': True
            }])
            print(f"Created Container: {p_name}")
        else:
            p_id = ids[0]
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[p_id], {
                'active': True,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)] if wolf_id else []
            }])
            print(f"Verified Container: {p_name}")
        project_ids[p_name] = p_id

    # 2. Re-distribute Tasks based on keywords/tags
    # Find all tasks tagged to the single project or orphans
    all_task_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[]])
    
    if all_task_ids:
        tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'read', [all_task_ids, ['name', 'project_id']])
        for t in tasks:
            for p_name, keywords in MAP.items():
                if any(k.lower() in t['name'].lower() for k in keywords):
                    new_pid = project_ids[p_name]
                    if t['project_id'] and t['project_id'][0] != new_pid:
                        session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [[t['id']], {'project_id': new_pid}])
                        print(f"Moved Task '{t['name']}' -> '{p_name}'")
                    break

    # 3. Cleanup: Archive the original Masterplan tile if empty
    master_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', '🚀 Homeserver 2027: Masterplan']]])
    if master_ids:
        session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [master_ids, {'active': False}])
        print("Archived the single-tile Masterplan to finalize visual cleanup.")

if __name__ == "__main__":
    surgical_remap()

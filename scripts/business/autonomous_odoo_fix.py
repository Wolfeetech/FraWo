import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "admin"
ODOO_PASS = "admin"

def autonomous_cleanup():
    print(f"Starting Autonomous SSOT Cleanup in {ODOO_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    # 1. Identify Wolf User
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    wolf_id = wolf_ids[0] if wolf_ids else None

    # 2. Archive Demo Projects
    demo_projects = ["Office Design", "Renovations", "Research & Development"]
    p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', 'in', demo_projects]]])
    if p_ids:
        session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [p_ids, {'active': False}])
        print(f"Archived {len(p_ids)} demo projects.")
    
    # 3. Pin 'Heritage' and 'Homeserver' as Favorites for Wolf
    target_projects = ["FraWo GbR - Heritage & History", "Homeserver 2027", "FraWo Homeserver 2027"]
    p_targets = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', 'in', target_projects]]])
    
    if p_targets and wolf_id:
        for pid in p_targets:
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[pid], {
                'favorite_user_ids': [(4, wolf_id)],
                'user_id': wolf_id,
                'active': True
            }])
        print(f"Pinned {len(p_targets)} target projects to user {wolf_id}.")

    # 4. Final Audit
    final_p = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search_read', [[['active', '=', True]]], ['name'])
    print(f"Final Active Projects: {[x['name'] for x in final_p]}")

if __name__ == "__main__":
    autonomous_cleanup()

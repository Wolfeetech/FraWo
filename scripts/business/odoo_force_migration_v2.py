import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "admin"
ODOO_PASS = "admin"

LANES = [
    "Lane A: Heritage & History",
    "Lane B: Website & Public Edge",
    "Lane C: Security & PBS",
    "Lane D: Stockenweiler Migration",
    "FraWo Homeserver 2027"
]

def force_orchestrate():
    print(f"Executing Global Odoo Force-Migration on {ODOO_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    # Identify Wolf
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    wolf_id = wolf_ids[0] if wolf_ids else 1

    # Archive the old single tile if it exists to clean the view
    old_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', '🚀 Homeserver 2027: Masterplan']]])
    if old_ids:
        session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [old_ids, {'active': False}])
        print("Archived the legacy Masterplan tile.")

    for lane in LANES:
        # Check if project exists (case insensitive or exact)
        p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', lane]]])
        
        if not p_ids:
            p_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{
                'name': lane,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)],
                'active': True
            }])
            print(f"CREATED: {lane} (ID: {p_id})")
        else:
            p_id = p_ids[0]
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[p_id], {
                'active': True,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)]
            }])
            print(f"VERIFIED/UPDATED: {lane} (ID: {p_id})")

    # Final Verification
    final_p = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search_count', [[['active', '=', True], ['user_id', '=', wolf_id]]])
    print(f"Final Count of Active Projects for Wolf: {final_p}")

if __name__ == "__main__":
    force_orchestrate()

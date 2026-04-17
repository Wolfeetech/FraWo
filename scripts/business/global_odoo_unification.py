import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_USER = "admin"
ODOO_PASS = "admin"

DB_LIST = ["FraWo_Live", "FraWo_GbR", "FraWo_GbR_Backup", "Recovery_DB"]

LANES = [
    "Lane A: Heritage & History",
    "Lane B: Website & Public Edge",
    "Lane C: Security & PBS",
    "Lane D: Stockenweiler Migration",
    "FraWo Homeserver 2027"
]

def global_unification():
    print(f"Starting Global DB Unification on {ODOO_URL}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    
    for db in DB_LIST:
        print(f"\n--- Unifying Database: {db} ---")
        try:
            session = connect(url=ODOO_URL, db=db, default_user=ODOO_USER)
            
            # Find Wolf in this DB
            wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
            wolf_id = wolf_ids[0] if wolf_ids else 1
            
            # Ensure Project Tile Visibility
            for lane in LANES:
                p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', lane]]])
                if not p_ids:
                    p_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{
                        'name': lane,
                        'user_id': wolf_id,
                        'favorite_user_ids': [(4, wolf_id)],
                        'active': True
                    }])
                    print(f"[{db}] CREATED: {lane}")
                else:
                    p_id = p_ids[0]
                    session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[p_id], {
                        'active': True,
                        'user_id': wolf_id,
                        'favorite_user_ids': [(4, wolf_id)]
                    }])
                    print(f"[{db}] VERIFIED: {lane}")
            
            # Archive JUNK
            junk = ["Office Design", "Renovations", "Research & Development", "🚀 Homeserver 2027: Masterplan"]
            junk_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', 'in', junk]]])
            if junk_ids:
                session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [junk_ids, {'active': False}])
                print(f"[{db}] ARCHIVED JUNK.")

        except Exception as e:
            print(f"[{db}] SKIPPED: {e}")

if __name__ == "__main__":
    global_unification()

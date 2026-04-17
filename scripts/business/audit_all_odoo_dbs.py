import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
DB_LIST = ["FraWo_Live", "FraWo_GbR_Backup", "Recovery_DB"]
ODOO_USER = "admin"
ODOO_PASS = "admin"

def audit_dbs():
    print(f"Starting Multi-DB Audit on {ODOO_URL}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    
    for db in DB_LIST:
        print(f"\n--- Checking Database: {db} ---")
        try:
            session = connect(url=ODOO_URL, db=db, default_user=ODOO_USER)
            
            # Count Projects
            p_count = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search_count', [[]])
            print(f"Project Count: {p_count}")
            
            if p_count > 0:
                projects = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search_read', [[], ['name', 'user_id']])
                for p in projects:
                    print(f" - Project: {p['name']} (Owner: {p['user_id']})")
                    
            # Count Tasks
            t_count = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search_count', [[]])
            print(f"Task Count: {t_count}")

            if t_count > 0:
                tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search_read', [[], ['name', 'project_id']], limit=5)
                for t in tasks:
                    print(f"   * Task: {t['name']} (Project: {t['project_id']})")

        except Exception as e:
            print(f"Error auditing {db}: {e}")

if __name__ == "__main__":
    audit_dbs()

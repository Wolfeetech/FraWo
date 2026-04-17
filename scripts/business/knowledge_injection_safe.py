import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "wolf@frawo-tech.de"
ODOO_PASS = "admin"  # Verified temporary password

# Historic Milestones extracted from Git Archives
HISTORIC_TASKS = [
    {"name": "GbR Gründungs-Entscheidung", "desc": "Initial decision to form FraWo GbR.", "date": "2026-03-15"},
    {"name": "Notar Termin Vorbereitung", "desc": "Drafting partnership agreement.", "date": "2026-03-20"},
    {"name": "Finanzamt Dokumentation", "desc": "Applying for tax ID and business registration.", "date": "2026-03-25"},
    {"name": "Infrastruktur-Audit 2026", "desc": "First baseline of Anker and Stockenweiler nodes.", "date": "2026-04-01"},
    {"name": "Masterplan Lane A Abschluss", "desc": "First internal MVP release gate.", "date": "2026-04-09"}
]

def safe_restore():
    print(f"Connecting to {ODOO_DB} for Heritage Restoration...")
    # Injecting password into environment as expected by connect()
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    # 1. Ensure Project Exists
    project_name = "FraWo GbR - Heritage & History"
    p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', project_name]]])
    
    if not p_ids:
        project_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{'name': project_name, 'description': 'Zentrales Archiv der Gründungsphasen der FraWo GbR (restored 2026-04-17)'}])
        print(f"Created Project: {project_name}")
    else:
        project_id = p_ids[0]
        print(f"Project {project_name} exists.")

    # 2. Inject Tasks Safely
    for t in HISTORIC_TASKS:
        t_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[['name', '=', t['name']], ['project_id', '=', project_id]]])
        if not t_ids:
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'create', [{
                'project_id': project_id,
                'name': t['name'],
                'description': t['desc'],
                'active': True
            }])
            print(f"Restored Task: {t['name']}")
        else:
            print(f"Task {t['name']} already exists. Skipping.")

if __name__ == "__main__":
    safe_restore()

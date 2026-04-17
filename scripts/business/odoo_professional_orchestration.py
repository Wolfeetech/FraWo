import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_Live"
ODOO_USER = "admin"
ODOO_PASS = "admin"

# High-Value Orchestration Map
PROJECT_MAP = {
    "Lane A: MVP Closeout": [
        {"name": "GbR Gründung - Historie", "desc": "Zertifizierung der GbR Gründungsphase 2026."},
        {"name": "Infrastruktur Thaw 2026-04-17", "desc": "Wiederherstellung nach Anker-Host-Freeze."}
    ],
    "Lane B: Website & Public Edge": [
        {"name": "Cloudflare Tunnel Deployment", "desc": "Implementierung eines permanenten Tunnels für www.frawo-tech.de."},
        {"name": "Caddy Reverse Proxy Config", "desc": "Absicherung des Ingress-Pfads auf VM 220."}
    ],
    "Lane C: Security & PBS": [
        {"name": "PBS Backups produktiv", "desc": "Einrichtung und Test der Snapshot-Replikation auf VM 240."},
        {"name": "Vaultwarden Sync", "desc": "Abgleich der Passwörter und Secrets."}
    ],
    "Lane D: Stockenweiler Migration": [
        {"name": "Remote Support Bridge", "desc": "Tailscale-only Zugriff auf die Stockenweiler Nodes."},
        {"name": "PBS Offsite", "desc": "Sicherstellung der Backup-Replikation nach Stockenweiler."}
    ],
    "FraWo Homeserver 2027": [
        {"name": "Dual-Node Architektur Final", "desc": "Konsolidierung Anker (Business/AI) und Stockenweiler (Media/Backup)."}
    ]
}

def orchestrate():
    print(f"Starting Professional Odoo Orchestration on {ODOO_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    # Identify Wolf
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    wolf_id = wolf_ids[0] if wolf_ids else None

    for p_name, tasks in PROJECT_MAP.items():
        # 1. Create/Find Project
        p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', p_name]]])
        if not p_ids:
            p_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{
                'name': p_name, 
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)] if wolf_id else [],
                'active': True
            }])
            print(f"Created Project Cluster: {p_name}")
        else:
            p_id = p_ids[0]
            # Ensure visible
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'write', [[p_id], {
                'active': True,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)] if wolf_id else []
            }])
            print(f"Project Cluster exists: {p_name} (Updating visibility)")

        # 2. Inject Sub-Tasks
        for t in tasks:
            t_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[['name', '=', t['name']], ['project_id', '=', p_id]]])
            if not t_ids:
                session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'create', [{
                    'project_id': p_id,
                    'name': t['name'],
                    'description': t['desc'],
                    'user_ids': [(4, wolf_id)] if wolf_id else [],
                    'active': True
                }])
                print(f"  + Orchestrated Task: {t['name']}")
            else:
                print(f"  - Task {t['name']} already orchestrated.")

    print("\nOrchestration Complete. Dashboard is now professionals and ready.")

if __name__ == "__main__":
    orchestrate()

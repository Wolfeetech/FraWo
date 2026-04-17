import os
from odoo_rpc_client import connect

# Configuration
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_GbR"
ODOO_USER = "admin"
ODOO_PASS = "admin"

LANES_MAP = {
    "Lane A: Heritage & History": ["Heritage", "Gründung", "Notar", "GbR", "Historie"],
    "Lane B: Website & Public Edge": ["Website", "Cloudflare", "Caddy", "Ingress", "Public", "Domain"],
    "Lane C: Security & PBS": ["Security", "PBS", "Backup", "Vaultwarden", "Safe", "Sicherheit", "Backup"],
    "Lane D: Stockenweiler Migration": ["Stockenweiler", "Remote", "Bridge", "Hardware", "Migration"],
    "FraWo Homeserver 2027": ["Homeserver", "Infrastructure", "Anker", "Tailscale", "QDevice", "WSL", "Node", "PVE"]
}

def total_mission_restore():
    print(f"Starting Total Mission Restoration on {ODOO_DB}...")
    os.environ["ODOO_RPC_PASSWORD"] = ODOO_PASS
    session = connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER)
    
    # Identify Wolf
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    wolf_id = wolf_ids[0] if wolf_ids else 1

    # 1. Map Lane Names to IDs in this DB
    lane_ids = {}
    for lane_name in LANES_MAP.keys():
        p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', lane_name]]])
        if p_ids:
            lane_ids[lane_name] = p_ids[0]
        else:
            # Create if missing
            p_id = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{
                'name': lane_name,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)],
                'active': True
            }])
            lane_ids[lane_name] = p_id
            print(f"Restored Lane Container: {lane_name}")

    # 2. Find ALL tasks (including orphans/archived)
    # Clear filter to find everything
    all_task_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[]])
    
    if all_task_ids:
        tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'read', [all_task_ids, ['name', 'project_id', 'active']])
        print(f"Found {len(tasks)} tasks in database archaeology...")
        
        for t in tasks:
            # Determine correct lane based on keywords
            target_lane_id = None
            for lane_name, keywords in LANES_MAP.items():
                if any(k.lower() in t['name'].lower() for k in keywords):
                    target_lane_id = lane_ids[lane_name]
                    break
            
            # If no keyword match, default to General Homeserver Lane
            if not target_lane_id:
                target_lane_id = lane_ids["FraWo Homeserver 2027"]

            # Perform surgical relink
            update_data = {
                'project_id': target_lane_id,
                'user_ids': [(4, wolf_id)], # Assign to Wolf
                'active': True # Unarchive
            }
            
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [[t['id']], update_data])
            print(f" -> Restored Task: '{t['name']}' into '{target_lane_id}'")

    print("\nMission Restoration Complete. All historical data is now in your 5-lane cockpit.")

if __name__ == "__main__":
    total_mission_restore()

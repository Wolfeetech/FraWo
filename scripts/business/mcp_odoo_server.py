import json
import os
import sys
from odoo_rpc_client import connect

# Odoo Connection Configuration (SSOT)
# Using User ID 7 (Wolf) from previous audit
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = os.getenv("ODOO_RPC_DB", "FraWo_GbR")
ODOO_USER = "wolf@frawo-tech.de"
ODOO_PWD = "admin" # Sync established earlier

LANES_MAP = {
    "Lane A: Heritage & History": ["Heritage", "Gründung", "Notar", "GbR", "Historie", "Gründung"],
    "Lane B: Website & Public Edge": ["Website", "Cloudflare", "Caddy", "Ingress", "Public", "Domain", "Tunnel"],
    "Lane C: Security & PBS": ["Security", "PBS", "Backup", "Vaultwarden", "Safe", "Sicherheit", "Datensicherung"],
    "Lane D: Stockenweiler Migration": ["Stockenweiler", "Remote", "Bridge", "Hardware", "Migration", "Hardware"],
    "FraWo Homeserver 2027": ["Homeserver", "Infrastructure", "Anker", "Tailscale", "QDevice", "WSL", "Node", "PVE"]
}

def get_odoo_session():
    return connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER, secret_label="MCP Odoo Pro Secret")

def ensure_mission_lanes():
    """Ensure all 5 mission projects exist and are favorites for Wolf."""
    session = get_odoo_session()
    results = []
    for lane_name in LANES_MAP.keys():
        p_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'search', [[['name', '=', lane_name]]]
        )
        if not p_ids:
            p_id = session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.project', 'create', [{
                    'name': lane_name,
                    'user_id': session.uid,
                    'favorite_user_ids': [(4, session.uid)],
                    'active': True
                }]
            )
            results.append(f"Created Lane: {lane_name} (ID: {p_id})")
        else:
            session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.project', 'write', [p_ids, {
                    'active': True,
                    'favorite_user_ids': [(4, session.uid)]
                }]
            )
            results.append(f"Verified Lane: {lane_name}")
    return results

def activate_discount_feature():
    """Activate the 'Discount on lines' feature in the Odoo system."""
    session = get_odoo_session()
    # In Odoo 17, this is often done by adding the user to a specific group
    group_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'res.groups', 'search', [[['name', '=', 'Discount on lines']]]
    )
    if group_ids:
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            'res.groups', 'write', [group_ids, {'users': [(4, session.uid)]}]
        )
        return "Discount feature activated for Wolf."
    return "Error: Could not find Discount group."

def reclaim_archived_tasks():
    """Find all tasks and move them into the mission lanes based on keywords."""
    session = get_odoo_session()
    # Fetch all tasks (active and archived)
    task_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'search', [[('active', 'in', [True, False])]]
    )
    if not task_ids:
        return "No tasks found to reclaim."
    
    tasks = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'read', [task_ids, ['name', 'project_id']]
    )
    
    # Map project names to IDs
    project_rec = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search_read', [[]], {'fields': ['id', 'name']}
    )
    lane_ids = {p['name']: p['id'] for p in project_rec}
    
    updated = 0
    for t in tasks:
        target_lane = None
        for lane_name, keywords in LANES_MAP.items():
            if any(k.lower() in t['name'].lower() for k in keywords):
                target_lane = lane_ids.get(lane_name)
                break
        
        if target_lane:
            session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.task', 'write', [[t['id']], {
                    'project_id': target_lane,
                    'active': True,
                    'user_ids': [(4, session.uid)]
                }]
            )
            updated += 1
            
    return f"Successfully reclaimed and relinked {updated} tasks."

def main():
    if len(sys.argv) < 2:
        print("Usage: mcp_odoo_server.py [ensure_lanes|activate_discount|reclaim_tasks]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "ensure_lanes":
        print(json.dumps(ensure_mission_lanes(), indent=2))
    elif cmd == "activate_discount":
        print(activate_discount_feature())
    elif cmd == "reclaim_tasks":
        print(reclaim_archived_tasks())

if __name__ == "__main__":
    main()

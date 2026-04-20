import json
import os
import sys
from odoo_rpc_client import connect

# Odoo Connection Configuration (SSOT)
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = "FraWo_GbR"
ODOO_USER = "admin"
ODOO_PWD = "admin" # Synchronized across all silos

def get_odoo_session():
    # Force use of FraWo_GbR for the cockpit
    return connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER, secret_label="MCP Odoo Pro Secret")

def ensure_mission_lanes():
    """Create the 5 professional mission lanes if they don't exist."""
    session = get_odoo_session()
    lanes = [
        "Lane A: Heritage & History",
        "Lane B: Website & Public Edge",
        "Lane C: Security & PBS",
        "Lane D: Stockenweiler Migration",
        "FraWo Homeserver 2027"
    ]
    
    # Identify Wolf ID
    wolf_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', '=', 'wolf@frawo-tech.de']]])
    wolf_id = wolf_ids[0] if wolf_ids else session.uid

    created_ids = []
    for lane in lanes:
        p_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search', [[['name', '=', lane]]])
        if not p_ids:
            pid = session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'create', [{
                'name': lane,
                'user_id': wolf_id,
                'favorite_user_ids': [(4, wolf_id)],
                'active': True
            }])
            created_ids.append(pid)
    return f"Created {len(created_ids)} lanes. All 5 lanes now active."

def activate_discount_feature():
    """Enable the Discount feature on sales orders/invoices."""
    session = get_odoo_session()
    # In Odoo, features are often enabled by adding users to specific groups
    group_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.groups', 'search', [[['name', '=', 'Discount on lines']]])
    if group_ids:
        # Add admin and wolf to this group
        user_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', 'in', ['admin', 'wolf@frawo-tech.de']]]])
        session.models.execute_kw(session.db, session.uid, session.secret, 'res.groups', 'write', [group_ids, {'users': [(4, uid) for uid in user_ids]}])
        return "Discount feature activated for Admin and Wolf."
    return "Error: Discount group not found."

def reclaim_tasks():
    """Find all tasks and categorize them into mission lanes based on keywords."""
    session = get_odoo_session()
    lanes_map = {
        "Lane A: Heritage & History": ["Heritage", "Gründung", "Notar", "GbR", "Historie"],
        "Lane B: Website & Public Edge": ["Website", "Cloudflare", "Caddy", "Ingress", "Public", "Domain"],
        "Lane C: Security & PBS": ["Security", "PBS", "Backup", "Vaultwarden", "Safe", "Sicherheit"],
        "Lane D: Stockenweiler Migration": ["Stockenweiler", "Remote", "Bridge", "Hardware", "Migration"],
        "FraWo Homeserver 2027": ["Homeserver", "Infrastructure", "Anker", "Tailscale", "QDevice", "WSL", "Node", "PVE"]
    }
    
    # Map project names to IDs
    p_map = {p['name']: p['id'] for p in session.models.execute_kw(session.db, session.uid, session.secret, 'project.project', 'search_read', [[]], {'fields': ['id', 'name']})}
    
    # Get all tasks
    task_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[]])
    tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'read', [task_ids, ['name', 'project_id']])
    
    reclaimed = 0
    for t in tasks:
        target_pid = None
        for lane, keywords in lanes_map.items():
            if any(k.lower() in t['name'].lower() for k in keywords) and lane in p_map:
                target_pid = p_map[lane]
                break
        
        if target_pid and (not t['project_id'] or t['project_id'][0] != target_pid):
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [[t['id']], {'project_id': target_pid, 'active': True}])
            reclaimed += 1
            
    return f"Reclaimed {reclaimed} tasks into mission lanes."

def main():
    if len(sys.argv) < 2:
        print("Usage: mcp_odoo_pro_server.py [ensure_lanes|activate_discounts|reclaim_tasks]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "ensure_lanes":
        print(ensure_mission_lanes())
    elif cmd == "activate_discounts":
        print(activate_discount_feature())
    elif cmd == "reclaim_tasks":
        print(reclaim_tasks())

if __name__ == "__main__":
    main()

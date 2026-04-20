import os
import sys
from mcp.server.fastmcp import FastMCP
from odoo_rpc_client import connect

# Initialize FastMCP server
mcp = FastMCP("OdooPro", dependencies=["odoo-rpc-client"])

# Odoo Connection Configuration (SSOT)
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = os.getenv("ODOO_RPC_DB", "FraWo_GbR")
ODOO_USER = os.getenv("ODOO_RPC_USER", "admin")

def get_odoo_session():
    """Establish connection to Odoo via RPC."""
    return connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER, secret_label="MCP Odoo Pro Secret")

@mcp.tool()
def ensure_mission_lanes() -> str:
    """
    Checks and creates the 5 professional mission lanes (projects) in Odoo if they are missing.
    Lanes: Heritage, Website, Security, Stockenweiler, Infrastructure.
    """
    try:
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
        return f"Success: Created {len(created_ids)} lanes. All 5 professional mission lanes are now active."
    except Exception as e:
        return f"Error ensuring mission lanes: {str(e)}"

@mcp.tool()
def activate_discount_feature() -> str:
    """
    Enables the 'Discount on lines' feature in Odoo for the Admin and Wolf users.
    Required for professional invoicing.
    """
    try:
        session = get_odoo_session()
        group_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.groups', 'search', [[['name', '=', 'Discount on lines']]])
        if group_ids:
            user_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'res.users', 'search', [[['login', 'in', ['admin', 'wolf@frawo-tech.de']]]])
            session.models.execute_kw(session.db, session.uid, session.secret, 'res.groups', 'write', [group_ids, {'users': [(4, uid) for uid in user_ids]}])
            return "Success: Discount feature activated for Admin and Wolf."
        return "Warning: Discount group 'Discount on lines' not found in Odoo."
    except Exception as e:
        return f"Error activating discount feature: {str(e)}"

@mcp.tool()
def reclaim_tasks() -> str:
    """
    Analyzes all Odoo tasks and automatically moves them into the correct mission lanes
    based on keyword matching (e.g., 'Website' -> Lane B).
    """
    try:
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
                
        return f"Success: Reclaimed {reclaimed} tasks into their respective mission lanes."
    except Exception as e:
        return f"Error reclaiming tasks: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

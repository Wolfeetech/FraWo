import json
import os
import sys
from odoo_rpc_client import connect

# Odoo Connection Configuration (SSOT)
ODOO_URL = os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069")
ODOO_DB = os.getenv("ODOO_RPC_DB", "FraWo_GbR")
ODOO_USER = os.getenv("ODOO_RPC_USER", "wolf@frawo-tech.de")
ODOO_PWD = os.getenv("ODOO_RPC_PASSWORD", "admin")  # Should be moved to vault later

def get_odoo_session():
    return connect(url=ODOO_URL, db=ODOO_DB, default_user=ODOO_USER, secret_label="MCP Odoo Secret")

def list_projects():
    """List all projects from the Odoo SSOT."""
    session = get_odoo_session()
    projects = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search_read',
        [[]], {'fields': ['name', 'description']}
    )
    return projects

def create_task(project_id, name, description=""):
    """Create a new task in the Odoo SSOT."""
    session = get_odoo_session()
    task_id = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.task', 'create',
        [{'project_id': project_id, 'name': name, 'description': description}]
    )
    return task_id

def main():
    # Simple MCP-style tool dispatcher
    if len(sys.argv) < 2:
        print("Usage: mcp_odoo_server.py [list_projects|create_task]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    if cmd == "list_projects":
        print(json.dumps(list_projects(), indent=2))
    elif cmd == "create_task":
        if len(sys.argv) < 4:
            print("Usage: create_task <project_id> <name> [description]")
            sys.exit(1)
        pid = int(sys.argv[2])
        name = sys.argv[3]
        desc = sys.argv[4] if len(sys.argv) > 4 else ""
        print(f"Created task ID: {create_task(pid, name, desc)}")

if __name__ == "__main__":
    main()

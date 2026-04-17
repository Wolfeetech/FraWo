import re
import os
from odoo_rpc_client import connect

def parse_masterplan(file_path):
    lanes = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Regex to find Lanes and their status
    lane_pattern = re.compile(r'- `(Lane [A-Z]: [^`]+)` -> `([^`]+)`')
    matches = lane_pattern.findall(content)
    
    for name, status in matches:
        lanes.append({
            'name': name,
            'status': status,
            'description': f"Migrated from MASTERPLAN.md on 2026-04-17. Status: {status}"
        })
    return lanes

def migrate_to_odoo(lanes):
    print("Connecting to Odoo SSOT...")
    # Use environment or known defaults
    session = connect(
        url=os.getenv("ODOO_RPC_URL", "http://10.1.0.22:8069"),
        db=os.getenv("ODOO_RPC_DB", "FraWo_Live"),
        default_user="wolf@frawo-tech.de",
        secret_label="Odoo SSOT Password"
    )
    
    # 1. Create or Find Project
    project_name = "FraWo Homeserver 2027"
    project_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        'project.project', 'search',
        [[['name', '=', project_name]]]
    )
    
    if project_ids:
        project_id = project_ids[0]
        print(f"Found existing project: {project_name} (ID: {project_id})")
    else:
        project_id = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.project', 'create',
            [{'name': project_name, 'description': 'Zentrale Roadmap fuer den Homeserver 2027'}]
        )
        print(f"Created new project: {project_name} (ID: {project_id})")
    
    # 2. Inject Lanes as Tasks
    for lane in lanes:
        # Check if task already exists
        task_ids = session.models.execute_kw(
            session.db, session.uid, session.secret,
            'project.task', 'search',
            [[['name', '=', lane['name']], ['project_id', '=', project_id]]]
        )
        
        if not task_ids:
            task_id = session.models.execute_kw(
                session.db, session.uid, session.secret,
                'project.task', 'create',
                [{
                    'project_id': project_id,
                    'name': lane['name'],
                    'description': lane['description'],
                    'active': True
                }]
            )
            print(f"Migrated {lane['name']} as Task ID: {task_id}")
        else:
            print(f"Task {lane['name']} already exists. Skipping.")

if __name__ == "__main__":
    masterplan_path = "MASTERPLAN.md"
    if os.path.exists(masterplan_path):
        lanes = parse_masterplan(masterplan_path)
        if lanes:
            migrate_to_odoo(lanes)
        else:
            print("No lanes found in MASTERPLAN.md")
    else:
        print(f"File not found: {masterplan_path}")

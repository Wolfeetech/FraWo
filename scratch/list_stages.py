import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    # Read stages
    stages = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task.type', 'search_read', [[]], {'fields': ['id', 'name']})
    print(f"Found {len(stages)} stages:")
    for s in stages:
        print(f"- ID: {s['id']} - Name: {s['name']}")

if __name__ == "__main__":
    main()

import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    # Read tasks
    tasks = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'read', [[154, 155, 156]], {'fields': ['name', 'state', 'stage_id']})
    for t in tasks:
        print(f"Task #{t['id']}: {t['name']}")
        print(f"  State: {t['state']}")
        print(f"  Stage: {t['stage_id']}")

if __name__ == "__main__":
    main()

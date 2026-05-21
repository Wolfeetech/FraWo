import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    # Masterplan project ID is 21
    tasks = session.models.execute_kw(
        session.db, session.uid, session.secret, 
        'project.task', 'search_read', 
        [[('project_id', '=', 21), ('stage_id.name', '!=', '✅ Erledigt')]], 
        {'fields': ['name', 'stage_id']}
    )
    for t in tasks:
        print(f"{t['id']}: {t['name']} (Stage: {t['stage_id'][1]})")

if __name__ == '__main__':
    main()

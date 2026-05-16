import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    task_ids = [155, 162]
    stage_today_id = 8
    
    result = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [task_ids, {
        'stage_id': stage_today_id,
        'priority': '1' # Adds a star/high priority
    }])
    print(f"Moved tasks {task_ids} to stage {stage_today_id} and set high priority: {result}")

if __name__ == "__main__":
    main()

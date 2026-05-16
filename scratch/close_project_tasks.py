import os
import sys
sys.path.append(os.path.abspath('.'))
from scripts.business.odoo_rpc_client import connect

def main():
    session = connect(default_user='wolf@frawo-tech.de', prompt_for_username=False)
    
    project_id = 5 # Stockenweiler Migration
    stage_done_id = 12
    
    # Search for tasks in project 5 that are not in stage 12
    task_ids = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'search', [[('project_id', '=', project_id), ('stage_id', '!=', stage_done_id)]])
    
    print(f"Found {len(task_ids)} open tasks in project {project_id}.")
    
    if task_ids:
        # Update stage to 12
        result = session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [task_ids, {'stage_id': stage_done_id}])
        print(f"Updated tasks to stage {stage_done_id}: {result}")
        
        # Also try to set state to '02_done'
        try:
            session.models.execute_kw(session.db, session.uid, session.secret, 'project.task', 'write', [task_ids, {'state': '02_done'}])
            print("Set state to 02_done.")
        except Exception as e:
            print(f"Could not set state: {e}")

if __name__ == "__main__":
    main()

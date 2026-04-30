import xmlrpc.client
import os

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'Wolf2024!Frawo'

def audit():
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    print("--- PROJECTS ---")
    projects = models.execute_kw(db, uid, password, 'project.project', 'search_read', [[]], {'fields': ['name', 'id']})
    for p in projects:
        print(f"Project: {p['name']} (ID: {p['id']})")
        tasks = models.execute_kw(db, uid, password, 'project.task', 'search_read', [[('project_id', '=', p['id'])]], {'fields': ['name', 'stage_id', 'kanban_state']})
        for t in tasks:
            print(f"  - Task: {t['name']} (Stage: {t['stage_id']}, State: {t['kanban_state']})")

if __name__ == "__main__":
    audit()

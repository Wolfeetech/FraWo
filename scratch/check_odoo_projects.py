import xmlrpc.client

url = 'http://10.1.0.22:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'Wolf2024!Frawo'

def check_odoo_projects():
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    if not uid:
        print("[X] Auth failed")
        return
    
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    print("--- Projects ---")
    projects = models.execute_kw(db, uid, password, 'project.project', 'search_read', [[]], {'fields': ['id', 'name']})
    for p in projects:
        print(f"Project [{p['id']}]: {p['name']}")
        
    print("\n--- Tasks ---")
    tasks = models.execute_kw(db, uid, password, 'project.task', 'search_read', [[]], {'fields': ['id', 'name', 'project_id', 'stage_id', 'is_closed']})
    for t in tasks:
        print(f"Task [{t['id']}]: {t['name']} | Stage: {t['stage_id']} | Closed: {t['is_closed']}")

if __name__ == "__main__":
    check_odoo_projects()

import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
import socket
socket.setdefaulttimeout(15.0)

url = "http://10.1.0.112:8069"
db = "FraWo_GbR"
user = "wolf@frawo.tech"
password = "FrawoWolf2026!"

print(f"Connecting to Odoo at {url}...")
common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
try:
    uid = common.authenticate(db, user, password, {})
    if not uid:
         # Try other DB
         db = "FraWo_Live"
         print(f"Failed GbR, trying DB {db}...")
         uid = common.authenticate(db, user, password, {})
         if not uid:
             raise RuntimeError("Authentication failed.")
             
    print(f"Connected successfully. UID: {uid}, DB: {db}")
    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)
    
    # Let's search for Project 35 or projects containing 'Infrastruktur'
    projects = models.execute_kw(db, uid, password, 'project.project', 'search_read', [[]], {'fields': ['id', 'name']})
    print("\n=== PROJECTS ===")
    for p in projects:
        print(f"ID: {p['id']} | Name: {p['name']}")
        
    # Get all active tasks for Project 35 or project '🏗️ Infrastruktur & Betrieb'
    # We will search for all tasks in any project, then filter
    print("\n=== TASKS ===")
    tasks = models.execute_kw(db, uid, password, 'project.task', 'search_read', 
                              [[('stage_id.name', 'not ilike', 'Erledigt'), ('stage_id.name', 'not ilike', 'Done')]], 
                              {'fields': ['id', 'name', 'project_id', 'stage_id', 'description']})
    
    for t in tasks:
        p_id = t['project_id'][0] if t['project_id'] else None
        p_name = t['project_id'][1] if t['project_id'] else "None"
        s_name = t['stage_id'][1] if t['stage_id'] else "None"
        print(f"ID: {t['id']} | Project: [{p_id}] {p_name:<25} | Stage: {s_name:<15} | Name: {t['name']}")
except Exception as e:
    print(f"Error: {e}")

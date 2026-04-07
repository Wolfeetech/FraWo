import xmlrpc.client
URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# Lese Tasks aus Projekt 12 und 13
project_ids = [12, 13]
tasks = models.execute_kw(DB, uid, PASS, 'project.task', 'search_read', 
    [[('project_id', 'in', project_ids)]], 
    {'fields': ['name', 'description', 'project_id', 'stage_id', 'tag_ids']}
)

print(f"--- Tasks in Projekten 12 & 13 ---")
for t in tasks:
    print(f"ID: {t['id']} | Project: {t['project_id'][1]} | Name: {t['name']}")

# Prüfe ob User "Agent" existiert
agent_user = models.execute_kw(DB, uid, PASS, 'res.users', 'search_read', 
    [[('name', 'ilike', 'Agent')]], 
    {'fields': ['name', 'login']}
)
print(f"\n--- User 'Agent' Check ---")
print(agent_user)

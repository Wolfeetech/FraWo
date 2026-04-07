import xmlrpc.client
URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

projects = models.execute_kw(DB, uid, PASS, 'project.project', 'search_read', [[]], {'fields': ['name']})
for p in projects:
    print(f"Project: {p['name']} (ID: {p['id']})")

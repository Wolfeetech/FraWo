import xmlrpc.client

url = "http://10.1.0.22:8069"
db = "FraWo_GbR"
username = "admin" # I'll try admin again
password = "frawo_temp_2026"

try:
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    if not uid:
        # Try agent user
        username = "agent@frawo-tech.de"
        uid = common.authenticate(db, username, password, {})
    
    if uid:
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
        views = models.execute_kw(db, uid, password, 'ir.ui.view', 'search_read', [[['key', 'ilike', 'css']]], {'fields': ['key', 'name']})
        for v in views:
            print(f"KEY: {v['key']} | NAME: {v['name']}")
    else:
        print("Auth failed for both admin and agent.")
except Exception as e:
    print(f"Error: {e}")

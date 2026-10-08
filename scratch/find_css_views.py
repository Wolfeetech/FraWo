import xmlrpc.client

import os

url = os.environ.get("ODOO_URL", "http://10.1.0.112:8069")
db = os.environ.get("ODOO_DB", "FraWo_GbR")
username = os.environ.get("ODOO_USER", "admin")
password = os.environ.get("ODOO_PASSWORD", "")

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

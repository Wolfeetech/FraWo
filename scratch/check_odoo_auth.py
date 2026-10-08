import xmlrpc.client

try:
    common = xmlrpc.client.ServerProxy("http://10.1.0.22:8069/xmlrpc/2/common")
    print("Databases:")
    # For Odoo 16/17, getting databases via common.login without db doesn't work, we must know the db.
    import os
    pwd = os.environ.get("ODOO_PASSWORD", "")
    for db in ["FraWo_GbR", "FraWo_Live"]:
        uid = common.authenticate(db, "admin", pwd, {})
        print(f"Auth for {db}: {uid}")
except Exception as e:
    print(f"Error: {e}")

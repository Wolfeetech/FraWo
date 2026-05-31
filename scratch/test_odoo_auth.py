import xmlrpc.client

url = "http://10.1.0.22:8069"
db = "FraWo_GbR"
username = "admin"
password = "frawo_temp_2026"

print(f"Connecting to {url}...")
try:
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    if uid:
        print(f"SUCCESS! UID: {uid}")
    else:
        print("FAILED: Authentication failed.")
except Exception as e:
    print(f"ERROR: {e}")

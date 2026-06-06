import xmlrpc.client
import os

URL = os.environ.get("ODOO_URL", "http://10.4.0.22:8069")
DB = os.environ.get("ODOO_DB", "FraWo_GbR")
USER = os.environ.get("ODOO_USER", "wolf@frawo-tech.de")
PASSWORD = os.environ.get("ODOO_PASSWORD", "")

if not PASSWORD:
    print("ERROR: Set ODOO_PASSWORD env var before running.")
    exit(1)

try:
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if uid:
        print(f"OK — uid={uid}")
    else:
        print("FAILED: Authentication failed.")
except Exception as e:
    print(f"ERROR: {e}")

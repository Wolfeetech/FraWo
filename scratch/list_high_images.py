import os, xmlrpc.client
from pathlib import Path

env_file = Path("C:/Users/StudioPC/.ai-tools-shared/.env")
if env_file.exists():
    for line in open(env_file):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k.strip()] = v.strip()

url = os.getenv("ODOO_URL", "http://10.4.0.22:8069")
db = os.getenv("ODOO_DB_GBR", "FraWo_GbR")
user = os.getenv("ODOO_USER", "wolf@frawo-tech.de")
pw = os.getenv("ODOO_PASSWORD", "Wolf2024!Frawo")

common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
uid = common.authenticate(db, user, pw, {})
models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")

images = models.execute_kw(db, uid, pw, 'ir.attachment', 'search_read', [[['mimetype', '=like', 'image/%']]], {'fields': ['id', 'name']})
for img in images:
    if img['id'] > 900:
        print(f"ID: {img['id']} | Name: {img['name']}")

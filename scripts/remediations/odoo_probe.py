import xmlrpc.client
import os

URL = "http://100.82.26.53:8444"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASSWORD = "Wolf2024!Frawo"

def probe():
    print(f"Probing Odoo at {URL}...")
    try:
        common = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/common')
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if uid:
            print(f"Success! UID: {uid}")
            models = xmlrpc.client.ServerProxy(f'{URL}/xmlrpc/2/object')
            projects = models.execute_kw(DB, uid, PASSWORD, 'project.project', 'search_read', [[]], {'fields': ['name']})
            print(f"Projects found: {projects}")
        else:
            print("Authentication failed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe()

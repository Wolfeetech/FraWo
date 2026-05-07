# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
import subprocess
import json
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection, resolve_db_password

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
db_password = resolve_db_password()
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def run_psql(sql):
    cmd = ['docker', 'exec', '-e', f'PGPASSWORD={db_password}', 'odoo_db_1', 'psql', '-U', 'odoo', '-d', db, '-t', '-c', sql]
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip()

# Find stage-like images
img_sql = "SELECT id, name FROM ir_attachment WHERE mimetype LIKE 'image/%' AND public=True ORDER BY id DESC LIMIT 100;"
images = run_psql(img_sql)

# Read Homepage View
v_data = models.execute_kw(db, uid, password, 'ir.ui.view', 'read', [[3644]], {'fields': ['arch_db']})

print("IMAGES:")
print(images)
print("\nHOMEPAGE ARCH:")
print(v_data[0]['arch_db'])

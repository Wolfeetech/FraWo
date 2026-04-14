# -*- coding: utf-8 -*-
import xmlrpc.client
import subprocess
import json

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

def run_psql(sql):
    cmd = ['docker', 'exec', '-e', 'PGPASSWORD=odoo_db_pass_final_v1', 'odoo_db_1', 'psql', '-U', 'odoo', '-d', 'FraWo_GbR', '-t', '-c', sql]
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

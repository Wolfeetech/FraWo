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

# Find images that look like "Stage" or "Bühne" (Buehne)
img_search = "SELECT id, name FROM ir_attachment WHERE mimetype LIKE 'image/%' AND (name ILIKE '%stage%' OR name ILIKE '%buehne%' OR name ILIKE '%PXL%') ORDER BY id DESC LIMIT 50;"
print("IMAGE_RESULTS:")
print(run_psql(img_search))

# Find the current Homepage architecture
v_data = models.execute_kw(db, uid, password, 'ir.ui.view', 'read', [[3644]], {'fields': ['arch_db', 'key']})
print("\nHOMEPAGE_ARCH:")
print(v_data[0]['arch_db'])

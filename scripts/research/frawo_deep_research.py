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

# 1. Check DB configuration
db_info = run_psql("SELECT name, setting FROM pg_settings WHERE name IN ('server_encoding', 'client_encoding', 'lc_collate');")

# 2. Find legacy views
view_search_sql = "SELECT id, key FROM ir_ui_view WHERE website_id = 1 AND active = True AND (arch_db::text ILIKE '%Eventtechnik%' OR key ILIKE '%header_standard%' OR key ILIKE '%footer_standard%');"
views = run_psql(view_search_sql)

# 3. Read the 'website' record to find global CSS or language settings
website_data = models.execute_kw(db, uid, password, 'website', 'read', [[1]], {'fields': ['name', 'language_ids', 'default_lang_id', 'custom_code_head']})

print("DB INFO:")
print(db_info)
print("\nTARGET VIEWS:")
print(views)
print("\nWEBSITE DATA:")
print(json.dumps(website_data, indent=2))

#!/usr/bin/env python3
"""Deploy B2B and B2C pages to Odoo"""
import os, sys, xmlrpc.client
from pathlib import Path

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

b2b_path = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\Codex\website\frawo_b2b_v3.3.html')
b2c_path = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\Codex\website\frawo_b2c_v3.3.html')

if not b2b_path.exists() or not b2c_path.exists():
    print("[FAIL] Source files not found")
    exit(1)

with open(b2b_path, 'r', encoding='utf-8') as f:
    b2b_html = f.read()
with open(b2c_path, 'r', encoding='utf-8') as f:
    b2c_html = f.read()

print("[*] Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("[FAIL] Auth failed")
    exit(1)

print(f"[OK] Auth OK (UID:{uid})")
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Update B2C
b2c_view_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.page_b2c']]])
if b2c_view_ids:
    print(f"Updating B2C Page View {b2c_view_ids[0]}...")
    b2c_arch = f'<t t-name="website.b2c"><t t-call="website.layout"><div id="wrap" class="oe_structure oe_empty">{b2c_html}</div></t></t>'
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [[b2c_view_ids[0]], {'arch_db': b2c_arch}])
    print("[OK] B2C updated")
else:
    print("[WARN] B2C view not found (website.page_b2c)")

# Update B2B
b2b_view_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.page_b2b']]])
if b2b_view_ids:
    print(f"Updating B2B Page View {b2b_view_ids[0]}...")
    b2b_arch = f'<t t-name="website.b2b"><t t-call="website.layout"><div id="wrap" class="oe_structure oe_empty">{b2b_html}</div></t></t>'
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [[b2b_view_ids[0]], {'arch_db': b2b_arch}])
    print("[OK] B2B updated")
else:
    print("[WARN] B2B view not found (website.page_b2b)")

print("Done!")

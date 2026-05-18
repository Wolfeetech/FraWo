#!/usr/bin/env python3
"""Deploy Contact Page to Odoo"""
import os, sys, xmlrpc.client
from pathlib import Path

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

html_path = Path(r'C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo\Codex\website\frawo_contactus_v4_OPTIMIZED.html')

if not html_path.exists():
    print(f"[FAIL] File not found: {html_path}")
    exit(1)

with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("[*] Connecting to Odoo...")
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("[FAIL] Auth failed")
    exit(1)

print(f"[OK] Auth OK (UID:{uid})")
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Wrap in Odoo Template
contact_html = f"""<t t-call="website.layout">
    <div id="wrap" class="oe_structure">
        {html_content}
    </div>
</t>"""

# Find contact page
pages = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'website.page', 'search_read',
    [[['url', '=', '/contactus']]],
    {'fields': ['id', 'name', 'view_id']}
)

if not pages:
    print("[FAIL] Contact page not found!")
    exit(1)

page = pages[0]
view_id = page['view_id'][0]

print(f"[*] Updating Contact Page (Page ID:{page['id']}, View ID:{view_id})...")

# Update view
models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'ir.ui.view', 'write',
    [[view_id], {
        'arch_db': contact_html,
    }]
)

print("[OK] Contact page updated!")

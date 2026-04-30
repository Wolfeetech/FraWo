# -*- coding: utf-8 -*-
# Simple Direct Deployment — No dependencies

import xmlrpc.client
import os
import getpass
from pathlib import Path

print("=" * 70)
print("FraWo Website v3.5 — Simple Deployment")
print("=" * 70)

# Odoo Connection
url = os.getenv("ODOO_RPC_URL", "http://172.21.0.3:8069")
db = os.getenv("ODOO_RPC_DB", "FraWo_GbR")
username = os.getenv("ODOO_RPC_USER", "wolf@frawo-tech.de")

# Get password from env or prompt
password = os.getenv("ODOO_RPC_PASSWORD") or os.getenv("ODOO_RPC_API_KEY")
if not password:
    password = getpass.getpass("Odoo Password: ")

print(f"\nConnecting to Odoo...")
print(f"   URL: {url}")
print(f"   DB: {db}")
print(f"   User: {username}\n")

try:
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})

    if not uid:
        print("[X] Authentication failed!")
        exit(1)

    print(f"[OK] Connected! UID: {uid}\n")

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # Step 1: Deploy Global CSS
    print("[1/2] Deploying Global CSS...")
    css_file = Path("C:/WORKSPACE/FraWo/DOCS/ODOO_GLOBAL_CSS_V3.5.css")

    if not css_file.exists():
        print(f"   ❌ CSS file not found: {css_file}")
        exit(1)

    css_content = css_file.read_text(encoding='utf-8')

    website_ids = models.execute_kw(db, uid, password, 'website', 'search', [[]], {'limit': 1})

    if website_ids:
        models.execute_kw(db, uid, password, 'website', 'write', [website_ids, {
            'custom_code_head': f'<style>\n{css_content}\n</style>'
        }])
        print(f"   [OK] Global CSS deployed (website ID: {website_ids[0]})")
    else:
        print("   [X] No website found!")
        exit(1)

    # Step 2: Deploy Homepage
    print("\n[2/2] Deploying Homepage...")
    homepage_file = Path("C:/WORKSPACE/FraWo/DOCS/ODOO_HOMEPAGE_V3.5_READY_TO_USE.html")

    if not homepage_file.exists():
        print(f"   [X] Homepage file not found: {homepage_file}")
        exit(1)

    homepage_content = homepage_file.read_text(encoding='utf-8')

    # Simple QWeb template
    homepage_arch = f"""<?xml version="1.0"?>
<odoo>
    <template id="homepage" name="FraWo Homepage v3.5">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                {homepage_content}
            </div>
        </t>
    </template>
</odoo>
"""

    # Update or create view
    view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search',
        [[('key', '=', 'website.homepage')]])

    if view_ids:
        models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [view_ids, {
            'arch_db': homepage_arch,
        }])
        print(f"   [OK] Homepage updated (view ID: {view_ids[0]})")
    else:
        view_id = models.execute_kw(db, uid, password, 'ir.ui.view', 'create', [{
            'name': 'FraWo Homepage v3.5',
            'key': 'website.homepage',
            'type': 'qweb',
            'arch_db': homepage_arch,
        }])
        print(f"   [OK] Homepage created (view ID: {view_id})")

    print("\n" + "=" * 70)
    print("[OK] DEPLOYMENT SUCCESSFUL!")
    print("=" * 70)
    print("\nVisit: https://www.frawo-tech.de")
    print("\nYou can now edit in Odoo:")
    print("   1. Click 'Edit' (top right)")
    print("   2. Change images, text, anything!")
    print("   3. Click 'Save'")
    print("\n" + "=" * 70)

except Exception as e:
    print(f"\n[X] ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

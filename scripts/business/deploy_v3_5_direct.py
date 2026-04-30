# -*- coding: utf-8 -*-
# Direct Deployment of v3.5 to Odoo — No SSH, pure XML-RPC

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection
import xmlrpc.client

print("=" * 70)
print("FraWo Website v3.5 — Direct Deployment")
print("=" * 70)

# Connect to Odoo
settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print(f"\n✅ Connected to Odoo: {url}")
print(f"   Database: {db}")
print(f"   User: {username}\n")

# Step 1: Deploy Global CSS
print("[1/2] Deploying Global CSS (Header, Footer, Fonts)...")
css_file = Path("C:/WORKSPACE/FraWo/DOCS/ODOO_GLOBAL_CSS_V3.5.css")
css_content = css_file.read_text(encoding='utf-8')

website_ids = models.execute_kw(db, uid, password, 'website', 'search', [[]], {'limit': 1})
if website_ids:
    models.execute_kw(db, uid, password, 'website', 'write', [website_ids, {
        'custom_code_head': f'<style>\n{css_content}\n</style>'
    }])
    print(f"   ✅ Global CSS deployed to website.custom_code_head")
else:
    print("   ❌ No website found!")
    sys.exit(1)

# Step 2: Deploy Homepage
print("\n[2/2] Deploying Homepage (Content + Radio Player)...")
homepage_file = Path("C:/WORKSPACE/FraWo/DOCS/ODOO_HOMEPAGE_V3.5_READY_TO_USE.html")
homepage_content = homepage_file.read_text(encoding='utf-8')

# Create QWeb view
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

# Check if view exists
view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search',
    [[('key', '=', 'website.homepage')]])

if view_ids:
    # Update existing
    models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [view_ids, {
        'arch_db': homepage_arch,
        'name': 'FraWo Homepage v3.5',
    }])
    print(f"   ✅ Updated existing view (ID: {view_ids[0]})")
else:
    # Create new
    view_id = models.execute_kw(db, uid, password, 'ir.ui.view', 'create', [{
        'name': 'FraWo Homepage v3.5',
        'key': 'website.homepage',
        'type': 'qweb',
        'arch_db': homepage_arch,
    }])
    print(f"   ✅ Created new view (ID: {view_id})")

# Ensure it's published
page_ids = models.execute_kw(db, uid, password, 'website.page', 'search',
    [[('url', '=', '/')]])

if page_ids:
    models.execute_kw(db, uid, password, 'website.page', 'write', [page_ids, {
        'is_published': True,
    }])
    print(f"   ✅ Homepage published")

print("\n" + "=" * 70)
print("✅ DEPLOYMENT COMPLETE!")
print("=" * 70)
print("\nGo to https://www.frawo-tech.de to see the result!")
print("\nYou can now edit everything in the Odoo Editor:")
print("  - Click 'Edit' in the top menu")
print("  - Change images, text, layout")
print("  - Everything is WYSIWYG!")
print("\n" + "=" * 70)

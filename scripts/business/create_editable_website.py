# -*- coding: utf-8 -*-
# Create Editable Website in Odoo (no more Python-View mess!)

import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection
import xmlrpc.client

settings = resolve_connection("http://10.1.0.22:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("=" * 60)
print("Creating Editable FraWo Website in Odoo")
print("=" * 60)

# Step 1: Apply v3.5 CSS
print("\n[1/3] Applying v3.5 Ultra-Minimal CSS...")
css_file = Path("C:/WORKSPACE/FraWo/Codex/website/frawo_custom_css.css")
css_content = css_file.read_text(encoding='utf-8')

css_arch = f"<style>\n{css_content}\n</style>"
website_id = models.execute_kw(db, uid, password, 'website', 'search', [[]], {'limit': 1})
if website_id:
    models.execute_kw(db, uid, password, 'website', 'write', [website_id, {'custom_code_head': css_arch}])
    print("   ✅ CSS applied to website.custom_code_head")
else:
    print("   ❌ No website found!")
    sys.exit(1)

# Step 2: Create Homepage as EDITABLE page
print("\n[2/3] Creating editable Homepage...")

# Read homepage content
homepage_file = Path("C:/WORKSPACE/FraWo/Codex/website/frawo_homepage_blocks.html")
homepage_content = homepage_file.read_text(encoding='utf-8')

# Create QWeb view for homepage
homepage_arch = f"""<?xml version="1.0"?>
<odoo>
    <template id="homepage" name="FraWo Homepage v3.5">
        <t t-call="website.layout">
            <div id="wrap">
                {homepage_content}
            </div>
        </t>
    </template>
</odoo>
"""

# Check if homepage view exists
view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search', [[('key', '=', 'website.homepage')]])

if view_ids:
    # Update existing
    models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [view_ids, {
        'arch_db': homepage_arch,
        'name': 'FraWo Homepage v3.5',
        'type': 'qweb',
    }])
    print(f"   ✅ Updated existing view (ID: {view_ids[0]})")
    view_id = view_ids[0]
else:
    # Create new
    view_id = models.execute_kw(db, uid, password, 'ir.ui.view', 'create', [{
        'name': 'FraWo Homepage v3.5',
        'key': 'website.homepage',
        'type': 'qweb',
        'arch_db': homepage_arch,
    }])
    print(f"   ✅ Created new view (ID: {view_id})")

# Step 3: Create website.page for homepage (makes it editable!)
print("\n[3/3] Creating editable Page...")

page_ids = models.execute_kw(db, uid, password, 'website.page', 'search', [[('url', '=', '/')]])

if page_ids:
    # Update existing
    models.execute_kw(db, uid, password, 'website.page', 'write', [page_ids, {
        'view_id': view_id,
        'is_published': True,
        'website_indexed': True,
    }])
    print(f"   ✅ Updated existing page (ID: {page_ids[0]})")
else:
    # Create new
    page_id = models.execute_kw(db, uid, password, 'website.page', 'create', [{
        'url': '/',
        'view_id': view_id,
        'website_id': website_id[0],
        'is_published': True,
        'website_indexed': True,
    }])
    print(f"   ✅ Created new page (ID: {page_id})")

print("\n" + "=" * 60)
print("✅ DONE! Website is now editable in Odoo!")
print("=" * 60)
print("\nNow you can:")
print("1. Go to https://www.frawo-tech.de")
print("2. Login to Odoo")
print("3. Click 'Edit' in the top menu")
print("4. Change images, text, layout - everything!")
print("\n" + "=" * 60)

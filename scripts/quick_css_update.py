#!/usr/bin/env python3
"""Quick CSS Update - Inject v7.0 CSS into existing homepage"""

import xmlrpc.client

# Odoo
ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

# Read new CSS
with open('Codex/website/frawo_custom_css.css', 'r', encoding='utf-8') as f:
    new_css = f.read()

# Connect
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print('[*] Finding homepage...')

# Get homepage
page_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'website.page', 'search', [[['url', '=', '/']]])

if not page_ids:
    print('[!] Homepage not found')
    exit(1)

# Get view
page = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'website.page', 'read', [page_ids[0], ['view_id']])[0]

view_id = page['view_id'][0]

# Get current arch
view = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'ir.ui.view', 'read', [view_id, ['arch_db']])[0]

arch = view['arch_db']

print('[*] Updating CSS...')

# Find and replace CSS in style tags
import re

# Escape for XML
css_escaped = (new_css
    .replace('&', '&amp;')
    .replace('<', '&lt;')
    .replace('>', '&gt;'))

if '<style>' in arch:
    # Replace existing
    new_arch = re.sub(r'<style>.*?</style>', f'<style>{css_escaped}</style>', arch, flags=re.DOTALL)
    print('[*] Replaced existing CSS')
else:
    # Add new - before closing </div> of wrap
    new_arch = arch.replace('</div>\n    </t>', f'        <style>{css_escaped}</style>\n</div>\n    </t>')
    print('[*] Added new CSS')

# Update
models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'ir.ui.view', 'write', [[view_id], {'arch_db': new_arch}])

print('[OK] CSS v7.0 deployed!')
print('[*] Test: https://www.frawo-tech.de/ (Ctrl+Shift+R to clear cache)')

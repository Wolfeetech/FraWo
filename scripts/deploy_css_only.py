#!/usr/bin/env python3
# Quick CSS Update Script for FraWo v7.0

import xmlrpc.client
from pathlib import Path

# Odoo Connection
ODOO_URL = 'http://10.4.0.22:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = 'Wolf2024!Frawo'

# Read CSS
css_path = Path(__file__).parent.parent / 'Codex' / 'website' / 'frawo_custom_css.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css_content = f.read()

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

print('[*] Searching for CSS asset...')

# Search for the CSS asset
asset_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
    'ir.asset', 'search',
    [[('name', 'ilike', 'frawo'), ('path', 'ilike', 'css')]])

if not asset_ids:
    # Try searching for any FraWo CSS
    asset_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'ir.asset', 'search',
        [[('path', 'ilike', 'frawo_custom_css')]])

if asset_ids:
    print(f'[*] Found asset ID: {asset_ids[0]}')
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'ir.asset', 'write',
        [asset_ids, {'inline': css_content}])
    print('[OK] CSS v7.0 deployed!')
else:
    # Create new asset
    print('[*] Creating new CSS asset...')
    asset_id = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'ir.asset', 'create',
        [{
            'name': 'FraWo Custom CSS v7.0',
            'bundle': 'web.assets_frontend',
            'path': 'website/static_src/frawo-custom-theme/frawo_custom_css.css',
            'inline': css_content,
            'active': True
        }])
    print(f'[OK] CSS asset created! ID: {asset_id}')

print('[*] Clearing Odoo cache...')
# Force refresh
try:
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD,
        'ir.qweb', 'clear_caches', [])
    print('[OK] Cache cleared!')
except:
    print('[!] Cache clear failed (might need manual clear)')

print('')
print('[OK] CSS v7.0 deployed successfully!')
print('[*] Test: https://www.frawo-tech.de/ (Ctrl+Shift+R to clear browser cache)')

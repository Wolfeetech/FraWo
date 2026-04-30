# -*- coding: utf-8 -*-
# Check what CSS is actually stored in Odoo

import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Read website custom_code_head
websites = models.execute_kw(db, uid, password, 'website', 'search_read', [[]], {'fields': ['custom_code_head'], 'limit': 1})

if websites:
    css = websites[0].get('custom_code_head', '')
    print("=== ODOO CUSTOM_CODE_HEAD ===")
    print(css[:500])  # First 500 chars
    print("\n...")
    print("\n=== SEARCH FOR KEYWORDS ===")
    if '2026-04-28' in css:
        print("✅ Found timestamp 2026-04-28")
    else:
        print("❌ Timestamp NOT found")

    if 'transparent !important' in css:
        print("✅ Found 'transparent !important' (v3.5)")
    else:
        print("❌ 'transparent !important' NOT found")

    if 'var(--fw-bg) !important' in css:
        print("⚠️  Found 'var(--fw-bg) !important' (old version)")
    else:
        print("✅ Old 'var(--fw-bg)' NOT found")
else:
    print("No website found!")

#!/usr/bin/env python3
"""Add performance hints (preload, dns-prefetch) to FraWo Website"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

PERFORMANCE_HINTS = """
<!-- Performance Hints -->
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link rel="dns-prefetch" href="https://fonts.googleapis.com"/>
<link rel="dns-prefetch" href="https://fonts.gstatic.com"/>

<!-- Preload Critical Resources -->
<link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" as="style"/>
<link rel="preload" href="/web/image/1003/hero-bodensee.webp" as="image" type="image/webp"/>
"""

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("[FAIL] Auth failed!")
    sys.exit(1)

print(f"[OK] Auth OK (UID:{uid})")

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Find website
websites = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'search_read', [[]], {'fields': ['id', 'custom_code_head'], 'limit': 1})

if websites:
    website = websites[0]
    current_head = website['custom_code_head'] or ''

    # Add performance hints if not already present
    if 'preconnect' not in current_head:
        updated_head = current_head + "\n" + PERFORMANCE_HINTS
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'write', [[website['id']], {'custom_code_head': updated_head}])
        print("[OK] Performance hints added!")
        print("\n[*] Added:")
        print("  - preconnect to fonts.googleapis.com")
        print("  - dns-prefetch for fonts")
        print("  - preload Inter font")
        print("  - preload hero image (WebP)")
    else:
        print("[INFO] Performance hints already exist")

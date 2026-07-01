#!/usr/bin/env python3
"""Check current CSS in Odoo"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

websites = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'search_read', [[]], {'fields': ['id', 'name', 'custom_code_head'], 'limit': 1})

if websites:
    website = websites[0]
    print(f"[*] Website ID: {website['id']}")
    print(f"[*] Website Name: {website['name']}")
    print(f"\n[*] Custom Code Head (first 500 chars):")
    print(website['custom_code_head'][:500] if website['custom_code_head'] else "EMPTY!")

    # Check for specific CSS rules
    if website['custom_code_head']:
        if '--spacing-xs' in website['custom_code_head']:
            print("\n[OK] New CSS variables found!")
        else:
            print("\n[WARN] Old CSS still in Odoo!")

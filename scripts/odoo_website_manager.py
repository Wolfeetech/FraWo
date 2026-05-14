#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Odoo Website Manager - List & Update Pages
==========================================
Usage: python odoo_website_manager.py [--list] [--update-homepage]
"""

import os
import sys
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

# Odoo connection
ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'  # Corrected database name
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')


def connect_odoo():
    """Connect to Odoo and return models proxy"""
    print(f"[*] Connecting to {ODOO_URL}...")

    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

    if not uid:
        print("[FAIL] Authentication failed!")
        sys.exit(1)

    print(f"[OK] Auth OK (UID:{uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    return models, uid


def list_pages(models, uid):
    """List all website pages"""
    pages = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'website.page', 'search_read',
        [[]],
        {'fields': ['id', 'name', 'url', 'website_published'], 'order': 'id'}
    )

    print("\n=== WEBSITE PAGES ===")
    for page in pages:
        status = "PUB" if page['website_published'] else "OFF"
        print(f"  {status} [{page['id']:2d}] {page['name']:<30} {page['url']}")

    return pages


def get_page_view_content(models, uid, page_id):
    """Get the view content for a page"""
    page = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'website.page', 'read',
        [[page_id]],
        {'fields': ['view_id', 'arch']}
    )[0]

    if page.get('view_id'):
        view_id = page['view_id'][0]
        view = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'ir.ui.view', 'read',
            [[view_id]],
            {'fields': ['name', 'arch', 'key']}
        )[0]
        return view

    return None


def main():
    """Main entry point"""
    try:
        models, uid = connect_odoo()

        # List all pages
        pages = list_pages(models, uid)

        # Find homepage
        homepage = next((p for p in pages if p['url'] == '/'), None)

        if homepage:
            print(f"\n=== HOMEPAGE ===")
            print(f"ID: {homepage['id']}")
            print(f"Name: {homepage['name']}")
            print(f"URL: {homepage['url']}")
            print(f"Published: {homepage['website_published']}")

            # Get view content
            view = get_page_view_content(models, uid, homepage['id'])
            if view:
                print(f"View ID: {view['id']}")
                print(f"View Name: {view['name']}")
                print(f"\nCurrent Arch (first 500 chars):")
                print(view['arch'][:500] if view['arch'] else "(empty)")

        return 0

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

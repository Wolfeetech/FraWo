#!/usr/bin/env python3
"""Add SEO Metadata to FraWo Homepage"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

# SEO Metadata
SEO_TITLE = "FraWo Veranstaltungstechnik Bodensee | Licht & Ton für Events"
SEO_DESCRIPTION = "Professionelle Veranstaltungstechnik am Bodensee. PA-Systeme, Lichttechnik, Bühnenaufbau. IHK-Fachkraft + Zimmermann. Jetzt anfragen!"
SEO_KEYWORDS = "Veranstaltungstechnik Bodensee, Licht Ton Verleih, PA-Systeme, Moving Heads, Bühnenaufbau, Event Technik Weissensberg, Fußballdart mieten"

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    print("[FAIL] Auth failed!")
    sys.exit(1)

print(f"[OK] Auth OK (UID:{uid})")

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Find homepage
pages = models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'website.page', 'search_read',
    [[['url', '=', '/']]],
    {'fields': ['id', 'name', 'view_id', 'website_meta_title', 'website_meta_description', 'website_meta_keywords']}
)

if not pages:
    print("[FAIL] Homepage not found!")
    sys.exit(1)

homepage = pages[0]
print(f"[*] Updating SEO metadata for homepage (Page ID:{homepage['id']})...")

# Update SEO fields
models.execute_kw(
    ODOO_DB, uid, ODOO_PASSWORD,
    'website.page', 'write',
    [[homepage['id']], {
        'website_meta_title': SEO_TITLE,
        'website_meta_description': SEO_DESCRIPTION,
        'website_meta_keywords': SEO_KEYWORDS,
    }]
)

print("[OK] SEO metadata updated!")
print(f"\nTitle: {SEO_TITLE}")
print(f"Description: {SEO_DESCRIPTION}")
print(f"Keywords: {SEO_KEYWORDS}")

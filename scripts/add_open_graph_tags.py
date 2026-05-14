#!/usr/bin/env python3
"""Add Open Graph Tags to FraWo Website"""
import os, sys, xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path.home() / '.ai-tools-shared' / '.env')

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD')

OG_TAGS = """
<!-- Open Graph / Social Media -->
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://www.frawo-tech.de/"/>
<meta property="og:title" content="FraWo Veranstaltungstechnik Bodensee | Licht & Ton"/>
<meta property="og:description" content="Professionelle Veranstaltungstechnik am Bodensee. PA-Systeme, Lichttechnik, Bühnenaufbau."/>
<meta property="og:image" content="https://www.frawo-tech.de/web/image/993/hero-bodensee.jpg"/>
<meta property="og:locale" content="de_DE"/>
<meta property="og:site_name" content="FraWo GbR"/>

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="FraWo Veranstaltungstechnik Bodensee"/>
<meta name="twitter:description" content="Professionelle Veranstaltungstechnik am Bodensee. PA-Systeme, Licht, Ton."/>
<meta name="twitter:image" content="https://www.frawo-tech.de/web/image/993/hero-bodensee.jpg"/>
"""

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

# Find website
websites = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'search_read', [[]], {'fields': ['id', 'custom_code_head'], 'limit': 1})

if websites:
    website = websites[0]
    current_head = website['custom_code_head'] or ''

    # Add OG tags if not already present
    if 'og:title' not in current_head:
        updated_head = current_head + "\n" + OG_TAGS
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website', 'write', [[website['id']], {'custom_code_head': updated_head}])
        print("[OK] Open Graph tags added!")
    else:
        print("[INFO] Open Graph tags already exist")

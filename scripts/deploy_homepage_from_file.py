#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deploy FraWo Homepage from File
===============================
Reads frawo_homepage_v4_OPTIMIZED.html and deploys it to Odoo ir.ui.view.
"""

import os
import sys
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
WEBSITE_DIR = REPO_ROOT / 'Codex' / 'website'

def deploy_homepage():
    print("[*] Connecting to Odoo...")
    
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    except Exception as e:
        print(f"[FAIL] Connection failed: {e}")
        return 1

    if not uid:
        print("[FAIL] Authentication failed!")
        return 1

    print(f"[OK] Auth OK (UID:{uid})")

    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    # Read HTML from file
    html_path = WEBSITE_DIR / 'frawo_homepage_v4_OPTIMIZED.html'
    if not html_path.exists():
        print(f"[FAIL] File not found: {html_path}")
        return 1
        
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    # Read Radio Player
    radio_player_path = WEBSITE_DIR / 'frawo_radio_player.html'
    if radio_player_path.exists():
        with open(radio_player_path, 'r', encoding='utf-8') as f:
            radio_player_content = f.read()
        print("[*] Injected radio player.")
    else:
        radio_player_content = '<!-- Radio Player not found -->'
        print("[!] Warning: frawo_radio_player.html not found!")

    html_content = html_content.replace('__RADIO_PLAYER__', radio_player_content)

    # Wrap in Odoo Template
    HOMEPAGE_HTML = f"""<t t-call="website.layout">
    <div id="wrap" class="oe_structure">
        {html_content}
    </div>
</t>"""

    # Find homepage
    pages = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'website.page', 'search_read',
        [[['url', '=', '/']]],
        {'fields': ['id', 'name', 'view_id']}
    )

    if not pages:
        print("[FAIL] Homepage not found!")
        return 1

    homepage = pages[0]
    view_id = homepage['view_id'][0]

    print(f"[*] Updating Homepage (Page ID:{homepage['id']}, View ID:{view_id})...")

    # Update page meta tags
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'website.page', 'write',
        [[homepage['id']], {
            'website_meta_title': 'FraWo Veranstaltungstechnik Bodensee | Licht & Ton für Events',
            'website_meta_description': 'Professionelle Veranstaltungstechnik am Bodensee. Licht, Ton, Verleih und Sonderbauten für Ihr Event. Jetzt anfragen!',
        }]
    )
    print("[*] Updated page meta tags.")

    # Update view arch
    models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.ui.view', 'write',
        [[view_id], {'arch': HOMEPAGE_HTML}]
    )

    print("[OK] Homepage deployed!")
    print(f"\n[*] Live at: https://www.frawo-tech.de/")

    return 0

if __name__ == "__main__":
    sys.exit(deploy_homepage())

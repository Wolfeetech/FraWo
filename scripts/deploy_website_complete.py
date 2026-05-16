#!/usr/bin/env python3
"""
FraWo Website Complete Deployment Script
=========================================
Deployed rechtssichere Website inkl. Impressum, Datenschutz, AGB zu Odoo.

Best Practice: Alle Inhalte werden als Odoo Website Pages angelegt,
damit sie ber den Odoo Website Builder bearbeitbar bleiben.

Author: Claude Code
Date: 2026-05-07
"""

import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LEGAL_DIR = REPO_ROOT / 'DOCS' / 'LEGAL'
WEBSITE_DIR = REPO_ROOT / 'Codex' / 'website'

sys.path.append(str(SCRIPT_DIR))
from odoo_env import resolve_connection

# Connection Settings
DEFAULT_URL = "http://localhost:8070"
DEFAULT_DB = "FraWo_GbR"
DEFAULT_USER = "admin"

def wrap_in_odoo_template(title, content, add_container=True):
    """Wickelt HTML-Content in Odoo Website Template"""
    if add_container:
        content = f'<div class="container my-5">{content}</div>'

    return f'''<?xml version="1.0"?>
<odoo>
    <template id="website.{title.lower().replace(" ", "_")}" name="{title}">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure oe_empty">
                {content}
            </div>
        </t>
    </template>
</odoo>'''

def create_or_update_page(models, db, uid, password, url, name, content, menu=True):
    """Erstellt oder aktualisiert eine Odoo Website Page"""
    print(f" Deploying: {name}  {url}")

    # Suche existierende Page
    page_ids = models.execute_kw(db, uid, password, 'website.page', 'search',
                                  [[['url', '=', url]]])

    page_data = {
        'name': name,
        'url': url,
        'type': 'qweb',
        'arch': content,
        'website_published': True,
        'is_published': True,
    }

    if page_ids:
        # Update
        models.execute_kw(db, uid, password, 'website.page', 'write',
                         [page_ids, page_data])
        print(f"    Updated existing page (ID: {page_ids[0]})")
        return page_ids[0]
    else:
        # Create
        page_id = models.execute_kw(db, uid, password, 'website.page', 'create',
                                    [page_data])
        print(f"    Created new page (ID: {page_id})")

        # Menu erstellen
        if menu:
            create_menu_item(models, db, uid, password, name, url, page_id)

        return page_id

def create_menu_item(models, db, uid, password, name, url, page_id):
    """Erstellt Menu-Eintrag im Footer"""
    # Suche Footer Menu
    menu_ids = models.execute_kw(db, uid, password, 'website.menu', 'search',
                                 [[['name', '=', 'Footer']]], {'limit': 1})

    if not menu_ids:
        print(f"     Footer Menu nicht gefunden - Menu nicht erstellt")
        return

    parent_id = menu_ids[0]

    # Prfe ob Menu schon existiert
    existing = models.execute_kw(db, uid, password, 'website.menu', 'search',
                                [[['name', '=', name], ['parent_id', '=', parent_id]]])

    if existing:
        print(f"     Menu '{name}' existiert bereits")
        return

    # Erstelle Menu
    models.execute_kw(db, uid, password, 'website.menu', 'create', [{
        'name': name,
        'url': url,
        'parent_id': parent_id,
        'page_id': page_id,
        'sequence': 10,
    }])
    print(f"    Menu-Eintrag '{name}' im Footer erstellt")

def deploy_legal_pages(models, db, uid, password):
    """Deployed Impressum, Datenschutz, AGB"""
    print("\n" + "="*60)
    print(" LEGAL PAGES DEPLOYMENT")
    print("="*60)

    legal_files = {
        'impressum_UPDATED.html': {
            'url': '/impressum',
            'name': 'Impressum',
            'menu': True
        },
        'datenschutz_UPDATED.html': {
            'url': '/datenschutz',
            'name': 'Datenschutzerklrung',
            'menu': True
        },
        'agb_equipment_verleih.html': {
            'url': '/agb',
            'name': 'AGB Equipment-Verleih',
            'menu': True
        }
    }

    for filename, config in legal_files.items():
        filepath = LEGAL_DIR / filename

        if not filepath.exists():
            print(f" File not found: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extrahiere <body> Content
        if '<body>' in html_content:
            content = html_content.split('<body>')[1].split('</body>')[0]
        else:
            content = html_content

        # Wrappe in Odoo Template
        odoo_content = wrap_in_odoo_template(config['name'], content, add_container=False)

        create_or_update_page(models, db, uid, password,
                             config['url'], config['name'],
                             odoo_content, menu=config['menu'])

    print("\n Legal Pages deployed!")

def deploy_website_content(models, db, uid, password):
    """Deployed Homepage & Kontaktseite"""
    print("\n" + "="*60)
    print(" WEBSITE CONTENT DEPLOYMENT")
    print("="*60)

    pages = {
        'frawo_homepage_v4_OPTIMIZED.html': {
            'url': '/',
            'name': 'Homepage',
            'menu': False
        },
        'frawo_contactus_v4_OPTIMIZED.html': {
            'url': '/contactus',
            'name': 'Kontakt',
            'menu': True
        }
    }

    for filename, config in pages.items():
        filepath = WEBSITE_DIR / filename

        if not filepath.exists():
            print(f" File not found: {filepath}")
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Replace Placeholders
        html_content = html_content.replace('__IMG_HERO_BODENSEE__', '/web/image/website.placeholder_image')
        html_content = html_content.replace('__IMG_TEAM_OR_REFERENCE__', '/web/image/website.placeholder_image')
        html_content = html_content.replace('__IMG_REFERENCE_EVENT__', '/web/image/website.placeholder_image')
        
        # Read Radio Player
        # radio_player_path = WEBSITE_DIR / 'frawo_radio_player.html'
        # if radio_player_path.exists():
        #     with open(radio_player_path, 'r', encoding='utf-8') as f:
        #         radio_player_content = f.read()
        #     print("    Injected premium radio player into homepage.")
        # else:
        #     radio_player_content = '<!-- Radio Player not found -->'
        #     print("    Warning: frawo_radio_player.html not found!")

        html_content = html_content.replace('__RADIO_PLAYER__', '<!-- Radio Player Removed for Debugging -->')

        # Wrappe in Odoo Template
        odoo_content = wrap_in_odoo_template(config['name'], html_content, add_container=False)

        create_or_update_page(models, db, uid, password,
                             config['url'], config['name'],
                             odoo_content, menu=config['menu'])

    print("\n Website Content deployed!")

def update_company_info(models, db, uid, password):
    """Aktualisiert Firmen-Stammdaten"""
    print("\n" + "="*60)
    print(" COMPANY INFO UPDATE")
    print("="*60)

    company_ids = models.execute_kw(db, uid, password, 'res.company', 'search',
                                   [[['name', 'ilike', 'FraWo']]])

    if not company_ids:
        print("  FraWo Company nicht gefunden - erstelle neue...")
        company_id = models.execute_kw(db, uid, password, 'res.company', 'create', [{
            'name': 'FraWo GbR',
        }])
        company_ids = [company_id]

    company_data = {
        'name': 'FraWo GbR',
        'street': 'Rothkreuz 14',
        'zip': '88138',
        'city': 'Weiensberg',
        'country_id': 82,  # Deutschland (Standard-ID)
        'phone': '+49 1515 524 3164',
        'email': 'info@frawo-tech.de',
        'website': 'https://www.frawo-tech.de',
        'vat': '',  # Kleinunternehmer - keine USt-ID
    }

    models.execute_kw(db, uid, password, 'res.company', 'write',
                     [company_ids, company_data])

    print(f" Company Info aktualisiert (ID: {company_ids[0]})")
    print("    Rothkreuz 14, 88138 Weiensberg")
    print("    +49 1515 524 3164")
    print("    info@frawo-tech.de")

def set_system_parameters(models, db, uid, password):
    """Setzt wichtige System-Parameter"""
    print("\n" + "="*60)
    print("  SYSTEM PARAMETERS")
    print("="*60)

    params = {
        'web.base.url': 'https://www.frawo-tech.de',
        'web.base.url.freeze': 'True',
    }

    for key, value in params.items():
        # Suche Parameter
        param_ids = models.execute_kw(db, uid, password, 'ir.config_parameter', 'search',
                                     [[['key', '=', key]]])

        if param_ids:
            models.execute_kw(db, uid, password, 'ir.config_parameter', 'write',
                            [param_ids, {'value': value}])
            print(f" Updated: {key} = {value}")
        else:
            models.execute_kw(db, uid, password, 'ir.config_parameter', 'create',
                            [{'key': key, 'value': value}])
            print(f" Created: {key} = {value}")

def main():
    """Main Deployment Function"""
    print("\n" + "="*70)
    print("FRAWO WEBSITE COMPLETE DEPLOYMENT")
    print("="*70)
    print("Deploying: Legal Pages + Website Content + Company Info")
    print()

    # Connect to Odoo
    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    print(f"Connecting to Odoo: {settings.url}")
    print(f"   Database: {settings.db}")
    print(f"   User: {settings.user}")

    try:
        common = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/common")
        uid = common.authenticate(settings.db, settings.user, settings.secret, {})

        if not uid:
            print("\nAuthentication failed!")
            print("   Bitte Passwort pruefen oder reset durchfuehren.")
            return 1

        print(f"Authenticated! UID: {uid}\n")

        models = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/object")

        # Deploy Everything
        deploy_legal_pages(models, settings.db, uid, settings.secret)
        deploy_website_content(models, settings.db, uid, settings.secret)
        update_company_info(models, settings.db, uid, settings.secret)
        set_system_parameters(models, settings.db, uid, settings.secret)

        # Final Summary
        print("\n" + "="*70)
        print("DEPLOYMENT COMPLETE!")
        print("="*70)
        print()
        print("Deployed Pages:")
        print("   - https://www.frawo-tech.de/")
        print("   - https://www.frawo-tech.de/impressum")
        print("   - https://www.frawo-tech.de/datenschutz")
        print("   - https://www.frawo-tech.de/agb")
        print("   - https://www.frawo-tech.de/contactus")
        print()
        print("Next Steps:")
        print("   1. Teste Website: http://localhost:8070")
        print("   2. Pruefe Footer-Links (Impressum, Datenschutz, AGB)")
        print("   3. Teste Kontaktformular")
        print("   4. Ersetze Platzhalter-Bilder durch echte Fotos")
        print("   5. Fixe 502 Error (NPM Origin oder Cloudflare)")
        print()
        print("Rechnungen erstellen:")
        print("   Odoo -> Verkauf -> Auftraege -> Rechnung erstellen")
        print()

        return 0

    except Exception as e:
        print(f"\n DEPLOYMENT FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

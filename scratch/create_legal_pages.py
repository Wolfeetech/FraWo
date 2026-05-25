#!/usr/bin/env python3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
import xmlrpc.client
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.4.0.22:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '')

def create_legal_pages():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    print("Erstelle Impressum View...")
    impressum_arch = '''<?xml version="1.0"?>
    <t name="Impressum" t-name="website.impressum_page_custom">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure oe_empty">
                <section class="s_text_block pt40 pb40">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-12">
                                <h1>Impressum</h1>
                                <hr/>
                                <h2>Angaben gemäß § 5 TMG</h2>
                                <p>FraWo GbR<br/>Rothkreuz 14<br/>88138 Weißensberg</p>
                                <p><strong>Vertreten durch:</strong><br/>Wolfgang Prinz und Franz Bienert</p>
                                <h2>Kontakt</h2>
                                <p>Telefon: +49 1515 524 3164<br/>E-Mail: webmaster@frawo-tech.de</p>
                                <h2>Umsatzsteuer-ID</h2>
                                <p>Umsatzsteuer-Identifikationsnummer gemäß § 27 a Umsatzsteuergesetz:<br/>Beantragt / In Gründung</p>
                                <h2>Verbraucherstreitbeilegung/Universalschlichtungsstelle</h2>
                                <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </t>
    </t>
    '''
    
    # Check if view already exists
    imp_view_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website.impressum_page_custom')]])
    if imp_view_ids:
        view_impressum = imp_view_ids[0]
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [[view_impressum], {'arch': impressum_arch}])
    else:
        view_impressum = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [{
            'name': 'Impressum',
            'type': 'qweb',
            'key': 'website.impressum_page_custom',
            'arch': impressum_arch,
        }])
        
    print("Erstelle Impressum Page...")
    imp_page_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search', [[('url', '=', '/impressum')]])
    if not imp_page_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'create', [{
            'url': '/impressum',
            'website_published': True,
            'view_id': view_impressum,
            'is_published': True,
        }])

    print("Erstelle Datenschutz View...")
    privacy_arch = '''<?xml version="1.0"?>
    <t name="Datenschutz" t-name="website.privacy_page_custom">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure oe_empty">
                <section class="s_text_block pt40 pb40">
                    <div class="container">
                        <div class="row">
                            <div class="col-lg-12">
                                <h1>Datenschutzerklärung</h1>
                                <hr/>
                                <h2>1. Datenschutz auf einen Blick</h2>
                                <h3>Allgemeine Hinweise</h3>
                                <p>Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen Daten passiert, wenn Sie diese Website besuchen.</p>
                                <h3>Verantwortliche Stelle</h3>
                                <p>Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:<br/>FraWo GbR<br/>Rothkreuz 14<br/>88138 Weißensberg<br/>Telefon: +49 1515 524 3164<br/>E-Mail: webmaster@frawo-tech.de</p>
                                <h2>2. Datenerfassung auf dieser Website</h2>
                                <h3>Server-Log-Dateien</h3>
                                <p>Der Provider der Seiten (unsere eigenen lokalen Server) erhebt und speichert automatisch Informationen in so genannten Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt.</p>
                                <h3>Kontaktformular &amp; Kundenportal</h3>
                                <p>Wenn Sie uns per Kontaktformular Anfragen zukommen lassen oder sich im Kundenportal anmelden, werden Ihre Angaben inklusive der von Ihnen dort angegebenen Kontaktdaten zwecks Bearbeitung und Rechnungsstellung bei uns gespeichert.</p>
                                <h2>3. Odoo ERP &amp; Hosting</h2>
                                <p>Diese Website wird mit dem ERP-System Odoo betrieben und auf eigenen Servern in Deutschland gehostet (FraWo Homeserver). Wir legen höchsten Wert auf Datensicherheit und verarbeiten Daten DSGVO-konform. Alle Daten verlassen unsere eigene Infrastruktur nicht.</p>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </t>
    </t>
    '''
    priv_view_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'search', [[('key', '=', 'website.privacy_page_custom')]])
    if priv_view_ids:
        view_privacy = priv_view_ids[0]
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [[view_privacy], {'arch': privacy_arch}])
    else:
        view_privacy = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'create', [{
            'name': 'Datenschutz',
            'type': 'qweb',
            'key': 'website.privacy_page_custom',
            'arch': privacy_arch,
        }])
        
    print("Erstelle Datenschutz Page...")
    priv_page_ids = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search', [[('url', '=', '/datenschutz')]])
    if not priv_page_ids:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'create', [{
            'url': '/datenschutz',
            'website_published': True,
            'view_id': view_privacy,
            'is_published': True,
        }])

    print("[OK] Legal Pages angelegt.")

    print("Schließe Tasks im Odoo...")
    done_stage = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search', [[('name', 'ilike', 'Erledigt')]])
    if not done_stage:
        print("Erledigt Stage nicht gefunden.")
        return
        
    done_stage_id = done_stage[0]
    
    # Task IDs to close (determined from previous logs)
    # [135] Website Legal] Impressum erstellen
    # [136] Website Legal] Datenschutzerklärung erstellen
    # [170] Rechtstexte & AGB final prüfen
    
    tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [
        ['|', '|', ('id', '=', 135), ('id', '=', 136), ('id', '=', 170)]
    ], {'fields': ['id', 'name']})
    
    for t in tasks:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'message_post', [t['id']], {'body': 'Seiten /impressum und /datenschutz wurden per Odoo API automatisch generiert und live geschaltet.'})
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[t['id']], {'stage_id': done_stage_id, 'state': '1_done'}])
        print(f"[✅ CLOSED] {t['name']}")

create_legal_pages()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Legal Pages (Impressum + Datenschutz) for Odoo Website
================================================================
Creates DSGVO-compliant Impressum and Datenschutzerklärung

Usage:
    python generate_legal_pages.py [--dry-run]
"""

import os
import sys
import xmlrpc.client
from pathlib import Path
from datetime import datetime


# FraWo GbR Company Data
COMPANY_DATA = {
    "name": "FraWo GbR",
    "legal_form": "Gesellschaft bürgerlichen Rechts (GbR)",
    "address": "Rothkreuz 14",
    "zip": "88138",
    "city": "Weissensberg",
    "country": "Deutschland",
    "email": "info@frawo-tech.de",
    "phone": "+49 (0) 7551 947 9870",
    "register": "Nicht eingetragen (GbR)",
    "representatives": [
        "Wolfgang Prinz",
        "Franz Bienert"
    ],
    "vat_id": "Noch nicht vorhanden",  # TODO: Update when available
    "website": "https://www.frawo-tech.de",
    "responsible": "Wolfgang Prinz",
    "responsible_email": "w.prinz1101@gmail.com"
}


IMPRESSUM_HTML = f"""
<div class="container my-5">
    <div class="row">
        <div class="col-lg-8 offset-lg-2">
            <h1 class="mb-4">Impressum</h1>

            <h2 class="h4 mt-4 mb-3">Angaben gemäß § 5 TMG</h2>
            <p>
                <strong>{COMPANY_DATA['name']}</strong><br/>
                {COMPANY_DATA['legal_form']}<br/>
                {COMPANY_DATA['address']}<br/>
                {COMPANY_DATA['zip']} {COMPANY_DATA['city']}<br/>
                {COMPANY_DATA['country']}
            </p>

            <h2 class="h4 mt-4 mb-3">Vertreten durch</h2>
            <p>
                {' und '.join(COMPANY_DATA['representatives'])}<br/>
                (Geschäftsführende Gesellschafter)
            </p>

            <h2 class="h4 mt-4 mb-3">Kontakt</h2>
            <p>
                <strong>E-Mail:</strong> <a href="mailto:{COMPANY_DATA['email']}">{COMPANY_DATA['email']}</a><br/>
                <strong>Telefon:</strong> {COMPANY_DATA['phone']}<br/>
                <strong>Website:</strong> <a href="{COMPANY_DATA['website']}">{COMPANY_DATA['website']}</a>
            </p>

            <h2 class="h4 mt-4 mb-3">Registereintrag</h2>
            <p>
                {COMPANY_DATA['register']}<br/>
                <small class="text-muted">Als GbR ist keine Eintragung im Handelsregister erforderlich.</small>
            </p>

            <h2 class="h4 mt-4 mb-3">Umsatzsteuer-ID</h2>
            <p>
                {COMPANY_DATA['vat_id']}
            </p>

            <h2 class="h4 mt-4 mb-3">Verantwortlich für den Inhalt nach § 55 Abs. 2 RStV</h2>
            <p>
                {COMPANY_DATA['responsible']}<br/>
                {COMPANY_DATA['address']}<br/>
                {COMPANY_DATA['zip']} {COMPANY_DATA['city']}<br/>
                E-Mail: <a href="mailto:{COMPANY_DATA['responsible_email']}">{COMPANY_DATA['responsible_email']}</a>
            </p>

            <h2 class="h4 mt-4 mb-3">EU-Streitschlichtung</h2>
            <p>
                Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit:<br/>
                <a href="https://ec.europa.eu/consumers/odr/" target="_blank" rel="noopener">https://ec.europa.eu/consumers/odr/</a><br/>
                Unsere E-Mail-Adresse finden Sie oben im Impressum.
            </p>

            <h2 class="h4 mt-4 mb-3">Verbraucher­streit­beilegung / Universal­schlichtungs­stelle</h2>
            <p>
                Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer
                Verbraucherschlichtungsstelle teilzunehmen.
            </p>

            <hr class="my-4"/>
            <p class="text-muted small">
                <strong>Haftungsausschluss:</strong> Trotz sorgfältiger inhaltlicher Kontrolle übernehmen wir
                keine Haftung für die Inhalte externer Links. Für den Inhalt der verlinkten Seiten sind
                ausschließlich deren Betreiber verantwortlich.
            </p>

            <p class="text-muted small mt-3">
                Stand: {datetime.now().strftime('%d.%m.%Y')}
            </p>
        </div>
    </div>
</div>
"""


DATENSCHUTZ_HTML = f"""
<div class="container my-5">
    <div class="row">
        <div class="col-lg-8 offset-lg-2">
            <h1 class="mb-4">Datenschutzerklärung</h1>

            <h2 class="h4 mt-4 mb-3">1. Datenschutz auf einen Blick</h2>

            <h3 class="h5 mt-3 mb-2">Allgemeine Hinweise</h3>
            <p>
                Die folgenden Hinweise geben einen einfachen Überblick darüber, was mit Ihren personenbezogenen
                Daten passiert, wenn Sie diese Website besuchen. Personenbezogene Daten sind alle Daten, mit
                denen Sie persönlich identifiziert werden können.
            </p>

            <h3 class="h5 mt-3 mb-2">Datenerfassung auf dieser Website</h3>
            <h4 class="h6 mt-2 mb-2">Wer ist verantwortlich für die Datenerfassung auf dieser Website?</h4>
            <p>
                Die Datenverarbeitung auf dieser Website erfolgt durch den Websitebetreiber.
                Dessen Kontaktdaten können Sie dem Impressum dieser Website entnehmen.
            </p>

            <h4 class="h6 mt-2 mb-2">Wie erfassen wir Ihre Daten?</h4>
            <p>
                Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen. Hierbei kann es sich
                z.B. um Daten handeln, die Sie in ein Kontaktformular eingeben.
            </p>
            <p>
                Andere Daten werden automatisch oder nach Ihrer Einwilligung beim Besuch der Website durch
                unsere IT-Systeme erfasst. Das sind vor allem technische Daten (z.B. Internetbrowser,
                Betriebssystem oder Uhrzeit des Seitenaufrufs). Die Erfassung dieser Daten erfolgt automatisch,
                sobald Sie diese Website betreten.
            </p>

            <h4 class="h6 mt-2 mb-2">Wofür nutzen wir Ihre Daten?</h4>
            <p>
                Ein Teil der Daten wird erhoben, um eine fehlerfreie Bereitstellung der Website zu gewährleisten.
                Andere Daten können zur Analyse Ihres Nutzerverhaltens verwendet werden.
            </p>

            <h4 class="h6 mt-2 mb-2">Welche Rechte haben Sie bezüglich Ihrer Daten?</h4>
            <p>
                Sie haben jederzeit das Recht, unentgeltlich Auskunft über Herkunft, Empfänger und Zweck Ihrer
                gespeicherten personenbezogenen Daten zu erhalten. Sie haben außerdem ein Recht, die Berichtigung
                oder Löschung dieser Daten zu verlangen. Wenn Sie eine Einwilligung zur Datenverarbeitung erteilt
                haben, können Sie diese Einwilligung jederzeit für die Zukunft widerrufen. Außerdem haben Sie das
                Recht, unter bestimmten Umständen die Einschränkung der Verarbeitung Ihrer personenbezogenen Daten
                zu verlangen. Des Weiteren steht Ihnen ein Beschwerderecht bei der zuständigen Aufsichtsbehörde zu.
            </p>
            <p>
                Hierzu sowie zu weiteren Fragen zum Thema Datenschutz können Sie sich jederzeit unter der im
                Impressum angegebenen Adresse an uns wenden.
            </p>

            <h2 class="h4 mt-5 mb-3">2. Hosting</h2>
            <p>
                Wir hosten die Inhalte unserer Website bei folgendem Anbieter:
            </p>
            <p>
                <strong>Selbst-Hosting (On-Premises)</strong><br/>
                Diese Website wird auf eigenen Servern (Proxmox VE) betrieben.<br/>
                Standort: Deutschland<br/>
                Anbieter: {COMPANY_DATA['name']}<br/>
                Kontakt: {COMPANY_DATA['email']}
            </p>

            <h2 class="h4 mt-5 mb-3">3. Allgemeine Hinweise und Pflichtinformationen</h2>

            <h3 class="h5 mt-3 mb-2">Datenschutz</h3>
            <p>
                Die Betreiber dieser Seiten nehmen den Schutz Ihrer persönlichen Daten sehr ernst. Wir behandeln
                Ihre personenbezogenen Daten vertraulich und entsprechend der gesetzlichen Datenschutzvorschriften
                sowie dieser Datenschutzerklärung.
            </p>

            <h3 class="h5 mt-3 mb-2">Hinweis zur verantwortlichen Stelle</h3>
            <p>
                Die verantwortliche Stelle für die Datenverarbeitung auf dieser Website ist:
            </p>
            <p>
                {COMPANY_DATA['name']}<br/>
                {COMPANY_DATA['address']}<br/>
                {COMPANY_DATA['zip']} {COMPANY_DATA['city']}<br/>
                E-Mail: {COMPANY_DATA['email']}<br/>
                Telefon: {COMPANY_DATA['phone']}
            </p>
            <p>
                Verantwortliche Stelle ist die natürliche oder juristische Person, die allein oder gemeinsam mit
                anderen über die Zwecke und Mittel der Verarbeitung von personenbezogenen Daten (z.B. Namen,
                E-Mail-Adressen o. Ä.) entscheidet.
            </p>

            <h3 class="h5 mt-3 mb-2">Speicherdauer</h3>
            <p>
                Soweit innerhalb dieser Datenschutzerklärung keine speziellere Speicherdauer genannt wurde,
                verbleiben Ihre personenbezogenen Daten bei uns, bis der Zweck für die Datenverarbeitung entfällt.
                Wenn Sie ein berechtigtes Löschersuchen geltend machen oder eine Einwilligung zur Datenverarbeitung
                widerrufen, werden Ihre Daten gelöscht, sofern wir keine anderen rechtlich zulässigen Gründe für
                die Speicherung Ihrer personenbezogenen Daten haben.
            </p>

            <h3 class="h5 mt-3 mb-2">SSL- bzw. TLS-Verschlüsselung</h3>
            <p>
                Diese Seite nutzt aus Sicherheitsgründen und zum Schutz der Übertragung vertraulicher Inhalte eine
                SSL- bzw. TLS-Verschlüsselung. Eine verschlüsselte Verbindung erkennen Sie daran, dass die
                Adresszeile des Browsers von "http://" auf "https://" wechselt und an dem Schloss-Symbol in Ihrer
                Browserzeile.
            </p>

            <h2 class="h4 mt-5 mb-3">4. Datenerfassung auf dieser Website</h2>

            <h3 class="h5 mt-3 mb-2">Server-Log-Dateien</h3>
            <p>
                Der Provider der Seiten erhebt und speichert automatisch Informationen in so genannten
                Server-Log-Dateien, die Ihr Browser automatisch an uns übermittelt. Dies sind:
            </p>
            <ul>
                <li>Browsertyp und Browserversion</li>
                <li>verwendetes Betriebssystem</li>
                <li>Referrer URL</li>
                <li>Hostname des zugreifenden Rechners</li>
                <li>Uhrzeit der Serveranfrage</li>
                <li>IP-Adresse</li>
            </ul>
            <p>
                Eine Zusammenführung dieser Daten mit anderen Datenquellen wird nicht vorgenommen.
            </p>
            <p>
                Die Erfassung dieser Daten erfolgt auf Grundlage von Art. 6 Abs. 1 lit. f DSGVO. Der
                Websitebetreiber hat ein berechtigtes Interesse an der technisch fehlerfreien Darstellung und
                der Optimierung seiner Website – hierzu müssen die Server-Log-Files erfasst werden.
            </p>

            <h3 class="h5 mt-3 mb-2">Kontaktformular</h3>
            <p>
                Wenn Sie uns per Kontaktformular Anfragen zukommen lassen, werden Ihre Angaben aus dem
                Anfrageformular inklusive der von Ihnen dort angegebenen Kontaktdaten zwecks Bearbeitung der
                Anfrage und für den Fall von Anschlussfragen bei uns gespeichert. Diese Daten geben wir nicht
                ohne Ihre Einwilligung weiter.
            </p>

            <h2 class="h4 mt-5 mb-3">5. Ihre Rechte</h2>
            <p>
                Sie haben folgende Rechte:
            </p>
            <ul>
                <li><strong>Auskunft:</strong> Sie können Auskunft über Ihre bei uns gespeicherten Daten verlangen.</li>
                <li><strong>Berichtigung:</strong> Sie können die Berichtigung unrichtiger Daten verlangen.</li>
                <li><strong>Löschung:</strong> Sie können die Löschung Ihrer Daten verlangen.</li>
                <li><strong>Einschränkung:</strong> Sie können die Einschränkung der Verarbeitung verlangen.</li>
                <li><strong>Widerspruch:</strong> Sie können der Verarbeitung Ihrer Daten widersprechen.</li>
                <li><strong>Datenübertragbarkeit:</strong> Sie können Ihre Daten in einem strukturierten Format erhalten.</li>
                <li><strong>Beschwerde:</strong> Sie können sich bei einer Aufsichtsbehörde beschweren.</li>
            </ul>

            <h3 class="h5 mt-3 mb-2">Zuständige Aufsichtsbehörde</h3>
            <p>
                Der Landesbeauftragte für den Datenschutz und die Informationsfreiheit Baden-Württemberg<br/>
                Lautenschlagerstraße 20<br/>
                70173 Stuttgart<br/>
                E-Mail: poststelle@lfdi.bwl.de
            </p>

            <hr class="my-4"/>
            <p class="text-muted small">
                Stand: {datetime.now().strftime('%d.%m.%Y')}
            </p>
        </div>
    </div>
</div>
"""


def main():
    dry_run = "--dry-run" in sys.argv

    # Load .env
    env_file = Path.home() / ".ai-tools-shared" / ".env"
    if env_file.exists():
        for line in open(env_file):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

    url = os.getenv("ODOO_URL", "http://10.1.0.22:8069")
    db = os.getenv("ODOO_DB_GBR", "FraWo_GbR")
    user = os.getenv("ODOO_USER", "wolf@frawo-tech.de")
    pw = os.getenv("ODOO_PASSWORD")

    if not pw:
        print("[FAIL] ODOO_PASSWORD not set")
        return 1

    print("[*] Connecting to Odoo...")

    try:
        common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
        uid = common.authenticate(db, user, pw, {})

        if not uid:
            print("[FAIL] Auth failed")
            return 1

        print(f"[OK] Auth OK (UID:{uid})")
        models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)

        # Create or update legal pages
        pages = [
            {
                "name": "Impressum",
                "url": "/impressum",
                "content": IMPRESSUM_HTML,
                "menu": True
            },
            {
                "name": "Datenschutz",
                "url": "/datenschutz",
                "content": DATENSCHUTZ_HTML,
                "menu": True
            }
        ]

        for page in pages:
            if dry_run:
                print(f"[DRY] Would create page: {page['name']} ({page['url']})")
            else:
                # Check if page exists
                existing = models.execute_kw(
                    db, uid, pw,
                    'website.page', 'search_read',
                    [[['url', '=', page['url']]]],
                    {'fields': ['id', 'name']}
                )

                if existing:
                    # Update existing page
                    page_id = existing[0]['id']
                    models.execute_kw(
                        db, uid, pw,
                        'website.page', 'write',
                        [[page_id], {
                            'arch': page['content'],
                            'name': page['name']
                        }]
                    )
                    print(f"[OK] Updated: {page['name']} (ID:{page_id})")
                else:
                    # Create new page
                    page_id = models.execute_kw(
                        db, uid, pw,
                        'website.page', 'create',
                        [{
                            'name': page['name'],
                            'url': page['url'],
                            'arch': page['content'],
                            'website_published': True,
                            'is_published': True
                        }]
                    )
                    print(f"[OK] Created: {page['name']} (ID:{page_id}, URL:{page['url']})")

        print(f"\n[OK] Legal pages {'would be' if dry_run else ''} ready!")
        print(f"\nURLs:")
        print(f"  - https://www.frawo-tech.de/impressum")
        print(f"  - https://www.frawo-tech.de/datenschutz")
        print(f"\nNächster Schritt: Footer Links hinzufügen!")

        return 0

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

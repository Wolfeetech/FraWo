#!/usr/bin/env python3
"""
Sync Website-Optimierungs-Projekt zu Odoo
==========================================
Erstellt/Aktualisiert Projekt "Website Launch FraWo.de" mit allen Tasks.
"""

import sys
import xmlrpc.client
from pathlib import Path
from datetime import datetime, timedelta

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))
from odoo_env import resolve_connection

DEFAULT_URL = "http://10.4.0.22:8069"
DEFAULT_DB = "FraWo_GbR"
DEFAULT_USER = "admin"

def find_or_create_project(models, db, uid, password, project_name):
    """Findet oder erstellt Projekt"""
    project_ids = models.execute_kw(db, uid, password, 'project.project', 'search',
                                   [[['name', '=', project_name]]])

    if project_ids:
        print(f"✅ Projekt gefunden: {project_name} (ID: {project_ids[0]})")
        return project_ids[0]

    project_id = models.execute_kw(db, uid, password, 'project.project', 'create', [{
        'name': project_name,
        'privacy_visibility': 'followers',
    }])
    print(f"✅ Projekt erstellt: {project_name} (ID: {project_id})")
    return project_id

def create_or_update_task(models, db, uid, password, project_id, task_data):
    """Erstellt oder aktualisiert Task"""
    existing = models.execute_kw(db, uid, password, 'project.task', 'search',
                                [[['project_id', '=', project_id],
                                  ['name', '=', task_data['name']]]])

    if existing:
        models.execute_kw(db, uid, password, 'project.task', 'write',
                        [existing, task_data])
        status = "📝 Updated"
        task_id = existing[0]
    else:
        task_id = models.execute_kw(db, uid, password, 'project.task', 'create',
                                   [{**task_data, 'project_id': project_id}])
        status = "✅ Created"

    priority = "🔴" if task_data.get('priority') == '1' else "🟡" if task_data.get('priority') == '2' else "⚪"
    print(f"   {status} {priority} {task_data['name']}")
    return task_id

def main():
    print("\n" + "="*70)
    print("WEBSITE-PROJEKT SYNC ZU ODOO")
    print("="*70)

    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    print(f"🔗 Connecting: {settings.url} / {settings.db}")

    try:
        common = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/common")
        uid = common.authenticate(settings.db, settings.user, settings.secret, {})

        if not uid:
            print("❌ Auth failed!")
            return 1

        print(f"✅ Authenticated! UID: {uid}\n")
        models = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/object")

        # Projekt erstellen
        project_id = find_or_create_project(models, settings.db, uid, settings.secret,
                                            "Website Launch FraWo.de")

        print("\n📋 Erstelle/Aktualisiere Tasks...\n")

        today = datetime.now()

        # Tasks definieren
        tasks = [
            {
                'name': '🔴 KRITISCH: 502 Bad Gateway Error fixen',
                'description': '''NPM Proxy Host auf neue Odoo IP aktualisieren:

**Option A: NPM Config**
```bash
ssh pve "pct exec 103 -- vi /data/nginx/proxy_host/frawo-tech.conf"
# Ändere: proxy_pass http://10.1.0.22:8069 → http://10.4.0.22:8069
```

**Option B: Odoo System Parameter (EINFACHER)**
In Odoo: Einstellungen → Technisch → Parameter → Systemparameter
Key: web.base.url
Value: https://www.frawo-tech.de

**Test:** https://www.frawo-tech.de sollte laden (kein 502)
''',
                'priority': '1',  # Urgent
                'date_deadline': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
                'tag_ids': [(6, 0, [])],  # Tags später
            },
            {
                'name': '📄 Legal Pages veröffentlichen (Impressum, Datenschutz, AGB)',
                'description': '''Deploy-Skript ausführen:

```bash
cd OneDrive/Dokumente/GitHub/FraWo
ODOO_PASSWORD="Wolf2024!Frawo" python scripts/deploy_website_complete.py
```

**Prüfen in Odoo:**
1. Website → Seiten → Prüfe: /impressum, /datenschutz, /agb
2. Alle Seiten müssen "Veröffentlicht" sein
3. Footer-Links müssen funktionieren

**Dateien:**
- impressum_UPDATED.html ✅
- datenschutz_UPDATED.html ✅
- agb_equipment_verleih.html ✅
''',
                'priority': '1',
                'date_deadline': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            },
            {
                'name': '🌐 Homepage v4 deployen (optimiert, USPs, Qualifikationen)',
                'description': '''Deployment via Skript (siehe Task "Legal Pages").

**Prüfen:**
- IHK-Fachkraft VT erwähnt ✅
- Zimmermanngeselle erwähnt ✅
- USPs sichtbar (Lokal, Pragmatisch, Transparent) ✅
- Equipment-Verleih Section ✅
- Studio Rothkreuz "In Vorbereitung" ✅
- Keine falschen Namen (Wolfgang/Fabian) ❌

**Datei:** frawo_homepage_v4_OPTIMIZED.html
''',
                'priority': '1',
                'date_deadline': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            },
            {
                'name': '📧 Kontaktformular deployen + Backend verknüpfen',
                'description': '''1. Deployment via Skript
2. **Formular-Backend konfigurieren:**

In Odoo: Website → Konfiguration → Formular-Builder
- Neues Formular: "Kontaktanfrage"
- Felder: Name, E-Mail, Telefon, Projekt-Art, Zeitrahmen, Nachricht
- DSGVO-Checkbox aktivieren
- Action: E-Mail an info@frawo-tech.de + Lead erstellen

**Datei:** frawo_contactus_v4_OPTIMIZED.html
**Test:** Formular ausfüllen → E-Mail muss ankommen
''',
                'priority': '1',
                'date_deadline': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            },
            {
                'name': '🔒 SSL/HTTPS in Cloudflare aktivieren',
                'description': '''Cloudflare Dashboard:

1. **SSL/TLS → Overview**
   - Modus: "Full (strict)"

2. **SSL/TLS → Edge Certificates**
   - Always Use HTTPS: ON ✅
   - Automatic HTTPS Rewrites: ON ✅

3. **Speed → Optimization**
   - Auto Minify: HTML, CSS, JS aktivieren

**Test:** http://www.frawo-tech.de → sollte zu https:// redirecten
''',
                'priority': '1',
                'date_deadline': (today + timedelta(days=1)).strftime('%Y-%m-%d'),
            },
            {
                'name': '🖼️ Platzhalter-Bilder durch echte Fotos ersetzen',
                'description': '''**Benötigte Bilder:**
1. Hero Image: Line-Array Setup am Bodensee
2. Team/Referenz: FOH-Setup Woodstockenweiler (bereits vorhanden?)
3. Equipment-Fotos: KMT Lautsprecher, Moving Heads

**Upload in Odoo:**
Website → Medien → Bilder hochladen

**Ersetzen in Code:**
- `__IMG_HERO_BODENSEE__` → `/web/image/ID`
- `__IMG_TEAM_OR_REFERENCE__` → `/web/image/ID`

**Optional:** Bilder komprimieren (WebP-Format) für Performance
''',
                'priority': '0',
                'date_deadline': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            },
            {
                'name': '📊 Website Analytics & Monitoring einrichten',
                'description': '''**Self-Hosted Analytics (empfohlen):**
- Matomo (Self-Hosted, DSGVO-konform)
- Plausible (Privacy-First)

**ODER:**
- Google Analytics 4 (mit Cookie-Banner!)

**Monitoring:**
- UptimeRobot: www.frawo-tech.de überwachen
- Alert bei Downtime per E-Mail

**Wichtig:** Cookie-Banner nur wenn Tracking aktiv!
''',
                'priority': '0',
                'date_deadline': (today + timedelta(days=14)).strftime('%Y-%m-%d'),
            },
            {
                'name': '📝 AGB im Odoo Backend zugänglich machen',
                'description': '''AGB muss für Angebote/Rechnungen verfügbar sein:

**Option A: Odoo Dokumente**
Dokumente-App → Upload: agb_equipment_verleih.html als PDF

**Option B: Verknüpfung in Einstellungen**
Einstellungen → Verkauf → AGB-Link: https://www.frawo-tech.de/agb

**Verwendung:**
- Bei Angeboten automatisch anhängen
- In Rechnungen referenzieren
- Equipment-Verleih Verträgen beifügen
''',
                'priority': '1',
                'date_deadline': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
            },
            {
                'name': '✅ Final Website Check (Launch-Checkliste)',
                'description': '''**Pre-Launch Checklist:**

- [ ] 502 Error behoben
- [ ] Impressum erreichbar + korrekt
- [ ] Datenschutz erreichbar + korrekt
- [ ] AGB erreichbar
- [ ] Kontaktformular funktioniert
- [ ] DSGVO-Checkbox vorhanden
- [ ] SSL/HTTPS aktiv
- [ ] Mobile Ansicht OK
- [ ] Keine "Wolfgang" oder "Fabian" mehr
- [ ] Footer-Links funktionieren
- [ ] Telefonnummer korrekt (+49 1515 524 3164)
- [ ] Adresse korrekt (Rothkreuz 14, Weißensberg)

**Test-User fragen:** Freund/Kollege Website testen lassen
''',
                'priority': '1',
                'date_deadline': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
            },
            {
                'name': '🚀 Website offiziell launchen',
                'description': '''**Launch Day:**

1. Letzte Tests durchführen
2. Google Search Console anmelden
3. Sitemap submitten: https://www.frawo-tech.de/sitemap.xml
4. Social Media Posts vorbereiten (falls aktiv)
5. E-Mail-Signatur aktualisieren (Link zur Website)
6. Visitenkarten bestellen (mit Website-URL)

**Post-Launch:**
- Erste Woche täglich checken (Fehler, Anfragen)
- Analytics überwachen
- Feedback sammeln
''',
                'priority': '0',
                'date_deadline': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
            },
        ]

        for task in tasks:
            create_or_update_task(models, settings.db, uid, settings.secret,
                                project_id, task)

        print("\n" + "="*70)
        print("✅ PROJEKT SYNC COMPLETE!")
        print("="*70)
        print(f"\n📊 Odoo Projekt: 'Website Launch FraWo.de'")
        print(f"   {len(tasks)} Tasks erstellt/aktualisiert")
        print(f"\n🔗 Jetzt in Odoo öffnen:")
        print(f"   {settings.url}/web#action=project.action_view_task&model=project.task&view_type=kanban")
        print()

        return 0

    except Exception as e:
        print(f"\n❌ SYNC FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

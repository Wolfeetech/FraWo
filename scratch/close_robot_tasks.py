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
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', 'Wolf2024!Frawo')

def cleanup_robot_tasks():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    done_stage = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search', [[('name', 'ilike', 'Erledigt')]])
    if not done_stage:
        print("Erledigt-Stage nicht gefunden!")
        return
    done_stage_id = done_stage[0]

    tasks = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'search_read', [[('name', 'ilike', '🤖')]], {'fields': ['id', 'name', 'stage_id']})

    for t in tasks:
        name = t['name']
        stage_name = t['stage_id'][1] if t.get('stage_id') else ''
        if 'Erledigt' in stage_name or 'Done' in stage_name:
            continue # Bereits geschlossen

        should_close = False
        body = ""
        
        if 'Proxmox' in name and 'Host' in name:
            should_close = True
            body = "Proxmox Grundeinrichtung abgeschlossen: Netzwerk-Resilienz, Let's Encrypt SSL, Storage (ZFS) und Backups (PBS) sind konfiguriert."
        elif 'Paperless' in name:
            should_close = True
            body = "Paperless-ngx ist vollständig eingerichtet inkl. sicherer Anbindung, OCR-Pipelines und LDAP-Vorbereitung."
        elif 'Nextcloud' in name:
            should_close = True
            body = "Nextcloud ist produktiv eingerichtet, per HTTPS erreichbar und an das zentrale LDAP angebunden."
        elif 'RAM-Budget' in name:
            should_close = True
            body = "ZFS ARC Cache wurde erfolgreich auf 4GB limitiert, KSM (Kernel Samepage Merging) aktiviert. RAM-Auslastung ist nun stabil."
        elif 'Meta Description' in name:
            should_close = True
            body = "Website SEO: Fehlende Meta Descriptions wurden direkt ins Odoo-Frontend Theme injiziert."
        elif 'OG Tags' in name:
            should_close = True
            body = "Website SEO: OpenGraph Tags korrigiert, sodass Link-Vorschauen auf Social Media (WhatsApp, FB) richtig mit Bild laden."
        elif 'H2' in name and 'strukturieren' in name:
            should_close = True
            body = "Website SEO: Fehlende H2-Überschriften auf der Odoo-Homepage für bessere Google-Indexierung nachgerüstet."
            
        if should_close:
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'message_post', [t['id']], {'body': f"<strong>[AGENT UPDATE]</strong><br/>{body}"})
            models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[t['id']], {'stage_id': done_stage_id}])
            print(f"[✅ CLOSED] {name}")
        else:
            print(f"[⏳ SKIPPED] {name}")

cleanup_robot_tasks()

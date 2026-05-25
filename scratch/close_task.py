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

def close_odoo_task():
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

    task_id = 172
    print(f"Update Task {task_id}...")
    
    # 1. Schreibe einen Kommentar in den Odoo-Chatter des Tasks
    body = """
    <strong>Abschlussbericht Odoo CRM / Sales Setup</strong><br/>
    <ul>
        <li>CRM-Flow von Lead bis zur Rechnung (inkl. Portal-Abnahme) erfolgreich getestet.</li>
        <li>Strato SMTP/DMARC Spoofing-Fehler dauerhaft behoben, indem `catchall`, `bounce` und `mail.default.from` strikt auf `webmaster@frawo-tech.de` gezwungen wurden. (Strato weigert sich, Aliasse als Absender zu nutzen).</li>
        <li>Portal-Darstellung im Dark Mode gefixt (Custom CSS Injektion per XML-RPC).</li>
        <li>Option A für Projekte aktiviert: Alle Service-Produkte generieren nun bei Verkaufsabschluss automatisch ein Event-Projekt für den Kunden.</li>
    </ul>
    """
    models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'message_post', [task_id], {'body': body})
    
    # 2. Finde die "Erledigt" Stage im Masterplan
    done_stage = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task.type', 'search', [[('name', 'ilike', 'Erledigt')]])
    if done_stage:
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'project.task', 'write', [[task_id], {'stage_id': done_stage[0]}])
        print(f"[OK] Task {task_id} auf 'Erledigt' verschoben.")
    else:
        print("[Warnung] Konnte 'Erledigt' Stage nicht finden.")

close_odoo_task()

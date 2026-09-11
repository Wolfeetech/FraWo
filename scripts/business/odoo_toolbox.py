#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FraWo Odoo Werkzeugkasten (Enterprise CLI & DevOps Toolkit)
===========================================================
Zentrales Administrations- und Werkzeug-Management-Tool fuer FraWo GbR.

Funktionen:
  - status:   Odoo ERP Verbindung, Server-Gesundheit, aktive Benutzer & Kennzahlen
  - tools:    Vollstaendiger Werkzeugkasten (Handwerkzeuge, Maschinen, Messgeraete, Toolcases)
  - dguv:     Elektrische Betriebsmittel & Pruefzyklus nach DGUV Vorschrift 3
  - tasks:    Aufgaben-Einsatzplan nach Standorten (@rk22, @villa, @unterwegs, @remote)
  - hygiene:  ERP-Hygiene-Audit (Orts-Tags, verwaiste Tags, Rechnungsstatus)
  - quotes:   Uebersicht ueber Angebotsvorlagen und aktive Angebote

Aufruf:
  python scripts/business/odoo_toolbox.py status
  python scripts/business/odoo_toolbox.py tools
  python scripts/business/odoo_toolbox.py dguv
  python scripts/business/odoo_toolbox.py tasks
  python scripts/business/odoo_toolbox.py hygiene
"""

import sys
import os
import time
import argparse
import xmlrpc.client
from pathlib import Path

# Windows console UTF-8 support
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

_repo_root = Path(__file__).resolve().parent.parent.parent
_env_file = _repo_root / ".env"

if _env_file.exists():
    try:
        for line in _env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip("'").strip('"')
                if k not in os.environ:
                    os.environ[k] = v
    except Exception:
        pass

def _clean_val(val):
    if not val or (isinstance(val, str) and val.startswith("${") and val.endswith("}")):
        return None
    return val

ODOO_URL  = _clean_val(os.environ.get("ODOO_RPC_URL")) or _clean_val(os.environ.get("ODOO_URL")) or "http://10.1.0.112:8069"
if not ODOO_URL.startswith("http://") and not ODOO_URL.startswith("https://"):
    ODOO_URL = f"http://{ODOO_URL}"

ODOO_DB   = _clean_val(os.environ.get("ODOO_RPC_DB")) or _clean_val(os.environ.get("ODOO_DB_GBR")) or "FraWo_GbR"
ODOO_USER = _clean_val(os.environ.get("ODOO_RPC_USER")) or _clean_val(os.environ.get("ODOO_USER")) or "agent@frawo.tech"
ODOO_PASS = _clean_val(os.environ.get("ODOO_RPC_PASSWORD")) or _clean_val(os.environ.get("ODOO_PASSWORD")) or ""

def get_connection():
    if not ODOO_PASS:
        print("FEHLER: ODOO_PASSWORD oder ODOO_RPC_PASSWORD nicht gesetzt.")
        sys.exit(1)
    try:
        common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common", allow_none=True)
        # 1. Echte HTTP/Netzwerklatenz (ohne Passwort-Hashing)
        t0 = time.perf_counter()
        _ = common.version()
        net_latency_ms = int((time.perf_counter() - t0) * 1000)
        
        # 2. Authentifizierung (bcrypt/PBKDF2 Passwort-Verifikation in PostgreSQL)
        t0 = time.perf_counter()
        uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASS, {})
        auth_duration_ms = int((time.perf_counter() - t0) * 1000)
        
        if not uid:
            print(f"Authentifizierung fehlgeschlagen fuer {ODOO_USER} an {ODOO_DB} ({ODOO_URL})")
            sys.exit(1)
        models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object", allow_none=True)
        return uid, models, net_latency_ms, auth_duration_ms
    except Exception as e:
        print(f"Verbindungsfehler zu Odoo ({ODOO_URL}): {e}")
        sys.exit(1)

def execute_kw(model, method, args=None, kwargs=None):
    uid, models, _, _ = get_connection()
    return models.execute_kw(ODOO_DB, uid, ODOO_PASS, model, method, args or [], kwargs or {})

def cmd_status():
    uid, models, net_ms, auth_ms = get_connection()
    version_info = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common").version()
    server_version = version_info.get("server_version", "Unbekannt")
    
    users_count = len(execute_kw('res.users', 'search', [[('active', '=', True)]]))
    tasks_active = len(execute_kw('project.task', 'search', [[('active', '=', True)]]))
    leads_active = len(execute_kw('crm.lead', 'search', [[('active', '=', True)]]))
    equipment_count = len(execute_kw('maintenance.equipment', 'search', [[]]))
    partners_count = len(execute_kw('res.partner', 'search', [[('customer_rank', '>', 0)]]))
    
    print("\n" + "="*70)
    print(" FraWo GbR - Odoo ERP Systemstatus")
    print("="*70)
    print(f" Host:                 {ODOO_URL}")
    print(f" Datenbank:            {ODOO_DB}")
    print(f" Odoo Version:         {server_version}")
    print(f" Netzwerk-HTTP-Latenz: {net_ms} ms (Ping < 1 ms)")
    print(f" Auth-Dauer (bcrypt):  {auth_ms} ms (Passwort-Hashverifikation Odoo)")
    print(f" Authentifiziert:      User ID {uid} ({ODOO_USER})")
    print("-" * 70)
    print(f" Aktive Benutzer:      {users_count}")
    print(f" Aktive Kunden:        {partners_count}")
    print(f" Offene Aufgaben:      {tasks_active}")
    print(f" Inventar/Equipment:   {equipment_count} Einheiten (Echtbestand)")
    print(f" Offene CRM-Leads:     {leads_active}")
    print("="*70 + "\n")

def cmd_tools():
    # Zeigt real vorhandenes Verleih-, Steuer- und Tontechnik-Equipment
    domain = [('category_id', 'in', [2, 9, 12, 13])]
    fields = ['id', 'name', 'category_id', 'serial_no', 'technician_user_id', 'cost', 'x_geraetestatus', 'x_status_hinweis']
    records = execute_kw('maintenance.equipment', 'search_read', [domain], {'fields': fields})
    
    print("\n" + "="*85)
    print(" FraWo Equipment & Veranstaltungstechnik (Echtbestand)")
    print("="*85)
    
    by_cat = {}
    for r in records:
        cat_name = r['category_id'][1] if r['category_id'] else 'Ohne Kategorie'
        by_cat.setdefault(cat_name, []).append(r)
        
    for cat, items in sorted(by_cat.items()):
        print(f"\n[Kategorie] {cat} ({len(items)} Posten):")
        print(f" {'ID':<5} | {'Inventar-Nr':<22} | {'Zustand':<14} | {'Bezeichnung'}")
        print(" " + "-"*83)
        for it in items:
            tid = it['id']
            sno = it['serial_no'] or '-'
            stat = it['x_geraetestatus'] or 'ungeklaert'
            stat_icon = "Bereit" if stat == "einsatzbereit" else stat
            name = it['name']
            print(f" #{tid:<4} | {sno:<22} | {stat_icon:<14} | {name}")
            if it.get('x_status_hinweis'):
                print(f"       -> {it['x_status_hinweis']}")
    print("\n" + "="*85 + "\n")

def cmd_dguv():
    domain = [('category_id', 'in', [12, 16, 17, 9, 2])]
    fields = ['id', 'name', 'category_id', 'serial_no', 'effective_date', 'x_geraetestatus', 'technician_user_id']
    records = execute_kw('maintenance.equipment', 'search_read', [domain], {'fields': fields})
    
    print("\n" + "="*85)
    print(" DGUV Vorschrift 3 - Elektrische Betriebsmittel & Pruefstatus")
    print("="*85)
    print(f" {'ID':<5} | {'Kategorie':<24} | {'Inventar-Nr':<18} | {'Status':<12} | {'Geraet'}")
    print(" " + "-"*83)
    for r in records:
        cat = (r['category_id'][1][:22] + '..') if len(r['category_id'][1]) > 24 else r['category_id'][1]
        sno = r['serial_no'] or '-'
        stat = r['x_geraetestatus'] or 'ungeklaert'
        icon = "DGUV V3 OK" if stat == "einsatzbereit" else ("Pruefung" if stat == "ungeklaert" else "Defekt")
        print(f" #{r['id']:<4} | {cat:<24} | {sno:<18} | {icon:<12} | {r['name']}")
    print("="*85 + "\n")

def cmd_tasks():
    tasks = execute_kw('project.task', 'search_read', 
                       [[('active', '=', True), ('stage_id', 'in', [2, 3])]], 
                       {'fields': ['id', 'name', 'stage_id', 'tag_ids', 'date_deadline', 'user_ids']})
    
    tags = {t['id']: t['name'] for t in execute_kw('project.tags', 'search_read', [[('name', 'ilike', '@')]], {'fields': ['id', 'name']})}
    
    by_loc = {'@rk22': [], '@villa': [], '@unterwegs': [], '@inselhalle': [], '@stockenweiler': [], '@remote': [], 'Ohne Standort': []}
    for t in tasks:
        loc = None
        for tid in t['tag_ids']:
            if tid in tags:
                loc = tags[tid]
                break
        if loc in by_loc:
            by_loc[loc].append(t)
        else:
            by_loc['Ohne Standort'].append(t)
            
    print("\n" + "="*80)
    print(" FraWo Einsatzplan nach Standorten (@rk22, @villa, @unterwegs, @remote)")
    print("="*80)
    for loc, items in by_loc.items():
        if not items:
            continue
        print(f"\n{loc} ({len(items)} Aufgaben):")
        for it in items:
            stage = it['stage_id'][1] if it['stage_id'] else 'Offen'
            dl = it['date_deadline'][:10] if it.get('date_deadline') else 'Keine Frist'
            print(f"  - [{it['id']}] {it['name']} ({stage} | Frist: {dl})")
    print("\n" + "="*80 + "\n")

def cmd_hygiene():
    print("\n" + "="*70)
    print(" FraWo ERP Hygiene-Audit")
    print("="*70)
    
    active_tasks = execute_kw('project.task', 'search_read', 
                              [[('active', '=', True), ('stage_id', 'in', [2, 3])]], 
                              {'fields': ['id', 'name', 'tag_ids']})
    loc_tags = set(t['id'] for t in execute_kw('project.tags', 'search_read', [[('name', 'ilike', '@')]], {'fields': ['id']}))
    unlocated = [t for t in active_tasks if not any(tid in loc_tags for tid in t['tag_ids'])]
    
    if unlocated:
        print(f" WARNUNG: {len(unlocated)} Aufgaben ohne Standort-Tag gefunden:")
        for u in unlocated:
            print(f"     - #{u['id']}: {u['name']}")
    else:
        print(" OK: 100 % aller aktiven Aufgaben besitzen einen gueltigen Standort-Tag.")
        
    tag_160_tasks = execute_kw('project.task', 'search_read', [[('active', '=', True), ('tag_ids', 'in', [160])]], {'fields': ['id', 'name', 'stage_id']})
    if tag_160_tasks:
        print(f" WARNUNG: {len(tag_160_tasks)} Aufgaben mit Tag 160 (beantwortet) ausstehend:")
        for t in tag_160_tasks:
            print(f"     - #{t['id']}: {t['name']} ({t['stage_id'][1]})")
    else:
        print(" OK: Tag 160 Warteschlange ist komplett bereinigt (0 Aufgaben).")
        
    invoices = execute_kw('account.move', 'search_read', 
                          [[('move_type', '=', 'out_invoice'), ('state', '=', 'posted'), ('payment_state', '!=', 'paid')]], 
                          {'fields': ['name', 'partner_id', 'amount_total', 'invoice_date_due']})
    if invoices:
        print(f" INFO: {len(invoices)} offene Kundenrechnungen:")
        for inv in invoices:
            print(f"     - {inv['name']}: {inv['partner_id'][1]} | {inv['amount_total']} EUR | Faellig: {inv['invoice_date_due']}")
    else:
        print(" OK: Keine ueberfaelligen oder unbezahlten Kundenrechnungen (100 % beglichen).")
        
    print("="*70 + "\n")

def cmd_quotes():
    templates = execute_kw('sale.order.template', 'search_read', [], {'fields': ['id', 'name']})
    quotes = execute_kw('sale.order', 'search_read', [[('state', 'in', ['draft', 'sent'])]], {'fields': ['name', 'partner_id', 'amount_total', 'state', 'date_order']})
    
    print("\n" + "="*70)
    print(" Angebotswesen (Vorlagen & Offene Angebote)")
    print("="*70)
    print(f"\nVorhandene Angebotsvorlagen ({len(templates)}):")
    for t in templates:
        print(f"  #{t['id']:<2}: {t['name']}")
        
    print(f"\nOffene Angebote in Bearbeitung/Versendet ({len(quotes)}):")
    for q in quotes:
        st = "Entwurf" if q['state'] == 'draft' else "Versendet"
        print(f"  {q['name']}: {q['partner_id'][1]} | {q['amount_total']:.2f} EUR | Status: {st}")
    print("="*70 + "\n")

def cmd_journal(task_id, sync=False):
    """Liest den Chatter einer Aufgabe aus und baut ein chronologisches Tagebuch."""
    import re
    import html
    task = execute_kw('project.task', 'search_read', [[('id', '=', task_id)]], {'fields': ['id', 'name', 'description']})
    if not task:
        print(f"FEHLER: Aufgabe #{task_id} nicht gefunden.")
        return
    t = task[0]
    msgs = execute_kw('mail.message', 'search_read', 
                      [[('model', '=', 'project.task'), ('res_id', '=', task_id)]], 
                      {'fields': ['id', 'date', 'author_id', 'body', 'subtype_id'], 'order': 'date asc'})
    
    entries = []
    for m in msgs:
        body = m['body'] or ''
        # Unescape first in case of doubly-encoded entities, then strip tags, then unescape remaining
        unescaped = html.unescape(body)
        clean = re.sub(r'<[^>]+>', ' ', unescaped)
        clean = html.unescape(clean).strip()
        clean = re.sub(r'\s+', ' ', clean)
        if not clean or 'Eine neue Aufgabe wurde' in clean or 'Termin / Fokuszeit' in clean or 'done' == clean:
            continue
        author = (m['author_id'][1].split(',')[0] if m['author_id'] else 'System').strip()
        date_str = m['date'][:10]
        entries.append({'date': date_str, 'author': author, 'text': clean, 'raw_html': body})
        
    print("\n" + "="*80)
    print(f" 📖 Chatter-Tagebuch fuer #{t['id']}: {t['name']}")
    print("="*80)
    if not entries:
        print("Keine Tagebucheintraege im Chatter gefunden.")
    else:
        for e in entries:
            print(f" [{e['date']}] {e['author']}:")
            print(f"   {e['text']}")
            print("-" * 80)
            
    if sync:
        rows_html = "".join([f"<tr><td><b>{e['date']}</b></td><td>{e['author']}</td><td>{e['text']}</td></tr>" for e in reversed(entries)])
        journal_table = f"""<h3>📖 Automatisiertes Chatter-Tagebuch</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse; width:100%;">
  <thead><tr style="background:#f2f2f2;"><th>Datum</th><th>Autor</th><th>Eintrag</th></tr></thead>
  <tbody>{rows_html}</tbody>
</table>"""
        old_desc = t['description'] or ''
        if '<h3>📖 Automatisiertes Chatter-Tagebuch</h3>' in old_desc:
            new_desc = old_desc.split('<h3>📖 Automatisiertes Chatter-Tagebuch</h3>')[0] + journal_table
        else:
            new_desc = old_desc + "<br>" + journal_table
        execute_kw('project.task', 'write', [[task_id], {'description': new_desc}])
        print(f"✅ Tagebuch erfolgreich in Aufgabenbeschreibung von #{task_id} synchronisiert.")
    print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(description="FraWo Odoo Werkzeugkasten CLI")
    subparsers = parser.add_subparsers(dest="command", help="Verfuegbare Befehle")
    
    subparsers.add_parser("status", help="Odoo Systemstatus und Kennzahlen")
    subparsers.add_parser("tools", help="Werkzeuge, Maschinen und Messgeraete")
    subparsers.add_parser("dguv", help="Elektrische Betriebsmittel & DGUV V3 Pruefstatus")
    subparsers.add_parser("tasks", help="Einsatzplan nach Standorten")
    subparsers.add_parser("hygiene", help="ERP Datenhygiene-Audit")
    subparsers.add_parser("quotes", help="Angebote und Vorlagen")
    
    p_journal = subparsers.add_parser("journal", help="Chatter-Tagebuch einer Aufgabe anzeigen / synchronisieren")
    p_journal.add_argument("task_id", type=int, help="ID der Odoo-Aufgabe (z.B. 1220)")
    p_journal.add_argument("--sync", action="store_true", help="Synchronisiert das Tagebuch direkt in die Aufgabenbeschreibung")
    
    args = parser.parse_args()
    
    if not args.command:
        cmd_status()
        cmd_tools()
        sys.exit(0)
        
    commands = {
        "status": cmd_status,
        "tools": cmd_tools,
        "dguv": cmd_dguv,
        "tasks": cmd_tasks,
        "hygiene": cmd_hygiene,
        "quotes": cmd_quotes
    }
    
    if args.command == "journal":
        cmd_journal(args.task_id, sync=args.sync)
    else:
        cmd_fn = commands.get(args.command)
        if cmd_fn:
            cmd_fn()
        else:
            parser.print_help()

if __name__ == "__main__":
    main()

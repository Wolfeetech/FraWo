#!/usr/bin/env python3
"""
Erweiterung PRJ-2026-MED-PRINZ: Gewerk 2 Signolux-Sicherheitssystem
- Neue Produkte (HMV-Nummern)
- Neuer Service SRV-SIG-SETUP
- Phase 5 & 6 Tasks in Projekt 22
- Separates Angebot fuer Krankenkasse (SGB V)
- Kassenantrag-Text als Projektnotiz
"""
import xmlrpc.client, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST = "http://10.4.0.22:8069"
DB = "FraWo_GbR"
UID = 6
import os
PW = os.environ.get('ODOO_PASSWORD', 'INSERT_PASSWORD_HERE')
PROJECT_ID = 22
PARTNER_ID = 42  # Alois Prinz

m = xmlrpc.client.ServerProxy(f"{HOST}/xmlrpc/2/object")

# ─── Hilfsfunktionen ──────────────────────────────────────────────────────────

def create_or_get_product(default_code, name, product_type, price, description="", categ_id=None):
    """Anlegen wenn nicht vorhanden, sonst ID zurueckgeben."""
    existing = m.execute_kw(DB, UID, PW, "product.template", "search",
                            [[["default_code", "=", default_code]]])
    if existing:
        print(f"  [EXISTS] {default_code} (ID {existing[0]})")
        return existing[0]
    vals = {
        "name": name,
        "default_code": default_code,
        "type": product_type,  # "consu" oder "service"
        "list_price": price,
        "description": description,
    }
    if categ_id:
        vals["categ_id"] = categ_id
    tmpl_id = m.execute_kw(DB, UID, PW, "product.template", "create", [vals])
    print(f"  [OK] Erstellt: {default_code} — ID={tmpl_id}")
    return tmpl_id


def get_product_product_id(tmpl_id):
    """product.product ID fuer ein product.template holen."""
    ids = m.execute_kw(DB, UID, PW, "product.product", "search",
                       [[["product_tmpl_id", "=", tmpl_id]]])
    return ids[0] if ids else None


def get_stage_id(name_fragment):
    stages = m.execute_kw(DB, UID, PW, "project.task.type", "search_read",
                          [[["name", "ilike", name_fragment]]],
                          {"fields": ["id", "name"]})
    return stages[0]["id"] if stages else 1


# ─── 1. Produktkategorie sichern ──────────────────────────────────────────────
print("\n[1] Produktkategorie...")
cat = m.execute_kw(DB, UID, PW, "product.category", "search_read",
                   [[["name", "ilike", "Medizintechnik"]]],
                   {"fields": ["id", "name"]})
categ_id = cat[0]["id"] if cat else None
print(f"    Kategorie: {cat[0]['name']} (ID={categ_id})" if cat else "    Kein 'Medizintechnik'-Kategorie gefunden — ohne Kategorie")

# ─── 2. Gewerk-2-Hardware (Signolux) ──────────────────────────────────────────
print("\n[2] Signolux Produkte anlegen...")

HMV_PRODUCTS = [
    ("HW-SIG-REC",   "Humantechnik signolux Empfaenger-Wecker",
     "Netzbetriebener Blitz-Wecker fuer Nachttisch. HMV-Nr: 13.99.04.3021 (GKV-faehig §33 SGB V)",
     184.00),
    ("HW-SIG-VIB",   "Humantechnik signolux Vibrationskissen",
     "Bett-Vibrationskissen fuer Schlafzimmer-Alarmierung. HMV-Nr: 13.99.04.5003 (GKV-faehig §33 SGB V)",
     42.00),
    ("HW-SIG-SMOKE", "Humantechnik signolux Funk-Rauchmelder (Hekatron)",
     "Funk-Rauchwarnmelder DIN 14676 mit int. Sender 868 MHz. HMV-Nr: 13.99.04.0023 (GKV-faehig §33 SGB V)",
     167.23),
    ("HW-SIG-BELL",  "Humantechnik signolux Klingelsender",
     "Ankopplung an vorhandene Haustuer-Klingelanlage. HMV-Nr: 13.99.04.1012 (GKV-faehig §33 SGB V)",
     109.24),
    ("HW-SIG-PORT",  "Humantechnik signolux Mobiler Empfaenger",
     "Mobiler Blitzempfaenger fuer Wohnzimmer/Garten. HMV-Nr: 13.99.04.2005 (GKV-faehig §33 SGB V)",
     142.86),
]

hw_sig_tmpl_ids = {}
for code, name, desc, price in HMV_PRODUCTS:
    tid = create_or_get_product(code, name, "consu", price, desc, categ_id)
    hw_sig_tmpl_ids[code] = tid

# ─── 3. Neuer Service SRV-SIG-SETUP ──────────────────────────────────────────
print("\n[3] Service SRV-SIG-SETUP anlegen...")
sig_setup_tmpl = create_or_get_product(
    "SRV-SIG-SETUP",
    "Einlernen & HF-Messung Signalanlage",
    "service",
    85.00,
    "Frequenz-Pairing aller Sender/Empfaenger, Reichweitenmessung im Haus, VDE-Pruefung DIN VDE 0701-0702"
)

# ─── 4. Stages fuer Projekt 22 pruefen ───────────────────────────────────────
print("\n[4] Verfuegbare Stages fuer Projekt 22...")
stages = m.execute_kw(DB, UID, PW, "project.task.type", "search_read",
                      [[["project_ids", "in", [PROJECT_ID]]]],
                      {"fields": ["id", "name"]})
for s in stages:
    print(f"    Stage {s['id']}: {s['name']}")

# Planung-Stage finden (oder ersten nehmen)
plan_stage = next((s["id"] for s in stages if "plan" in s["name"].lower()), stages[0]["id"])
todo_stage = next((s["id"] for s in stages if "todo" in s["name"].lower()
                   or "backlog" in s["name"].lower()
                   or "auftrag" in s["name"].lower()), plan_stage)
print(f"    -> Nutze Stage ID {todo_stage} fuer neue Tasks")

# ─── 5. Phase-5-Tasks (GKV-Sicherheitsanlage) ────────────────────────────────
print("\n[5] Phase-5-Tasks anlegen (Installation Signolux)...")

PHASE5_TASKS = [
    ("Task 5.1 – Montage Klingelsender",
     "Montage des signolux Klingelsenders an den Gong/Klingel-Transformator (Mikrofon-Abgreifer ODER galvanisch Klemmen 0/F). Polaritaet pruefen, Kabelzugentlastung sichern.",
     1.0),
    ("Task 5.2 – Installation Funk-Rauchmelder",
     "Installation signolux Funk-Rauchwarnmelder nach DIN 14676 in Schlafzimmer, Flur und Wohnzimmer. Montagehoehe >= 50 cm von Wand, Batteriespannung pruefen.",
     1.5),
    ("Task 5.3 – Positionierung Wecker & Vibrationskissen",
     "Aufstellung signolux Empfaenger-Wecker auf Nachttisch. Vibrationskissen unter Matratzenbezug platzieren, Kabel zugentlastet verlegen, Reichweitentest.",
     0.5),
    ("Task 5.4 – Aufstellung Mobiler Empfaenger (Wohnzimmer)",
     "Mobiler signolux Blitzempfaenger an zentraler Position mit Sichtachse zum Sessel des Vaters aufstellen. Ladesystem einrichten.",
     0.5),
]

phase5_ids = []
for name, desc, hours in PHASE5_TASKS:
    existing = m.execute_kw(DB, UID, PW, "project.task", "search",
                            [[["name", "=", name], ["project_id", "=", PROJECT_ID]]])
    if existing:
        print(f"  [EXISTS] {name}")
        phase5_ids.append(existing[0])
        continue
    tid = m.execute_kw(DB, UID, PW, "project.task", "create", [{
        "name": name,
        "project_id": PROJECT_ID,
        "stage_id": todo_stage,
        "description": f"<p>{desc}</p>",
        "allocated_hours": hours,
        "tag_ids": [],
    }])
    print(f"  [OK] {name} (ID={tid})")
    phase5_ids.append(tid)

# ─── 6. Phase-6-Tasks (Pairing, HF-Pruefung, VDE) ────────────────────────────
print("\n[6] Phase-6-Tasks anlegen (Pairing & Pruefung)...")

PHASE6_TASKS = [
    ("Task 6.1 – System-Pairing & Blink-Muster",
     "Einlernen aller Sender auf Empfaenger. Individuelle Blink-Muster vergeben: Rauchalarm = Rotes Dauerlicht + schneller Blitz. Tuerklingel = Gruenes Blinklicht. Protokoll erstellen.",
     1.0),
    ("Task 6.2 – HF-Reichweitentest 868 MHz",
     "Daempfungstest: Abschreiten aller Raeume (inkl. Keller und Terrasse) mit mobilem Empfaenger. Mindestreichweite in jedem Raum verifizieren. Ergebnis fotografisch dokumentieren.",
     0.75),
    ("Task 6.3 – VDE-Pruefung & Dokumentation",
     "Elektrische Sicherheitspruefung nach DIN VDE 0701-0702 fuer alle netzbetriebenen Empfaenger. Pruefprotokoll im Odoo-Chatter hochladen. Kopie fuer Kassenbescheid anfertigen.",
     0.75),
]

phase6_ids = []
for name, desc, hours in PHASE6_TASKS:
    existing = m.execute_kw(DB, UID, PW, "project.task", "search",
                            [[["name", "=", name], ["project_id", "=", PROJECT_ID]]])
    if existing:
        print(f"  [EXISTS] {name}")
        phase6_ids.append(existing[0])
        continue
    tid = m.execute_kw(DB, UID, PW, "project.task", "create", [{
        "name": name,
        "project_id": PROJECT_ID,
        "stage_id": todo_stage,
        "description": f"<p>{desc}</p>",
        "allocated_hours": hours,
    }])
    print(f"  [OK] {name} (ID={tid})")
    phase6_ids.append(tid)

# ─── 7. Angebot Gewerk 2 (Krankenkasse SGB V) ────────────────────────────────
print("\n[7] Angebot Gewerk 2 (KK SGB V) erstellen...")

existing_orders = m.execute_kw(DB, UID, PW, "sale.order", "search_read",
                               [[["client_order_ref", "=", "PRJ-2026-MED-PRINZ-GW2"]]],
                               {"fields": ["id", "name"]})
if existing_orders:
    print(f"  [EXISTS] {existing_orders[0]['name']} — nicht nochmal anlegen")
    gw2_order_id = existing_orders[0]["id"]
else:
    # Produkt-IDs fuer Angebotspositionen holen
    def get_pp_id(code):
        tids = m.execute_kw(DB, UID, PW, "product.template", "search",
                            [[["default_code", "=", code]]])
        if not tids:
            return None
        ppids = m.execute_kw(DB, UID, PW, "product.product", "search",
                             [[["product_tmpl_id", "=", tids[0]]]])
        return ppids[0] if ppids else None

    note_gw2 = (
        "<p><strong>GEWERK 2: Drahtlose Lichtsignal- &amp; Notfall-Warnanlage</strong></p>"
        "<p>Kostentraeger: Gesetzliche Krankenkasse (GKV) gemaess &sect; 33 SGB V</p>"
        "<p>Erstattungsfaehige Hilfsmittel (HMV-gelistet). Voraussetzung: HNO-Rezept mit Indikation "
        "'beidseitige, an Taubheit grenzende Schwerhörigkeit'. Zuzahlung: 10,- Euro.</p>"
        "<p>Rechtsbasis: BSG-Urteil 29.04.2010 – B 3 KR 5/09 R</p>"
    )

    LINE_ITEMS_GW2 = [
        ("HW-SIG-REC",   1, 184.00),
        ("HW-SIG-VIB",   1,  42.00),
        ("HW-SIG-SMOKE", 3, 167.23),  # 3x: Schlafzimmer + Flur + Wohnzimmer
        ("HW-SIG-BELL",  1, 109.24),
        ("HW-SIG-PORT",  1, 142.86),
        ("SRV-SIG-SETUP", 1,  85.00),
        ("SRV-SEN-EINW",  1,  80.00),
    ]

    lines = []
    for code, qty, price in LINE_ITEMS_GW2:
        ppid = get_pp_id(code)
        if not ppid:
            print(f"  [WARN] Produkt {code} nicht gefunden — ueberspringe")
            continue
        lines.append((0, 0, {
            "product_id": ppid,
            "product_uom_qty": qty,
            "price_unit": price,
        }))

    order_vals = {
        "partner_id": PARTNER_ID,
        "project_id": PROJECT_ID,
        "date_order": "2026-05-29",
        "validity_date": "2026-07-31",
        "client_order_ref": "PRJ-2026-MED-PRINZ-GW2",
        "note": note_gw2,
        "order_line": lines,
    }
    gw2_order_id = m.execute_kw(DB, UID, PW, "sale.order", "create", [order_vals])

    order = m.execute_kw(DB, UID, PW, "sale.order", "read",
                         [[gw2_order_id]],
                         {"fields": ["name", "amount_total"]})[0]
    print(f"  [OK] {order['name']} — Gesamt: {order['amount_total']:.2f} EUR")

# ─── 8. Kassenantrag-Text als Projektnotiz (chatter) ──────────────────────────
print("\n[8] Kassenantrag-Begründung als Projektnotiz...")

kassenantrag = """<h3>Begruendung der Leistungspflicht &sect; 33 SGB V (Gewerk 2)</h3>
<p>Der Versicherte leidet unter einer beidseitigen, an Taubheit grenzenden Schwerhörigkeit
(Cochlea-Implantat links, Hoergeraet rechts). Waehrend der Schlafphase (abgelegte Hoersysteme)
ist die Wahrnehmung von Haustürklingel, Telefonanruf und Brandalarm vollstaendig unmoeglich.</p>
<p>Gemaess BSG-Urteil 29.04.2010 &ndash; B 3 KR 5/09 R besteht Anspruch auf Lichtsignalanlage
und funkvernetzte Rauchwarnmelder als Hilfsmittel der GKV. Die beantragten Komponenten sind
nicht fest mit dem Gebaeude verbunden (portable), daher eindeutig SGB V – nicht SGB XI.</p>
<p><strong>HNO-Rezept Muster 16 (Textvorschlag):</strong><br/>
1x Lichtsignalanlage fuer Gehoerlose: 1x Funksender Haustuere, 1x Funk-Rauchwarnmelder DIN 14676,
1x stationaerer Blitzempfaenger mit Vibrationskissen, 1x mobiler Blitzempfaenger.<br/>
Indikation: Beidseitige, an Taubheit grenzende Schwerhörigkeit (CI links, HG rechts).</p>"""

try:
    m.execute_kw(DB, UID, PW, "project.project", "message_post",
                 [[PROJECT_ID]], {
                     "body": kassenantrag,
                     "message_type": "comment",
                     "subtype_xmlid": "mail.mt_note",
                 })
    print("  [OK] Kassenantrag-Text als interne Notiz im Projekt gespeichert")
except Exception as e:
    print(f"  [WARN] Chatter-Notiz fehlgeschlagen: {e}")

# ─── Zusammenfassung ──────────────────────────────────────────────────────────
print("\n" + "="*70)
print("ERGEBNIS:")
print(f"  Neue Produkte: {len(HMV_PRODUCTS)} Signolux-Hardware + 1 Service")
print(f"  Neue Tasks:    {len(PHASE5_TASKS)} x Phase 5 + {len(PHASE6_TASKS)} x Phase 6")
print(f"  Angebot GW2:   http://10.4.0.22:8069/odoo/sales/{gw2_order_id}")
print(f"  Angebot GW1:   http://10.4.0.22:8069/odoo/sales/12  (unveraendert)")
print(f"  Projekt 22:    http://10.4.0.22:8069/odoo/project/{PROJECT_ID}")
print("="*70)
print("\nNaechste Schritte:")
print("  1. GW2-Angebot in Odoo pruefen und PDF exportieren (fuer KK-Antrag)")
print("  2. HNO-Arzt-Termin → Muster-16-Rezept ausstellen lassen")
print("  3. GW1-Angebot S00012 aktualisieren (Pflegekasse §40 SGB XI)")
print("  4. Signolux-Produkte bei Humantechnik bestellen")

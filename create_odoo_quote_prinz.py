#!/usr/bin/env python3
"""
Kostenvoranschlag Bimodale Audiointegration — Alois Prinz
Erstellt sale.order (Angebot) in Odoo für Partner 42, Projekt 22
"""
import xmlrpc.client
from datetime import date

HOST = "http://10.4.0.22:8069"
DB = "FraWo_GbR"
UID = 6
import os
PW = os.environ.get('ODOO_PASSWORD', 'INSERT_PASSWORD_HERE')

models = xmlrpc.client.ServerProxy(f"{HOST}/xmlrpc/2/object")

# Produkt-IDs (aus update_odoo_prinz.py bestätigt)
# (product_id, name_display, qty, unit_price)
LINE_ITEMS = [
    (73, "HW-DSP-4X4 — t.racks 4x4 DSP Pro",               1, 139.00),
    (74, "HW-SPK-ERIS35 — PreSonus Eris 3.5 (Paar)",        1,  99.00),
    (75, "HW-EXT-SWIS — Swissonic Audio Extractor",          1,  49.00),
    (76, "HW-ACC-VOL — Fostex PC-1e Lautstärkeregler",       1,  29.00),
    (77, "HW-CAB-PHOEN1 — Kabel Euro→XLR 0,5m (Eigenbau)",  2,  15.00),
    (78, "HW-CAB-PHOEN2 — Kabel Euro→RCA 0,5m (Eigenbau)",  2,  15.00),
    (79, "HW-CAB-TOS — Toslink-Kabel 1,5m",                  1,   9.90),
    (80, "HW-NET-SW8 — PoE Switch 8-Port",                   1,  79.00),
    (81, "SRV-INSTALL — Installation vor Ort",               3,  85.00),
    (82, "SRV-DSP-PROG — DSP-Programmierung & bimod. Einmessung", 3, 95.00),
    (83, "SRV-SEN-EINW — Einweisung & App-Konfiguration",    1,  80.00),
]

def create_quote():
    # Angebot (sale.order) anlegen
    note = (
        "Kostenvoranschlag für bimodales Audiointegrationssystem Familie Prinz.\n"
        "CI links: Med-El Sonnet 3 | HG rechts: Phonak.\n"
        "DSP-gestützte Latenzkompensation, Lautstärkeanpassung und Signalverteilung.\n"
        "Rechtsgrundlage: SGB V §33 / SGB XI §40 (Kassenantrag in Vorbereitung)."
    )

    order_vals = {
        "partner_id": 42,           # Alois Prinz
        "project_id": 22,           # Projekt 22: Hörsystem & In-Ear Monitoring
        "date_order": str(date.today()),
        "validity_date": "2026-07-31",
        "note": note,
        "client_order_ref": "PRJ-2026-MED-PRINZ",
        "order_line": [
            (0, 0, {
                "product_id": pid,
                "name": name,
                "product_uom_qty": qty,
                "price_unit": price,
            })
            for pid, name, qty, price in LINE_ITEMS
        ],
    }

    order_id = models.execute_kw(DB, UID, PW, "sale.order", "create", [order_vals])
    print(f"[OK] sale.order erstellt: ID={order_id}")

    # Gesamtsumme berechnen
    order = models.execute_kw(DB, UID, PW, "sale.order", "read",
                               [[order_id]], {"fields": ["name", "amount_total", "state"]})[0]
    print(f"     Angebotsnummer : {order['name']}")
    print(f"     Status         : {order['state']}")
    print(f"     Gesamtbetrag   : {order['amount_total']:.2f} €")

    # Einzelposten zur Kontrolle
    lines = models.execute_kw(DB, UID, PW, "sale.order.line", "search_read",
                              [[["order_id", "=", order_id]]],
                              {"fields": ["name", "product_uom_qty", "price_unit", "price_subtotal"]})
    print("\n  Positionen:")
    for l in lines:
        print(f"    {l['product_uom_qty']:.0f}×  {l['name'][:55]:<55}  "
              f"{l['price_unit']:>8.2f}€  → {l['price_subtotal']:>8.2f}€")

    return order_id

if __name__ == "__main__":
    oid = create_quote()
    print(f"\nAngebot unter http://10.4.0.22:8069/odoo/sales/{oid} abrufbar.")
    print("Zum PDF-Export: Angebot öffnen → Drucken → 'Angebot / Auftragsbestätigung'")

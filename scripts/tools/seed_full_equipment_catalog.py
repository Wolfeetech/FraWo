import subprocess
import json
import sys

# Script to enrich all 49 equipment items in Odoo DB (maintenance_equipment)

EQUIPMENT_CATALOG = [
    {
        "id": 1,
        "name": "Fussballdart - aufblasbar (5m)",
        "category_id": 1,
        "model": "Air Inflatable Event Dart 5 Meter",
        "location": "Rothkreuz - Eventlager",
        "serial_no": "RENTAL-DART-5M",
        "note": "Riesiges 5m Event-Fussballdart mit Gebläse, Klettbällen und Teleskop-Stange. Vermietung & Events."
    },
    {
        "id": 2,
        "name": "KMT CS-215 Top (Pair 1)",
        "category_id": 2,
        "model": "KMT CS-215 Professional Top 2-Way",
        "location": "Rothkreuz - Event Rack",
        "serial_no": "KMT-CS215-01",
        "note": "Professionelles PA-Topteil 15'' / 1'' Horn 500W RMS. Druckvoller Klang für Live-Events."
    },
    {
        "id": 3,
        "name": "KMT CS-215 Top (Pair 2)",
        "category_id": 2,
        "model": "KMT CS-215 Professional Top 2-Way",
        "location": "Rothkreuz - Event Rack",
        "serial_no": "KMT-CS215-02",
        "note": "Professionelles PA-Topteil 15'' / 1'' Horn 500W RMS. Druckvoller Klang für Live-Events."
    },
    {
        "id": 4,
        "name": "Brüll-Würfel Compact PA",
        "category_id": 2,
        "model": "Custom Active Mobile Box 300W",
        "location": "Villa Rothkreuz",
        "serial_no": "BRUELL-WUERFEL-01",
        "note": "Kompakter robuster Aktivlautsprecher für Partys, Afterwork & Baustellen-Beschallung."
    },
    {
        "id": 5,
        "name": "Ubiquiti UniFi Cloud Gateway Ultra (UCG)",
        "category_id": 3,
        "model": "Ubiquiti UCG-Ultra Multi-WAN Router",
        "location": "Rothkreuz - Server Rack 1",
        "serial_no": "UCG-ULTRA-ROTHKREUZ",
        "note": "Master Router & Firewall (10.1.0.1). Verwaltet VLAN101 Server, VLAN104 IoT, VLAN105 Guest."
    },
    {
        "id": 6,
        "name": "Martin CX-2 Color Projector (Unit 1)",
        "category_id": 9,
        "model": "Martin CX-2 DMX Gobo/Color Change",
        "location": "Rothkreuz - Licht-Case 1",
        "serial_no": "MARTIN-CX2-01",
        "note": "DMX Farb- & Effekt-Projektor 250W Halogen. Rotierende Gobos & Farbfilter für Events."
    },
    {
        "id": 7,
        "name": "Martin CX-2 Color Projector (Unit 2)",
        "category_id": 9,
        "model": "Martin CX-2 DMX Gobo/Color Change",
        "location": "Rothkreuz - Licht-Case 1",
        "serial_no": "MARTIN-CX2-02",
        "note": "DMX Farb- & Effekt-Projektor 250W Halogen. Rotierende Gobos & Farbfilter für Events."
    },
    {
        "id": 8,
        "name": "Alto Elvis 15A Active Speaker",
        "category_id": 2,
        "model": "Alto Elvis 15A Active 350W RMS",
        "location": "Rothkreuz - Ton-Lager",
        "serial_no": "ALTO-ELVIS15-01",
        "note": "15 Zoll Aktiv-Fullrange-Lautsprecher 350W. Integrierter Limiter & XLR/Klinke Eingänge."
    },
    {
        "id": 9,
        "name": "JB Systems Vibe 12 Mk2 (LS 1)",
        "category_id": 2,
        "model": "JB Systems Vibe 12 Mk2 250W RMS",
        "location": "Rothkreuz - Ton-Lager",
        "serial_no": "JB-VIBE12-01",
        "note": "12 Zoll Passiv-Lautsprecher 8 Ohm. Robuste Holzgehäuse für Sprache & Musik."
    },
    {
        "id": 10,
        "name": "JB Systems Vibe 12 Mk2 (LS 2)",
        "category_id": 2,
        "model": "JB Systems Vibe 12 Mk2 250W RMS",
        "location": "Rothkreuz - Ton-Lager",
        "serial_no": "JB-VIBE12-02",
        "note": "12 Zoll Passiv-Lautsprecher 8 Ohm. Robuste Holzgehäuse für Sprache & Musik."
    },
    {
        "id": 11,
        "name": "Subwoofer Dual 12'' Passive Bass",
        "category_id": 2,
        "model": "Custom Dual 12 Subwoofer 800W",
        "location": "Rothkreuz - Ton-Lager",
        "serial_no": "SUB-DUAL12-01",
        "note": "Doppel 12 Zoll Passiv-Subwoofer. Tieftonsystem für PA-Anlagen."
    },
    {
        "id": 12,
        "name": "Crown CT 2000 Power Amplifier",
        "category_id": 4,
        "model": "Crown ComTech CT 2000 (2x1000W)",
        "location": "Rothkreuz - Event Rack 1",
        "serial_no": "EQUIP-CT2000-01",
        "note": "Professionelle 2-Kanal Endstufe. Treibt KMT Tops und Subwoofer im Rack an."
    },
    {
        "id": 13,
        "name": "Stairville LED Par 56 RGB (Set 1)",
        "category_id": 9,
        "model": "Stairville LED Par 56 DMX RGB",
        "location": "Rothkreuz - Licht-Case 2",
        "serial_no": "STAIRVILLE-PAR56-01",
        "note": "DMX LED Scheinwerfer für Ambiente- & Grundbeleuchtung bei Veranstaltungen."
    },
    {
        "id": 14,
        "name": "Stairville LED Par 56 RGB (Set 2)",
        "category_id": 9,
        "model": "Stairville LED Par 56 DMX RGB",
        "location": "Rothkreuz - Licht-Case 2",
        "serial_no": "STAIRVILLE-PAR56-02",
        "note": "DMX LED Scheinwerfer für Ambiente- & Grundbeleuchtung bei Veranstaltungen."
    },
    {
        "id": 15,
        "name": "Strobe Light 1500W DMX",
        "category_id": 9,
        "model": "High-Power DMX Strobe 1500W",
        "location": "Rothkreuz - Licht-Case 2",
        "serial_no": "STROBE-1500W-01",
        "note": "Blitzlicht Stroboskop 1500W mit DMX-Steuerung für Club & Bühne."
    },
    {
        "id": 16,
        "name": "Nebelmaschine Hazer 1000W",
        "category_id": 9,
        "model": "DMX Hazer / Nebelmaschine 1000W",
        "location": "Rothkreuz - Event Rack",
        "serial_no": "HAZER-1000W-01",
        "note": "DMX Dunsterzeuger für feinen gleichmäßigen Nebel zur Lichtstrahlen-Visualisierung."
    },
    {
        "id": 18,
        "name": "Ubiquiti UniFi USW-24-PoE Switch",
        "category_id": 3,
        "model": "Ubiquiti USW-24-PoE Managed Switch",
        "location": "Rothkreuz - Server Rack 1",
        "serial_no": "USW-24POE-RK1",
        "note": "24-Port Gigabit Managed Switch mit 16 PoE+ Ports (95W Total Budget) für Access Points & Cams."
    },
    {
        "name": "Ubiquiti UniFi U6-Lite Access Point",
        "category_id": 3,
        "model": "Ubiquiti U6-Lite Wi-Fi 6 AP",
        "location": "Rothkreuz - Studio Decke",
        "serial_no": "MAC-74-AC-B9-6C-79-5A",
        "note": "Dual-Band Wi-Fi 6 Access Point (10.1.0.142) versorgt Studio & Werkstatt mit WLAN."
    },
    {
        "id": 40,
        "name": "Surface Go (1. Gen) Kiosk-Terminal",
        "category_id": 10,
        "model": "Microsoft Surface Go 10'' Touch (Intel Pentium Gold)",
        "location": "Studio / Werkstatt Wand",
        "serial_no": "SURFACE-GO-KIOSK",
        "note": "10 Zoll Touchscreen Kiosk Terminal (100.79.103.59) für Odoo Werkstatt & Radio Curation."
    },
    {
        "name": "Yamaha MG12XU Mischpult",
        "category_id": 4,
        "model": "Yamaha MG12XU 12-Kanal Analog/USB",
        "location": "Rothkreuz - Studio Desk",
        "serial_no": "YAMAHA-MG12XU-01",
        "note": "12-Kanal Mischpult mit SPX Effekten & 24-bit/192kHz 2in/2out USB Interface."
    },
    {
        "name": "Pioneer DDJ DJ-Controller",
        "category_id": 10,
        "model": "Pioneer DDJ 2-Kanal Performance Controller",
        "location": "Rothkreuz - Studio Desk",
        "serial_no": "PIONEER-DDJ-RK1",
        "note": "DJ Controller für Live Curation, Streaming & Events."
    }
]

def run_sql_script(sql: str):
    cmd = [
        "ssh", "-o", "BatchMode=yes", "root@10.1.0.128",
        "pct exec 140 -- docker exec -i frawotech-db-1 psql -U odoo -d FraWo_GbR"
    ]
    res = subprocess.run(cmd, input=sql, capture_output=True, text=True, encoding="utf-8")
    if res.returncode != 0:
        print(f"SQL Error: {res.stderr}")
        sys.exit(1)
    print(res.stdout)

def main():
    print("=== Enriching Full AV, Lighting, IT & Event Equipment Catalog in Odoo ===")
    sql_updates = []
    
    for item in EQUIPMENT_CATALOG:
        name_json = json.dumps({"de_DE": item["name"], "en_US": item["name"]})
        if "id" in item:
            sql_updates.append(f"""
UPDATE maintenance_equipment
SET 
    name = '{name_json}'::jsonb,
    category_id = {item["category_id"]},
    model = '{item["model"].replace("'", "''")}',
    location = '{item["location"].replace("'", "''")}',
    serial_no = '{item["serial_no"].replace("'", "''")}',
    note = '{item["note"].replace("'", "''")}',
    equipment_assign_to = 'other',
    effective_date = CURRENT_DATE,
    write_date = NOW()
WHERE id = {item["id"]};
""")
        else:
            sql_updates.append(f"""
INSERT INTO maintenance_equipment (
    name, category_id, model, location, serial_no, note, equipment_assign_to, effective_date, create_date, write_date
) VALUES (
    '{name_json}'::jsonb, {item["category_id"]}, '{item["model"].replace("'", "''")}', '{item["location"].replace("'", "''")}', '{item["serial_no"].replace("'", "''")}', '{item["note"].replace("'", "''")}', 'other', CURRENT_DATE, NOW(), NOW()
);
""")

    # Clean up empty placeholder rows
    sql_updates.append("DELETE FROM maintenance_equipment WHERE name IS NULL OR name->>'de_DE' IS NULL OR name->>'de_DE' = '';")

    run_sql_script("\n".join(sql_updates))
    print("[OK] Full AV, Lighting, IT & Event Equipment catalog enriched in Odoo!")

if __name__ == "__main__":
    main()

import subprocess
import json
import sys

# Script to add VT Service Rates & Day Rates to Odoo Product Catalog

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

SERVICES = [
    {
        "name": "[FW-019] Techniker-Stunde Veranstaltungstechnik",
        "list_price": 85.00,
        "standard_price": 45.00,
        "default_code": "FW-019",
        "description": "Techniker-Stundensatz für Auf-/Abbau, Verkabelung & Betreuung vor Ort."
    },
    {
        "name": "[FW-020] Qualifizierte Fachkraft VT — Tagessatz (8 Std.)",
        "list_price": 500.00,
        "standard_price": 300.00,
        "default_code": "FW-020",
        "description": "Qualifizierte Fachkraft für Veranstaltungstechnik (8 Stunden Tagessatz), ohne Technik."
    },
    {
        "name": "[FW-021] Tontechniker / FOH Operator — Tagessatz (8 Std.)",
        "list_price": 450.00,
        "standard_price": 280.00,
        "default_code": "FW-021",
        "description": "Erfahrener Tontechniker für Live-Mischung (FOH), Soundcheck & Mikrofonsysteme."
    },
    {
        "name": "[FW-022] Lichttechniker / DMX Operator — Tagessatz (8 Std.)",
        "list_price": 450.00,
        "standard_price": 280.00,
        "default_code": "FW-022",
        "description": "Lichttechniker für DMX-Steuerung, Show-Programmierung & Effekt-Licht."
    }
]

def main():
    print("=== Creating VT Service Products in Odoo ===")
    sql_statements = []

    for s in SERVICES:
        name_json = json.dumps({"de_DE": s["name"], "en_US": s["name"]})
        desc_json = json.dumps({"de_DE": s["description"], "en_US": s["description"]})
        
        sql_statements.append(f"""
INSERT INTO product_template (
    name, list_price, standard_price, default_code, description,
    type, categ_id, uom_id, uom_po_id, active, sale_ok, purchase_ok,
    create_date, write_date
) VALUES (
    '{name_json}'::jsonb, {s["list_price"]}, {s["standard_price"]}, '{s["default_code"]}', '{desc_json}'::jsonb,
    'service', 1, 1, 1, true, true, true,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;
""")

    run_sql_script("\n".join(sql_statements))
    print("[OK] VT Service Products created in Odoo!")

if __name__ == "__main__":
    main()

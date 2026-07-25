import subprocess
import json
import sys

# Script to create Indoor Gardening Setup Packages & Consulting Products in Odoo

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

PRODUCTS = [
    {
        "name": "Indoor Gardening Setup S (Kompakt 60x60)",
        "list_price": 890.00,
        "standard_price": 550.00,
        "default_code": "IG-SETUP-S",
        "description": "Smartes Einsteiger-Setup 60x60cm: LED 150W Full-Spectrum, Lüftungsset inkl. Aktivkohlefilter, Home Assistant Sensorik Kit (Temp/Humidity)."
    },
    {
        "name": "Indoor Gardening Setup M (Standard 100x100)",
        "list_price": 1490.00,
        "standard_price": 920.00,
        "default_code": "IG-SETUP-M",
        "description": "Standard Profi-Setup 100x100cm: LED 300W High-Efficiency, regelbarer EC-Lüfter + AKF, Shelly/HA Automation Kit für Licht & Klima."
    },
    {
        "name": "Indoor Gardening Setup L (Profi 120x120 2-Etagen)",
        "list_price": 2490.00,
        "standard_price": 1550.00,
        "default_code": "IG-SETUP-L",
        "description": "High-End 2-Etagen System 120x120cm: LED 600W, automatische Bewässerung, Redundante Sensorik, Home Assistant Live Dashboard Integration."
    },
    {
        "name": "CSC Compliance & Automation Consulting",
        "list_price": 490.00,
        "standard_price": 150.00,
        "default_code": "CSC-CONSULT-01",
        "description": "KCanG & CSC Compliance-Beratung: Bestandsführung, Dokumentation, Daten-Compliance & Smart Automation Integration."
    }
]

def main():
    print("=== Creating Indoor Gardening Products in Odoo ===")
    sql_statements = []

    for p in PRODUCTS:
        name_json = json.dumps({"de_DE": p["name"], "en_US": p["name"]})
        desc_json = json.dumps({"de_DE": p["description"], "en_US": p["description"]})
        
        sql_statements.append(f"""
INSERT INTO product_template (
    name, list_price, standard_price, default_code, description,
    type, categ_id, uom_id, uom_po_id, active, sale_ok, purchase_ok,
    create_date, write_date
) VALUES (
    '{name_json}'::jsonb, {p["list_price"]}, {p["standard_price"]}, '{p["default_code"]}', '{desc_json}'::jsonb,
    'consu', 1, 1, 1, true, true, true,
    NOW(), NOW()
) ON CONFLICT DO NOTHING;
""")

    run_sql_script("\n".join(sql_statements))
    print("[OK] Indoor Gardening Products created in Odoo!")

if __name__ == "__main__":
    main()

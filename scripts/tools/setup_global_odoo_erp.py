import subprocess
import json
import sys

# Global Odoo ERP Production Setup Script for FraWo GbR (CT140)

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
    print("=== Step 1: Configuring Company Data (FraWo GbR) ===")
    sql_company = """
-- Update Company Details
UPDATE res_company
SET 
    name = 'FraWo GbR',
    street = 'Stockenweiler 3',
    city = 'Hergensweiler',
    zip = '88138',
    country_id = (SELECT id FROM res_country WHERE code = 'DE' LIMIT 1),
    email = 'info@frawo.tech',
    website = 'https://frawo.tech',
    currency_id = (SELECT id FROM res_currency WHERE name = 'EUR' LIMIT 1)
WHERE id = 1;

-- Update Company Partner
UPDATE res_partner
SET 
    name = 'FraWo GbR',
    street = 'Stockenweiler 3',
    city = 'Hergensweiler',
    zip = '88138',
    country_id = (SELECT id FROM res_country WHERE code = 'DE' LIMIT 1),
    email = 'info@frawo.tech',
    website = 'https://frawo.tech',
    lang = 'de_DE'
WHERE id = (SELECT partner_id FROM res_company WHERE id = 1);
"""
    run_sql_script(sql_company)
    print("[OK] Company master data (FraWo GbR) configured!")

    print("\n=== Step 2: Creating Partner Categories / Tags ===")
    sql_tags = """
INSERT INTO res_partner_category (name, color, create_date, write_date)
VALUES 
    ('{"de_DE": "Kunde", "en_US": "Customer"}'::jsonb, 1, NOW(), NOW()),
    ('{"de_DE": "Lieferant", "en_US": "Supplier"}'::jsonb, 2, NOW(), NOW()),
    ('{"de_DE": "Partner", "en_US": "Partner"}'::jsonb, 3, NOW(), NOW()),
    ('{"de_DE": "Event-Veranstalter", "en_US": "Event Organizer"}'::jsonb, 4, NOW(), NOW()),
    ('{"de_DE": "Mitglied e.V.", "en_US": "Member e.V."}'::jsonb, 5, NOW(), NOW()),
    ('{"de_DE": "Infrastruktur", "en_US": "Infrastructure"}'::jsonb, 6, NOW(), NOW())
ON CONFLICT DO NOTHING;
"""
    run_sql_script(sql_tags)
    print("[OK] Partner categories / tags created!")

    print("\n=== Step 3: Configuring Global Project Task Stages ===")
    sql_stages = """
-- Ensure standard task stages exist
INSERT INTO project_task_type (name, sequence, fold, active)
VALUES 
    ('{"de_DE": "📋 Backlog", "en_US": "📋 Backlog"}'::jsonb, 1, false, true),
    ('{"de_DE": "⚙️ In Planung", "en_US": "⚙️ In Planung"}'::jsonb, 2, false, true),
    ('{"de_DE": "🚀 In Arbeit", "en_US": "🚀 In Arbeit"}'::jsonb, 3, false, true),
    ('{"de_DE": "🛑 Blockiert", "en_US": "🛑 Blockiert"}'::jsonb, 4, false, true),
    ('{"de_DE": "✅ Erledigt", "en_US": "✅ Erledigt"}'::jsonb, 5, true, true),
    ('{"de_DE": "🗑️ Abgebrochen", "en_US": "🗑️ Abgebrochen"}'::jsonb, 6, true, true)
ON CONFLICT DO NOTHING;
"""
    run_sql_script(sql_stages)
    print("[OK] Project task stages harmonized!")

    print("\n=== Step 4: Configuring Global System Parameters ===")
    sql_params = """
-- Set global system parameters in ir_config_parameter
DELETE FROM ir_config_parameter WHERE key IN ('web.base.url', 'frawo.company_name', 'frawo.default_lang');
INSERT INTO ir_config_parameter (key, value, create_date, write_date)
VALUES 
    ('web.base.url', 'https://frawo.tech', NOW(), NOW()),
    ('frawo.company_name', 'FraWo GbR', NOW(), NOW()),
    ('frawo.default_lang', 'de_DE', NOW(), NOW());
"""
    run_sql_script(sql_params)
    print("[OK] Global system parameters configured!")

if __name__ == "__main__":
    main()

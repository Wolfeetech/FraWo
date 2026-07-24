import subprocess
import json
import sys

# Script to correct Martin Audio CX2 equipment records and create Maintenance Repair Requests

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
    print("=== Correcting Martin Audio CX2 Equipment Records in Odoo ===")
    sql_fix_equipment = """
-- Update Equipment ID 6
UPDATE maintenance_equipment
SET 
    name = '{"de_DE": "Martin Audio CX2 Coaxial Top (LS 1)", "en_US": "Martin Audio CX2 Coaxial Top (LS 1)"}'::jsonb,
    category_id = 2,
    model = 'Martin Audio CX2 Coaxial 2-Way Speaker Top',
    location = 'Rothkreuz - Ton-Lager / Werkstatt',
    serial_no = 'MARTIN-AUDIO-CX2-01',
    note = 'Martin Audio CX2 Coaxial PA-Topteil. DEFEKT: Coaxial-Treiber tot / kein Ton. Reparaturauftrag in Odoo angelegt.',
    equipment_assign_to = 'other',
    effective_date = CURRENT_DATE,
    write_date = NOW()
WHERE id = 6;

-- Update Equipment ID 7
UPDATE maintenance_equipment
SET 
    name = '{"de_DE": "Martin Audio CX2 Coaxial Top (LS 2)", "en_US": "Martin Audio CX2 Coaxial Top (LS 2)"}'::jsonb,
    category_id = 2,
    model = 'Martin Audio CX2 Coaxial 2-Way Speaker Top',
    location = 'Rothkreuz - Ton-Lager / Werkstatt',
    serial_no = 'MARTIN-AUDIO-CX2-02',
    note = 'Martin Audio CX2 Coaxial PA-Topteil. DEFEKT: Coaxial-Treiber tot / kein Ton. Reparaturauftrag in Odoo angelegt.',
    equipment_assign_to = 'other',
    effective_date = CURRENT_DATE,
    write_date = NOW()
WHERE id = 7;

-- Create Repair Request for Martin Audio CX2 (1)
INSERT INTO maintenance_request (
    name, company_id, maintenance_team_id, kanban_state, equipment_id, category_id, maintenance_type, priority, stage_id, request_date, description, create_date, write_date
) VALUES (
    '🔴 Reparatur: Martin Audio CX2 (LS 1) — Coaxial Treiber tot',
    1, 1, 'normal', 6, 2, 'corrective', '3', 1, CURRENT_DATE,
    'Coaxial-Treiber defekt (kein Ton / tot). Überprüfung der Spule, Frequenzweiche oder Recone-Kit / Ersatz-Chassis erforderlich.',
    NOW(), NOW()
);

-- Create Repair Request for Martin Audio CX2 (2)
INSERT INTO maintenance_request (
    name, company_id, maintenance_team_id, kanban_state, equipment_id, category_id, maintenance_type, priority, stage_id, request_date, description, create_date, write_date
) VALUES (
    '🔴 Reparatur: Martin Audio CX2 (LS 2) — Coaxial Treiber tot',
    1, 1, 'normal', 7, 2, 'corrective', '3', 1, CURRENT_DATE,
    'Coaxial-Treiber defekt (kein Ton / tot). Überprüfung der Spule, Frequenzweiche oder Recone-Kit / Ersatz-Chassis erforderlich.',
    NOW(), NOW()
);
"""
    run_sql_script(sql_fix_equipment)
    print("[OK] Martin Audio CX2 equipment records & repair requests updated successfully!")

if __name__ == "__main__":
    main()

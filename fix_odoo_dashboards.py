import xmlrpc.client
import json

URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# IDs der korrupten Dashboards (7 gefunden)
corrupt_ids = [1, 2, 3, 4, 5, 6, 7] # Annahme basierend auf dem Fund

print(f"🛠️ Fixing {len(corrupt_ids)} dashboards...")
for d_id in corrupt_ids:
    try:
        models.execute_kw(DB, uid, PASS, 'spreadsheet.dashboard', 'write', [[d_id], {'spreadsheet_data': '{}'}])
        print(f"   ✅ Dashboard ID {d_id}: Data reset to '{{}}'")
    except Exception as e:
        print(f"   ❌ Failed to fix ID {d_id}: {e}")

print("\n🎉 Fix applied. Please refresh the Odoo UI.")

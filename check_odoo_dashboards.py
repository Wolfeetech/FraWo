import xmlrpc.client
import json

URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

print("--- Searching for Corrupt Dashboards ---")
# Suche nach leeren oder ungültigen Dashboard-Daten
dashboards = models.execute_kw(DB, uid, PASS, 'spreadsheet.dashboard', 'search_read', [[]], {'fields': ['name', 'spreadsheet_data']})

corrupt_ids = []
for d in dashboards:
    data = d.get('spreadsheet_data')
    if not data or data == "" or data == "false":
        print(f"❌ Found Corrupt Dashboard: '{d['name']}' (ID: {d['id']}) - Data is empty/false")
        corrupt_ids.append(d['id'])
    else:
        try:
            json.loads(data)
        except Exception as e:
            print(f"❌ Found Corrupt Dashboard: '{d['name']}' (ID: {d['id']}) - Invalid JSON: {e}")
            corrupt_ids.append(d['id'])

if corrupt_ids:
    print(f"\n💡 Proposal: Resetting {len(corrupt_ids)} dashboards to '{{}}' to fix the RPC error.")
else:
    print("✅ No corrupt dashboards found via search_read.")

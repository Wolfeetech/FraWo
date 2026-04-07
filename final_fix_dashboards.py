import xmlrpc.client

URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# Suche alle Dashboards mit leerem spreadsheet_data
try:
    corrupt_ids = models.execute_kw(DB, uid, PASS, 'spreadsheet.dashboard', 'search', [
        ['|', ('spreadsheet_data', '=', False), ('spreadsheet_data', '=', '')]
    ])
    
    print(f"🛠️ Fixing {len(corrupt_ids)} corrupt dashboards...")
    for d_id in corrupt_ids:
        models.execute_kw(DB, uid, PASS, 'spreadsheet.dashboard', 'write', [[d_id], {'spreadsheet_data': '{}'}])
        print(f"   ✅ Fixed ID {d_id}")
    
    print("\n🎉 All corrupt dashboards corrected. Please refresh the Odoo UI.")
except Exception as e:
    print(f"❌ Error during fix: {e}")

import xmlrpc.client
URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

# 1. Odoo Mail Server Check
servers = models.execute_kw(DB, uid, PASS, 'ir.mail_server', 'search_read', [[('smtp_user', '=', 'noreply@frawo-tech.de')]], {'fields': ['name', 'smtp_host', 'smtp_port']})
if not servers:
    print("❌ Kein Mailserver für noreply@frawo-tech.de gefunden.")
else:
    for s in servers:
        print(f"✅ Mailserver gefunden: {s['name']} ({s['smtp_host']})")
        # Test (Odoo 17 method)
        try:
            res = models.execute_kw(DB, uid, PASS, 'ir.mail_server', 'test_smtp_connection', [s['id']])
            print(f"🚀 Odoo SMTP Test Result: {res}")
        except Exception as e:
            print(f"❌ Odoo SMTP Test fehlgeschlagen: {e}")

# 2. Nextcloud Check (Versuch via SSH/OCC auf der Nextcloud VM)
# Die Nextcloud VM hat die IP 10.1.0.21.

import xmlrpc.client
URL = "http://10.1.0.22:8069"
DB = "FraWo_GbR"
USER = "wolf@frawo-tech.de"
PASS = "OD-Wolf-2026!"

common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
uid = common.authenticate(DB, USER, PASS, {})
models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")

print("--- Odoo Outgoing Mail Servers ---")
servers = models.execute_kw(DB, uid, PASS, 'ir.mail_server', 'search_read', [[]], {'fields': ['name', 'smtp_user', 'smtp_host', 'smtp_port', 'smtp_encryption']})
for s in servers:
    print(s)

print("\n--- Odoo System Parameters for Mail ---")
params = models.execute_kw(DB, uid, PASS, 'ir.config_parameter', 'search_read', [[('key', 'ilike', 'mail')]], {'fields': ['key', 'value']})
for p in params:
    print(p)

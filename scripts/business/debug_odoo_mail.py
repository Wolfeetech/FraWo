from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

print("--- Odoo Outgoing Mail Servers ---")
servers = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "ir.mail_server",
    "search_read",
    [[]],
    {"fields": ["name", "smtp_user", "smtp_host", "smtp_port", "smtp_encryption"]},
)
for server in servers:
    print(server)

print("\n--- Odoo System Parameters for Mail ---")
params = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "ir.config_parameter",
    "search_read",
    [[("key", "ilike", "mail")]],
    {"fields": ["key", "value"]},
)
for param in params:
    print(param)

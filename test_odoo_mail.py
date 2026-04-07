from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

servers = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "ir.mail_server",
    "search_read",
    [[("smtp_user", "=", "noreply@frawo-tech.de")]],
    {"fields": ["name", "smtp_host", "smtp_port"]},
)

if not servers:
    print("Kein Mailserver fuer noreply@frawo-tech.de gefunden.")
else:
    for server in servers:
        print(f"Mailserver gefunden: {server['name']} ({server['smtp_host']})")
        try:
            result = session.models.execute_kw(
                session.db,
                session.uid,
                session.secret,
                "ir.mail_server",
                "test_smtp_connection",
                [server["id"]],
            )
            print(f"Odoo SMTP Test Result: {result}")
        except Exception as exc:
            print(f"Odoo SMTP Test fehlgeschlagen: {exc}")

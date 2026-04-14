from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

try:
    print("Trigger SMTP Connection Test for Odoo (Server ID 1)...")
    result = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "ir.mail_server",
        "test_smtp_connection",
        [1],
    )
    print(f"Result: {result}")
except Exception as exc:
    print(f"Odoo Mail Test Error: {exc}")

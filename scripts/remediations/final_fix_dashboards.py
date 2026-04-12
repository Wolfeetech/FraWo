from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

corrupt_ids = [1, 2, 3, 4, 5, 6, 7]

print(f"Fixing {len(corrupt_ids)} dashboards...")
for dashboard_id in corrupt_ids:
    try:
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "spreadsheet.dashboard",
            "write",
            [[dashboard_id], {"spreadsheet_data": "{}"}],
        )
        print(f"Dashboard ID {dashboard_id}: Data reset to '{{}}'")
    except Exception as exc:
        print(f"Failed to fix ID {dashboard_id}: {exc}")

print("\nFix applied. Please refresh the Odoo UI.")

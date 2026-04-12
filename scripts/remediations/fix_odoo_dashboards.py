from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

try:
    corrupt_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "spreadsheet.dashboard",
        "search",
        [["|", ("spreadsheet_data", "=", False), ("spreadsheet_data", "=", "")]],
    )

    print(f"Fixing {len(corrupt_ids)} corrupt dashboards...")
    for dashboard_id in corrupt_ids:
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "spreadsheet.dashboard",
            "write",
            [[dashboard_id], {"spreadsheet_data": "{}"}],
        )
        print(f"Fixed ID {dashboard_id}")

    print("\nAll corrupt dashboards corrected. Please refresh the Odoo UI.")
except Exception as exc:
    print(f"Error during fix: {exc}")

import json

from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

print("--- Searching for Corrupt Dashboards ---")
dashboards = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "spreadsheet.dashboard",
    "search_read",
    [[]],
    {"fields": ["name", "spreadsheet_data"]},
)

corrupt_ids = []
for dashboard in dashboards:
    data = dashboard.get("spreadsheet_data")
    if not data or data in {"", "false"}:
        print(
            f"Found Corrupt Dashboard: '{dashboard['name']}' "
            f"(ID: {dashboard['id']}) - Data is empty/false"
        )
        corrupt_ids.append(dashboard["id"])
        continue

    try:
        json.loads(data)
    except Exception as exc:
        print(
            f"Found Corrupt Dashboard: '{dashboard['name']}' "
            f"(ID: {dashboard['id']}) - Invalid JSON: {exc}"
        )
        corrupt_ids.append(dashboard["id"])

if corrupt_ids:
    print(f"\nProposal: Resetting {len(corrupt_ids)} dashboards to '{{}}'.")
else:
    print("No corrupt dashboards found via search_read.")

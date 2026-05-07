from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")
projects = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "project.project",
    "search_read",
    [[]],
    {"fields": ["name"]},
)

for project in projects:
    print(f"Project: {project['name']} (ID: {project['id']})")

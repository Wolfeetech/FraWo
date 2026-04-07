from odoo_rpc_client import connect


session = connect(default_user="wolf@frawo-tech.de")

project_ids = [12, 13]
tasks = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "project.task",
    "search_read",
    [[("project_id", "in", project_ids)]],
    {"fields": ["name", "description", "project_id", "stage_id", "tag_ids"]},
)

print("--- Tasks in Projekten 12 & 13 ---")
for task in tasks:
    print(f"ID: {task['id']} | Project: {task['project_id'][1]} | Name: {task['name']}")

agent_user = session.models.execute_kw(
    session.db,
    session.uid,
    session.secret,
    "res.users",
    "search_read",
    [[("name", "ilike", "Agent")]],
    {"fields": ["name", "login"]},
)
print("\n--- User 'Agent' Check ---")
print(agent_user)

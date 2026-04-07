from odoo_rpc_client import connect


PROJECT_NAME = "Private Networking (Masterplan)"


def sync() -> None:
    print("Odoo Advanced Masterplan Sync")
    session = connect(
        default_user="wolf@frawo-tech.de",
        prompt_for_username=True,
    )
    print(f"Ziel: {session.url} | Projekt: '{PROJECT_NAME}'")

    project_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.project",
        "search",
        [[("name", "=", PROJECT_NAME)]],
    )
    if not project_ids:
        print(f"Erstelle Projekt: '{PROJECT_NAME}'")
        project_id = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.project",
            "create",
            [{"name": PROJECT_NAME}],
        )
    else:
        project_id = project_ids[0]

    tag_map = {}
    for tag_name in ["Infrastructure", "Security", "Audit", "MVP"]:
        existing = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.tags",
            "search",
            [[("name", "=", tag_name)]],
        )
        tag_id = existing[0] if existing else session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.tags",
            "create",
            [{"name": tag_name}],
        )
        tag_map[tag_name] = tag_id

    user_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "res.users",
        "search",
        [[("name", "ilike", "Wolf")]],
    )
    wolf_id = user_ids[0] if user_ids else session.uid

    tasks_to_sync = [
        {
            "name": "Vaultwarden Recovery-Material verifizieren",
            "description": "<ul><li>[ ] Zwei getrennte physische Offline-Kopien sicherstellen.</li></ul>",
            "project_id": project_id,
            "user_ids": [wolf_id],
            "tag_ids": [tag_map["Security"], tag_map["MVP"]],
            "priority": "1",
        },
        {
            "name": "Geraete-Rollout abnehmen (Surface & iPhone)",
            "description": "<ul><li>[ ] Franz Endgeraete im Alltagspfad verifizieren.</li></ul>",
            "project_id": project_id,
            "user_ids": [wolf_id],
            "tag_ids": [tag_map["Infrastructure"]],
            "priority": "0",
        },
        {
            "name": "Tailscale Route freigeben (10.1.0.0/24)",
            "description": "<ul><li>[ ] Approve Route in Tailscale Admin Panel.</li></ul>",
            "project_id": project_id,
            "user_ids": [wolf_id],
            "tag_ids": [tag_map["Infrastructure"], tag_map["Security"]],
            "priority": "1",
        },
        {
            "name": "Tailscale Split-DNS (hs27.internal)",
            "description": "<ul><li>[ ] Nameserver 10.1.0.20 hinzufuegen.</li></ul>",
            "project_id": project_id,
            "user_ids": [wolf_id],
            "tag_ids": [tag_map["Infrastructure"]],
            "priority": "1",
        },
    ]

    print("Synchronisiere Aufgaben...")
    for task_data in tasks_to_sync:
        existing_task = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "search",
            [[("name", "=", task_data["name"]), ("project_id", "=", project_id)]],
        )
        if existing_task:
            print(f"Ueberspringe (existiert bereits): {task_data['name']}")
            continue

        task_id = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "create",
            [task_data],
        )
        print(f"Erstellt: {task_data['name']} (ID: {task_id})")

    print("Odoo-Sync erfolgreich abgeschlossen.")


if __name__ == "__main__":
    sync()

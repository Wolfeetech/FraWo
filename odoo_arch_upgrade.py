#!/usr/bin/env python3
"""
FRAWO Homeserver 2027 - Odoo Architecture Upgrade
=================================================
1. Erstellt User "Agent" (agent@frawo-tech.de)
2. Konsolidiert alte Infra-/Roadmap-Projekte in den Masterplan
3. Erstellt Automation Stage und Tags
"""

from odoo_rpc_client import connect


def main() -> None:
    print("Odoo Architecture Upgrade - Start...")
    session = connect(default_user="wolf@frawo-tech.de")
    print(f"Eingeloggt als UID {session.uid}")

    existing_agent = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "res.users",
        "search",
        [[("login", "=", "agent@frawo-tech.de")]],
    )
    if existing_agent:
        agent_uid = existing_agent[0]
        print(f"Agent existiert bereits (UID {agent_uid})")
    else:
        agent_uid = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "res.users",
            "create",
            [{
                "name": "Agent",
                "login": "agent@frawo-tech.de",
                "email": "agent@frawo-tech.de",
                "notification_type": "email",
                "groups_id": [(6, 0, [1, 2])],
            }],
        )
        print(f"Agent angelegt (UID {agent_uid})")

    master_project = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.project",
        "search",
        [[("name", "=", "Homeserver 2027: Masterplan")]],
    )
    if not master_project:
        raise RuntimeError("Masterprojekt nicht gefunden.")
    master_project_id = master_project[0]

    automation_stage_name = "Automatisierung"
    existing_stage = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.task.type",
        "search",
        [[("name", "=", automation_stage_name)]],
    )
    if existing_stage:
        automation_stage_id = existing_stage[0]
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task.type",
            "write",
            [[automation_stage_id], {"project_ids": [(4, master_project_id)]}],
        )
    else:
        automation_stage_id = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task.type",
            "create",
            [{
                "name": automation_stage_name,
                "sequence": 35,
                "project_ids": [(4, master_project_id)],
            }],
        )
    print(f"Stage bereit (ID {automation_stage_id})")

    for tag_name in ["OCR: Beleg", "INV: Rechnung"]:
        existing_tag = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.tags",
            "search",
            [[("name", "=", tag_name)]],
        )
        if not existing_tag:
            session.models.execute_kw(
                session.db,
                session.uid,
                session.secret,
                "project.tags",
                "create",
                [{"name": tag_name}],
            )
        print(f"Tag bereit: {tag_name}")

    source_project_ids = [12, 13]
    tasks = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.task",
        "search_read",
        [[("project_id", "in", source_project_ids)]],
        {"fields": ["name", "description", "user_ids", "project_id"]},
    )

    infra_tag = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.tags",
        "search",
        [[("name", "=", "Lane C: Infra")]],
    )
    roadmap_tag = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.tags",
        "search",
        [[("name", "=", "Lane B: Website")]],
    )

    for task in tasks:
        new_tags = []
        if task["project_id"][0] == 12:
            new_tags = infra_tag
        if task["project_id"][0] == 13:
            new_tags = roadmap_tag

        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "write",
            [[task["id"]], {"project_id": master_project_id, "tag_ids": [(4, tag) for tag in new_tags]}],
        )
        print(f"Verschoben: {task['name']}")

    for project_id in source_project_ids:
        try:
            session.models.execute_kw(
                session.db,
                session.uid,
                session.secret,
                "project.project",
                "unlink",
                [[project_id]],
            )
            print(f"Geloescht: ID {project_id}")
        except Exception:
            print(f"ID {project_id} konnte nicht geloescht werden")

    print("Odoo Architektur-Upgrade abgeschlossen.")


if __name__ == "__main__":
    main()

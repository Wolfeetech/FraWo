#!/usr/bin/env python3
"""
FRAWO Homeserver 2027 - Odoo Project Management Best Practice Optimizer
"""

from odoo_rpc_client import connect


def main() -> None:
    print("Odoo Best Practice Optimizer - Start...")
    session = connect(default_user="wolf@frawo-tech.de")
    print(f"Eingeloggt als UID {session.uid}")

    project_name = "Homeserver 2027: Masterplan"
    existing_project = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.project",
        "search",
        [[("name", "=", project_name)]],
    )

    if existing_project:
        master_project_id = existing_project[0]
        print(f"Master-Projekt existiert bereits (ID {master_project_id})")
    else:
        master_project_id = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.project",
            "create",
            [{
                "name": project_name,
                "description": "Zentrales operatives Board fuer Homeserver 2027.",
                "privacy_visibility": "employees",
            }],
        )
        print(f"Master-Projekt angelegt (ID {master_project_id})")

    stages = [
        {"name": "Backlog", "sequence": 10},
        {"name": "Planung", "sequence": 20},
        {"name": "In Arbeit", "sequence": 30},
        {"name": "Blockiert", "sequence": 40},
        {"name": "Erledigt", "sequence": 50},
    ]

    stage_id_map = {}
    for stage in stages:
        existing_stage = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task.type",
            "search",
            [[("name", "=", stage["name"])]],
        )
        if existing_stage:
            stage_id = existing_stage[0]
            session.models.execute_kw(
                session.db,
                session.uid,
                session.secret,
                "project.task.type",
                "write",
                [[stage_id], {"project_ids": [(4, master_project_id)]}],
            )
        else:
            stage_id = session.models.execute_kw(
                session.db,
                session.uid,
                session.secret,
                "project.task.type",
                "create",
                [{
                    "name": stage["name"],
                    "sequence": stage["sequence"],
                    "project_ids": [(4, master_project_id)],
                }],
            )
        stage_id_map[stage["name"]] = stage_id
        print(f"Stage bereit: {stage['name']}")

    lane_tags = {
        "Lane A": "Lane A: MVP",
        "Lane B": "Lane B: Website",
        "Lane C": "Lane C: Infra",
        "Lane D": "Lane D: Stockenweiler",
        "Lane E": "Lane E: Radio & Media",
    }

    tag_id_map = {}
    for lane, tag_name in lane_tags.items():
        existing_tag = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.tags",
            "search",
            [[("name", "=", tag_name)]],
        )
        if existing_tag:
            tag_id = existing_tag[0]
        else:
            tag_id = session.models.execute_kw(
                session.db,
                session.uid,
                session.secret,
                "project.tags",
                "create",
                [{"name": tag_name}],
            )
        tag_id_map[lane] = tag_id
        print(f"Tag bereit: {tag_name}")

    source_project_names = [
        "Homeserver 2027: MVP Closeout (Lane A)",
        "Homeserver 2027: Website Release (Lane B)",
        "Homeserver 2027: Security & Infra (Lane C)",
        "Homeserver 2027: Stockenweiler (Lane D)",
        "Homeserver 2027: Radio & Media (Lane E)",
    ]

    source_project_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.project",
        "search",
        [[("name", "in", source_project_names)]],
    )

    tasks = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.task",
        "search_read",
        [[("project_id", "in", source_project_ids)]],
        {"fields": ["name", "description", "project_id", "priority", "tag_ids"]},
    )

    print(f"Optimiere {len(tasks)} Tasks...")
    for task in tasks:
        parent_project = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.project",
            "read",
            [task["project_id"][0]],
            {"fields": ["name"]},
        )
        parent_name = parent_project[0]["name"]

        target_lane = None
        for lane in lane_tags:
            if lane in parent_name:
                target_lane = lane
                break

        target_stage_name = "Backlog"
        description = task["description"] or ""
        if "ERLEDIGT" in description.upper() or "[x]" in description:
            target_stage_name = "Erledigt"
        elif "BLOCK" in description.upper():
            target_stage_name = "Blockiert"

        update_data = {
            "project_id": master_project_id,
            "stage_id": stage_id_map[target_stage_name],
            "tag_ids": [(4, tag_id_map[target_lane])] if target_lane else [],
        }
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "write",
            [[task["id"]], update_data],
        )
        print(f"Migriert: {task['name']} -> {target_stage_name}")

    for project_id in source_project_ids:
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.project",
            "unlink",
            [[project_id]],
        )
        print(f"Geloescht: Projekt ID {project_id}")

    print("Odoo Best Practice Struktur ist jetzt live.")


if __name__ == "__main__":
    main()

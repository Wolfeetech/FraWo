from __future__ import annotations

import sys
import xmlrpc.client
from collections import Counter
from typing import Any

from odoo_env import resolve_connection


DEFAULT_URL = "http://100.82.26.53:8444"
DEFAULT_DB = "FraWo_GbR"
DEFAULT_USER = "wolf@frawo-tech.de"
PROJECT_NAME_NEEDLE = "Homeserver 2027: Masterplan"


def xmlrpc_call(
    models: xmlrpc.client.ServerProxy,
    db: str,
    uid: int,
    secret: str,
    model: str,
    method: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Any:
    return models.execute_kw(db, uid, secret, model, method, args or [], kwargs or {})


def format_stage(stage_value: Any) -> str:
    if isinstance(stage_value, list) and len(stage_value) >= 2:
        return str(stage_value[1])
    return "-"


def main() -> int:
    try:
        settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    common = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(settings.db, settings.user, settings.secret, {})
    if not uid:
        print("Authentifizierung fehlgeschlagen.", file=sys.stderr)
        return 1

    models = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/object", allow_none=True)
    project = xmlrpc_call(
        models,
        settings.db,
        uid,
        settings.secret,
        "project.project",
        "search_read",
        [[["name", "ilike", PROJECT_NAME_NEEDLE]]],
        {"fields": ["name"], "limit": 1},
    )
    if not project:
        print(f"Projekt mit Name-Needle '{PROJECT_NAME_NEEDLE}' nicht gefunden.", file=sys.stderr)
        return 1

    project_record = project[0]
    tasks = xmlrpc_call(
        models,
        settings.db,
        uid,
        settings.secret,
        "project.task",
        "search_read",
        [[["project_id", "=", project_record["id"]]]],
        {
            "fields": ["name", "stage_id", "priority", "date_deadline", "write_date"],
            "order": "priority desc, write_date desc",
        },
    )

    print(f"Projekt: {project_record['name']} ({len(tasks)} Tasks)")
    stage_counter = Counter(format_stage(task.get("stage_id")) for task in tasks)
    for stage_name, count in sorted(stage_counter.items()):
        print(f"- {stage_name}: {count}")

    print("\nTasks:")
    for task in tasks:
        stage_name = format_stage(task.get("stage_id"))
        deadline = task.get("date_deadline") or "-"
        updated = task.get("write_date") or "-"
        print(f"- {task['name']} | Stage: {stage_name} | Deadline: {deadline} | Updated: {updated}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

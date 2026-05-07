from __future__ import annotations

import argparse
import html
import sys
import xmlrpc.client
from datetime import datetime
from pathlib import Path
from typing import Any

from odoo_env import resolve_connection


DEFAULT_URL = "http://100.82.26.53:8444"
DEFAULT_DB = "FraWo_GbR"
DEFAULT_USER = "wolf@frawo-tech.de"
DEFAULT_PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"


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


def connect_odoo() -> tuple[Any, xmlrpc.client.ServerProxy, int]:
    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    common = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(settings.db, settings.user, settings.secret, {})
    if not uid:
        raise RuntimeError("Authentifizierung fehlgeschlagen.")
    models = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/object", allow_none=True)
    return settings, models, uid


def markdownish_to_html(text: str) -> str:
    blocks: list[str] = []
    list_items: list[str] = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            blocks.append("<ul>" + "".join(list_items) + "</ul>")
            list_items = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            flush_list()
            continue
        if line.startswith("#"):
            flush_list()
            blocks.append(f"<h3>{html.escape(line.lstrip('#').strip())}</h3>")
            continue
        if line.startswith("- "):
            list_items.append(f"<li>{html.escape(line[2:].strip())}</li>")
            continue
        flush_list()
        blocks.append(f"<p>{html.escape(line)}</p>")

    flush_list()
    return "".join(blocks)


def find_project(models: xmlrpc.client.ServerProxy, db: str, uid: int, secret: str, project_name: str) -> dict[str, Any]:
    projects = xmlrpc_call(
        models,
        db,
        uid,
        secret,
        "project.project",
        "search_read",
        [[["name", "ilike", project_name]]],
        {"fields": ["name"], "limit": 1},
    )
    if not projects:
        raise RuntimeError(f"Projekt mit Name-Needle '{project_name}' nicht gefunden.")
    return projects[0]


def upsert_progress(
    project_name: str,
    task_name: str,
    note_html: str,
    *,
    create_missing: bool,
    apply: bool,
) -> int:
    try:
        settings, models, uid = connect_odoo()
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    project = find_project(models, settings.db, uid, settings.secret, project_name)
    tasks = xmlrpc_call(
        models,
        settings.db,
        uid,
        settings.secret,
        "project.task",
        "search_read",
        [[["project_id", "=", project["id"]], ["name", "=", task_name]]],
        {"fields": ["name", "description"], "limit": 1},
    )

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    section_html = f"<hr/><h3>Progress Update {html.escape(timestamp)}</h3>{note_html}"

    if tasks:
        task = tasks[0]
        new_description = (task.get("description") or "") + section_html
        print(f"{'APPLY' if apply else 'DRY-RUN'} update task: {task_name}")
        if apply:
            xmlrpc_call(
                models,
                settings.db,
                uid,
                settings.secret,
                "project.task",
                "write",
                [[task["id"]], {"description": new_description}],
            )
        return 0

    if not create_missing:
        print(f"Task nicht gefunden: {task_name}", file=sys.stderr)
        return 1

    print(f"{'APPLY' if apply else 'DRY-RUN'} create task: {task_name}")
    if apply:
        xmlrpc_call(
            models,
            settings.db,
            uid,
            settings.secret,
            "project.task",
            "create",
            [{
                "name": task_name,
                "project_id": project["id"],
                "description": section_html,
            }],
        )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Haengt eine Fortschrittsnotiz an einen Odoo-Task an.")
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME, help="Projektname oder Needle.")
    parser.add_argument("--task-name", required=True, help="Exakter Taskname fuer die Fortschrittsnotiz.")
    parser.add_argument("--body-file", required=True, help="Markdown- oder Textdatei mit der Fortschrittsnotiz.")
    parser.add_argument("--create-missing", action="store_true", help="Legt den Task an, falls er fehlt.")
    parser.add_argument("--apply", action="store_true", help="Wendet die Aenderung wirklich an.")
    args = parser.parse_args()

    body_path = Path(args.body_file)
    note_html = markdownish_to_html(body_path.read_text(encoding="utf-8"))
    return upsert_progress(
        project_name=args.project_name,
        task_name=args.task_name,
        note_html=note_html,
        create_missing=args.create_missing,
        apply=args.apply,
    )


if __name__ == "__main__":
    raise SystemExit(main())

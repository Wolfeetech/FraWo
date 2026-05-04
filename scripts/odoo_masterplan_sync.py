from __future__ import annotations

import argparse
import html
import re
import sys
import xmlrpc.client
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from odoo_env import resolve_connection


DEFAULT_URL = "http://100.82.26.53:8444"
DEFAULT_DB = "FraWo_GbR"
DEFAULT_USER = "wolf@frawo-tech.de"
DEFAULT_PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"
MASTERPLAN_PATH = Path(__file__).resolve().parents[1] / "MASTERPLAN.md"

STAGE_MAP = {
    "active": "🚀 In Arbeit",
    "active/prov": "⚙️ Planung & Vorbereitung",
    "watch": "🛑 Blockiert",
    "blocked": "🛑 Blockiert",
    "sealed": "✅ Erledigt",
    "done": "✅ Erledigt",
    "erledigt": "✅ Erledigt",
}


@dataclass
class Lane:
    key: str
    title: str
    status: str
    bullets: list[str]

    @property
    def task_name(self) -> str:
        return f"[{self.key}] {self.title}"

    @property
    def desired_stage(self) -> str:
        return STAGE_MAP.get(self.status.lower(), "📝 Backlog")


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


def parse_masterplan(text: str) -> list[Lane]:
    heading_re = re.compile(r"^### (Lane [A-E]): (.+) - \[STATUS: (.+)\]$")
    lanes: list[Lane] = []
    current: Lane | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        heading_match = heading_re.match(line)
        if heading_match:
            current = Lane(
                key=heading_match.group(1),
                title=heading_match.group(2).strip(),
                status=heading_match.group(3).strip(),
                bullets=[],
            )
            lanes.append(current)
            continue

        if current is None:
            continue

        stripped = line.strip()
        if stripped.startswith("### "):
            current = None
            continue

        if stripped.startswith("- "):
            current.bullets.append(stripped[2:].strip())
        elif re.match(r"^\d+\.\s", stripped):
            current.bullets.append(stripped)

    return lanes


def lane_description(lane: Lane) -> str:
    bullets = "".join(f"<li>{html.escape(item)}</li>" for item in lane.bullets)
    return (
        f"<p><strong>Status:</strong> {html.escape(lane.status)}</p>"
        f"<ul>{bullets}</ul>"
    )


def connect_odoo() -> tuple[Any, xmlrpc.client.ServerProxy, int]:
    settings = resolve_connection(DEFAULT_URL, DEFAULT_DB, DEFAULT_USER)
    common = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(settings.db, settings.user, settings.secret, {})
    if not uid:
        raise RuntimeError("Authentifizierung fehlgeschlagen.")
    models = xmlrpc.client.ServerProxy(f"{settings.url}/xmlrpc/2/object", allow_none=True)
    return settings, models, uid


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


def find_stage_id(
    models: xmlrpc.client.ServerProxy,
    db: str,
    uid: int,
    secret: str,
    stage_name: str,
) -> int | None:
    stages = xmlrpc_call(
        models,
        db,
        uid,
        secret,
        "project.task.type",
        "search_read",
        [[["name", "ilike", stage_name]]],
        {"fields": ["name"], "limit": 1},
    )
    if not stages:
        return None
    return stages[0]["id"]


def sync_lanes(project_name: str, apply: bool) -> int:
    lanes = parse_masterplan(MASTERPLAN_PATH.read_text(encoding="utf-8"))
    if not lanes:
        print("Keine Lanes im MASTERPLAN gefunden.", file=sys.stderr)
        return 1

    try:
        settings, models, uid = connect_odoo()
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1

    project = find_project(models, settings.db, uid, settings.secret, project_name)
    print(f"Projekt: {project['name']}")
    print("Modus:", "APPLY" if apply else "DRY-RUN")

    stage_cache: dict[str, int | None] = {}
    for lane in lanes:
        desired_stage = lane.desired_stage
        if desired_stage not in stage_cache:
            stage_cache[desired_stage] = find_stage_id(
                models, settings.db, uid, settings.secret, desired_stage
            )

        existing = xmlrpc_call(
            models,
            settings.db,
            uid,
            settings.secret,
            "project.task",
            "search_read",
            [[["project_id", "=", project["id"]], ["name", "=", lane.task_name]]],
            {"fields": ["name", "stage_id", "description"], "limit": 1},
        )

        payload: dict[str, Any] = {
            "name": lane.task_name,
            "description": lane_description(lane),
            "project_id": project["id"],
        }
        stage_id = stage_cache.get(desired_stage)
        if stage_id:
            payload["stage_id"] = stage_id

        if existing:
            existing_record = existing[0]
            current_stage = existing_record.get("stage_id")
            current_stage_name = current_stage[1] if isinstance(current_stage, list) and len(current_stage) > 1 else "-"
            print(f"- UPDATE {lane.task_name} -> Stage {current_stage_name} => {desired_stage}")
            if apply:
                xmlrpc_call(
                    models,
                    settings.db,
                    uid,
                    settings.secret,
                    "project.task",
                    "write",
                    [[existing_record["id"]], payload],
                )
        else:
            print(f"- CREATE {lane.task_name} -> Stage {desired_stage}")
            if apply:
                xmlrpc_call(
                    models,
                    settings.db,
                    uid,
                    settings.secret,
                    "project.task",
                    "create",
                    [payload],
                )

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronisiert Lane-Tasks aus MASTERPLAN nach Odoo.")
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME, help="Projektname oder Needle fuer das Odoo-Projekt.")
    parser.add_argument("--apply", action="store_true", help="Wendet die Aenderungen wirklich an.")
    args = parser.parse_args()
    return sync_lanes(project_name=args.project_name, apply=args.apply)


if __name__ == "__main__":
    raise SystemExit(main())

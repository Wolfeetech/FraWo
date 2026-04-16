from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from typing import Any

from odoo_rpc_client import OdooSession, connect


CANONICAL_PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"
PROJECT_NAME_NEEDLE = "Homeserver 2027: Masterplan"

WOLF_LOGIN = "wolf@frawo-tech.de"
FRANZ_LOGIN = "franz@frawo-tech.de"
AGENT_LOGIN = "agent@frawo-tech.de"
ROOTFLO_LOGIN = "rootflo2525@gmail.com"

STAGE_SPECS = [
    {"name": "📝 Backlog", "sequence": 10},
    {"name": "⚙️ Planung & Vorbereitung", "sequence": 20},
    {"name": "🚀 In Arbeit", "sequence": 30},
    {"name": "🤖 Automatisierung", "sequence": 35},
    {"name": "🛑 Blockiert", "sequence": 40},
    {"name": "✅ Erledigt", "sequence": 50},
]

LANE_TAG_NAMES = {
    "lane_a": "Lane A: MVP",
    "lane_b": "Lane B: Website",
    "lane_c": "Lane C: Infra",
    "lane_d": "Lane D: Stockenweiler",
    "lane_e": "Lane E: Radio & Media",
}

LEAST_PRIVILEGE_GROUP_XMLIDS = [
    "base.group_user",
    "project.group_project_user",
]

ODOO_CONTEXT = {
    "tracking_disable": True,
    "mail_create_nosubscribe": True,
    "mail_auto_subscribe_no_notify": True,
    "mail_notify_force_send": False,
    "default_notify": False,
}

EXISTING_TASK_RULES = [
    {
        "match": "Service Reachability Audit",
        "owners": [WOLF_LOGIN],
        "stage": "✅ Erledigt",
    },
    {
        "match": "Odoo External Access (frawo-tech.de)",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "Port-Weiterleitung 80/443 auf UCG-Ultra",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "PHP-Syntax Korrektur (SUB-Zeichen)",
        "owners": [WOLF_LOGIN],
    },
    {
        "match": "Git-Bereinigung Radio-Node (4K Commits)",
        "owners": [WOLF_LOGIN],
    },
    {
        "match": "AdGuard Home Pilot",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "Tailscale Finalisierung",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "Mail Rollout",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
        "stage": "✅ Erledigt",
    },
    {
        "match": "MVP Gate Audit",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
        "stage": "✅ Erledigt",
    },
    {
        "match": "Vaultwarden Recovery",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "Vaultwarden Recovery-Material verifizieren",
        "owners": [WOLF_LOGIN],
        "stage": "✅ Erledigt",
    },
    {
        "match": "Geräte-Rollout",
        "owners": [WOLF_LOGIN],
        "stage": "✅ Erledigt",
    },
    {
        "match": "Wolf & Franz Login-Walkthrough",
        "owners": [WOLF_LOGIN],
        "stage": "✅ Erledigt",
    },
    {
        "match": "DNS Rollback dokumentieren",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "PBS Guarded Rebuild (VM 240)",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
    {
        "match": "AdGuard Home als primärer LAN-DNS",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
    },
]

NEW_TASK_SPECS = [
    {
        "name": "Unified Brand Rollout: CI-Farben & Logos",
        "stage": "🚀 In Arbeit",
        "lane": "lane_b",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
        "description": (
            "<ul>"
            "<li>[ ] Odoo: Deep Forest (#064e3b) & UV Power (#a855f7) setzen</li>"
            "<li>[ ] Odoo: brand_assets/1.png als Logo hochladen</li>"
            "<li>[ ] Nextcloud: Theming-App via occ konfigurieren</li>"
            "<li>[ ] Home Assistant: Themes.yaml (frawo_hybrid) injizieren</li>"
            "<li>[ ] Paperless/Vaultwarden: UX-Standard angleichen</li>"
            "</ul>"
        ),
    },
    {
        "name": "App-SMTP Baseline: noreply@ SMTP Proof",
        "stage": "⚙️ Planung & Vorbereitung",
        "lane": "lane_c",
        "owners": [WOLF_LOGIN, AGENT_LOGIN],
        "description": (
            "<ul>"
            "<li>[ ] SMTP-Test via test_odoo_smtp.py (Passwort: OD-Wolf-2026!)</li>"
            "<li>[ ] noreply-Identitaet bei Strato final verifizieren</li>"
            "<li>[ ] Sichtbare Testmail in Franz' Postfach bestaetigen</li>"
            "</ul>"
        ),
    },
]


@dataclass
class Change:
    scope: str
    name: str
    details: str


def normalize_label(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stripped = re.sub(r"[^0-9A-Za-zäöüÄÖÜß ]+", " ", stripped)
    return re.sub(r"\s+", " ", stripped).strip().lower()


def contains_label(haystack: str, needle: str) -> bool:
    return normalize_label(needle) in normalize_label(haystack)


def xmlrpc_call(
    session: OdooSession,
    model: str,
    method: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Any:
    merged_kwargs = dict(kwargs or {})
    merged_context = dict(ODOO_CONTEXT)
    if "context" in merged_kwargs:
        merged_context.update(merged_kwargs["context"])
    merged_kwargs["context"] = merged_context
    return session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        model,
        method,
        args or [],
        merged_kwargs,
    )


def print_changes(changes: list[Change], *, title: str) -> None:
    print(title)
    if not changes:
        print("  - keine Aenderungen")
        return
    for change in changes:
        try:
            print(f"  - [{change.scope}] {change.name}: {change.details}")
        except UnicodeEncodeError:
            print(f"  - [{change.scope}] {change.name.encode('ascii', 'ignore').decode()}: {change.details.encode('ascii', 'ignore').decode()}")


def find_by_name(records: list[dict[str, Any]], target: str) -> dict[str, Any] | None:
    for record in records:
        if contains_label(record.get("name", ""), target):
            return record
    return None


def find_exact_or_contains(records: list[dict[str, Any]], target: str) -> dict[str, Any] | None:
    normalized_target = normalize_label(target)
    exact_raw = [record for record in records if (record.get("name") or "") == target]
    if exact_raw:
        return sorted(exact_raw, key=lambda item: item.get("id", 0))[-1]

    exact_normalized = [
        record
        for record in records
        if normalize_label(record.get("name", "")) == normalized_target
    ]
    if exact_normalized:
        return sorted(exact_normalized, key=lambda item: item.get("id", 0))[-1]

    return find_by_name(records, target)


def find_stage_record(
    stages: list[dict[str, Any]],
    target_name: str,
    sequence: int,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    normalized_target = normalize_label(target_name)
    logical_matches = [
        stage
        for stage in stages
        if normalize_label(stage.get("name", "")) == normalized_target
    ]
    same_sequence = [
        stage
        for stage in logical_matches
        if stage.get("sequence") == sequence
    ]
    chosen_pool = same_sequence or logical_matches
    chosen = sorted(chosen_pool, key=lambda item: item.get("id", 0))[-1] if chosen_pool else None
    aliases = [stage for stage in logical_matches if not chosen or stage.get("id") != chosen.get("id")]
    return chosen, aliases


def resolve_xmlid(session: OdooSession, xmlid: str) -> int:
    module, name = xmlid.split(".", 1)
    record = xmlrpc_call(
        session,
        "ir.model.data",
        "search_read",
        [[("module", "=", module), ("name", "=", name)]],
        {"fields": ["res_id"], "limit": 1},
    )
    if not record:
        raise RuntimeError(f"XML-ID nicht gefunden: {xmlid}")
    return int(record[0]["res_id"])


def ensure_agent_user(
    session: OdooSession,
    *,
    apply: bool,
    changes: list[Change],
) -> dict[str, Any]:
    users = xmlrpc_call(
        session,
        "res.users",
        "search_read",
        [[("login", "in", [WOLF_LOGIN, FRANZ_LOGIN, AGENT_LOGIN, ROOTFLO_LOGIN])]],
        {"fields": ["login", "name", "active", "groups_id", "email"], "order": "login asc"},
    )
    user_by_login = {user["login"]: user for user in users}
    group_ids = [resolve_xmlid(session, xmlid) for xmlid in LEAST_PRIVILEGE_GROUP_XMLIDS]

    agent = user_by_login.get(AGENT_LOGIN)
    agent_payload = {
        "name": "🤖 Agent",
        "login": AGENT_LOGIN,
        "email": AGENT_LOGIN,
        "active": True,
        "notification_type": "email",
        "groups_id": [(6, 0, group_ids)],
    }

    if not agent:
        changes.append(Change("users", AGENT_LOGIN, "wird als least-privilege Internal User angelegt"))
        if apply:
            agent_id = xmlrpc_call(session, "res.users", "create", [agent_payload])
            agent = {"id": agent_id, **agent_payload, "groups_id": group_ids}
    else:
        desired_group_set = sorted(group_ids)
        actual_group_set = sorted(agent.get("groups_id", []))
        needs_update = (
            agent.get("name") != agent_payload["name"]
            or agent.get("email") != agent_payload["email"]
            or not agent.get("active", True)
            or actual_group_set != desired_group_set
        )
        if needs_update:
            changes.append(
                Change(
                    "users",
                    AGENT_LOGIN,
                    "wird auf least-privilege Gruppen und kanonischen Anzeigenamen normalisiert",
                )
            )
            if apply:
                xmlrpc_call(session, "res.users", "write", [[agent["id"]], agent_payload])
                agent = {**agent, **agent_payload, "groups_id": group_ids}

    refreshed_users = xmlrpc_call(
        session,
        "res.users",
        "search_read",
        [[("login", "in", [WOLF_LOGIN, FRANZ_LOGIN, AGENT_LOGIN, ROOTFLO_LOGIN])]],
        {"fields": ["login", "name", "active", "groups_id", "email"], "order": "login asc"},
    )
    return {user["login"]: user for user in refreshed_users}


def ensure_project(session: OdooSession, *, apply: bool, changes: list[Change]) -> dict[str, Any]:
    projects = xmlrpc_call(
        session,
        "project.project",
        "search_read",
        [[]],
        {"fields": ["name", "active"], "order": "id asc"},
    )
    project = find_by_name(projects, PROJECT_NAME_NEEDLE)
    if not project:
        changes.append(Change("project", CANONICAL_PROJECT_NAME, "wird neu angelegt"))
        if not apply:
            return {"id": None, "name": CANONICAL_PROJECT_NAME}
        project_id = xmlrpc_call(
            session,
            "project.project",
            "create",
            [[{"name": CANONICAL_PROJECT_NAME, "privacy_visibility": "employees"}]],
        )
        return {"id": project_id, "name": CANONICAL_PROJECT_NAME}

    if project["name"] != CANONICAL_PROJECT_NAME:
        changes.append(Change("project", project["name"], f"wird auf '{CANONICAL_PROJECT_NAME}' umbenannt"))
        if apply:
            xmlrpc_call(
                session,
                "project.project",
                "write",
                [[project["id"]], {"name": CANONICAL_PROJECT_NAME}],
            )
            project["name"] = CANONICAL_PROJECT_NAME
    return project


def ensure_lane_tags(session: OdooSession) -> dict[str, dict[str, Any]]:
    tags = xmlrpc_call(
        session,
        "project.tags",
        "search_read",
        [[]],
        {"fields": ["name"], "order": "id asc"},
    )
    tag_lookup: dict[str, dict[str, Any]] = {}
    for lane_key, tag_name in LANE_TAG_NAMES.items():
        tag = find_by_name(tags, tag_name)
        if not tag:
            print(f"Erstelle fehlendes Lane-Tag: {tag_name}")
            tag_id = xmlrpc_call(
                session,
                "project.tags",
                "create",
                [{"name": tag_name}]
            )
            tag = {"id": tag_id, "name": tag_name}
        tag_lookup[lane_key] = tag
    return tag_lookup


def ensure_stages(
    session: OdooSession,
    project_id: int,
    *,
    apply: bool,
    changes: list[Change],
) -> dict[str, dict[str, Any]]:
    stages = xmlrpc_call(
        session,
        "project.task.type",
        "search_read",
        [[]],
        {"fields": ["name", "sequence", "project_ids", "active"], "order": "sequence asc, id asc"},
    )
    stage_lookup: dict[str, dict[str, Any]] = {}
    alias_stage_ids_to_unlink: list[int] = []

    for spec in STAGE_SPECS:
        existing, aliases = find_stage_record(stages, spec["name"], int(spec["sequence"]))
        if not existing:
            changes.append(Change("stages", spec["name"], "wird global angelegt und mit dem Masterprojekt verknuepft"))
            if not apply:
                stage_lookup[spec["name"]] = {"id": None, "name": spec["name"], "sequence": spec["sequence"], "project_ids": [project_id]}
                continue
            stage_id = xmlrpc_call(
                session,
                "project.task.type",
                "create",
                [[{"name": spec["name"], "sequence": spec["sequence"], "project_ids": [(4, project_id)]}]],
            )
            existing = {"id": stage_id, "name": spec["name"], "sequence": spec["sequence"], "project_ids": [project_id]}
        else:
            updates: dict[str, Any] = {}
            if existing.get("sequence") != spec["sequence"]:
                updates["sequence"] = spec["sequence"]
            if project_id not in existing.get("project_ids", []):
                updates["project_ids"] = [(4, project_id)]
            if updates:
                changes.append(Change("stages", spec["name"], "wird mit Sequenz/Projektverknuepfung normalisiert"))
                if apply:
                    xmlrpc_call(session, "project.task.type", "write", [[existing["id"]], updates])
                    existing = {**existing, **{k: v for k, v in updates.items() if k != "project_ids"}}
                    existing["project_ids"] = sorted(set(existing.get("project_ids", []) + [project_id]))

        for alias in aliases:
            if project_id in alias.get("project_ids", []):
                alias_stage_ids_to_unlink.append(int(alias["id"]))
        stage_lookup[spec["name"]] = existing

    for alias_stage_id in sorted(set(alias_stage_ids_to_unlink)):
        changes.append(Change("stages", str(alias_stage_id), "alias-stage wird aus der Projektverknuepfung entfernt"))
        if apply:
            xmlrpc_call(
                session,
                "project.task.type",
                "write",
                [[alias_stage_id], {"project_ids": [(3, project_id)]}],
            )
    return stage_lookup


def build_task_specs() -> list[dict[str, Any]]:
    specs = list(EXISTING_TASK_RULES)
    specs.append(
        {
            "match": "Nextcloud Stabilization",
            "owners": [WOLF_LOGIN, AGENT_LOGIN],
            "stage": "✅ Erledigt",
            "append_note": (
                "<p><strong>Superseded:</strong> Runtime-Drift technisch behoben; "
                "Weiterarbeit erfolgt im Folge-Task <em>Nextcloud Runtime Hardening / Version Pinning</em>.</p>"
            ),
        }
    )
    return specs


def upsert_new_tasks(
    session: OdooSession,
    project_id: int,
    stage_lookup: dict[str, dict[str, Any]],
    tag_lookup: dict[str, dict[str, Any]],
    user_by_login: dict[str, dict[str, Any]],
    existing_tasks: list[dict[str, Any]],
    *,
    apply: bool,
    changes: list[Change],
) -> None:
    for spec in NEW_TASK_SPECS:
        existing = find_exact_or_contains(existing_tasks, spec["name"])
        owner_ids = [user_by_login[login]["id"] for login in spec["owners"]]
        tag_id = tag_lookup[spec["lane"]]["id"]
        payload = {
            "name": spec["name"],
            "project_id": project_id,
            "stage_id": stage_lookup[spec["stage"]]["id"],
            "user_ids": [(6, 0, owner_ids)],
            "tag_ids": [(6, 0, [tag_id])],
            "description": spec["description"],
        }

        if not existing:
            changes.append(Change("tasks", spec["name"], f"wird neu in '{spec['stage']}' mit {', '.join(spec['owners'])} angelegt"))
            if apply:
                task_id = xmlrpc_call(session, "project.task", "create", [[payload]])
                # Correctly handle stage_id display name for consistency
                stage_record = stage_lookup[spec["stage"]]
                stage_val = [stage_record["id"], stage_record["name"]]
                existing_tasks.append({"id": task_id, **payload, "user_ids": owner_ids, "tag_ids": [tag_id], "stage_id": stage_val})
            continue

        updates: dict[str, Any] = {}
        existing_owner_ids = sorted(existing.get("user_ids", []))
        existing_tag_ids = sorted(existing.get("tag_ids", []))
        if existing.get("stage_id") and existing["stage_id"][0] != payload["stage_id"]:
            updates["stage_id"] = payload["stage_id"]
        if existing_owner_ids != sorted(owner_ids):
            updates["user_ids"] = [(6, 0, owner_ids)]
        if existing_tag_ids != [tag_id]:
            updates["tag_ids"] = [(6, 0, [tag_id])]
        if (existing.get("description") or "").strip() != spec["description"].strip():
            updates["description"] = spec["description"]
        if updates:
            changes.append(Change("tasks", spec["name"], "wird auf kanonischen Stage/Owner/Tag-Stand normalisiert"))
            if apply:
                xmlrpc_call(session, "project.task", "write", [[existing["id"]], updates])


def reconcile_existing_tasks(
    session: OdooSession,
    existing_tasks: list[dict[str, Any]],
    stage_lookup: dict[str, dict[str, Any]],
    user_by_login: dict[str, dict[str, Any]],
    *,
    apply: bool,
    changes: list[Change],
) -> None:
    task_specs = build_task_specs()
    for spec in task_specs:
        task = find_exact_or_contains(existing_tasks, spec["match"])
        if not task:
            changes.append(Change("tasks", spec["match"], "wurde in Odoo nicht gefunden"))
            continue

        desired_owner_ids = [user_by_login[login]["id"] for login in spec["owners"]]
        updates: dict[str, Any] = {}

        if sorted(task.get("user_ids", [])) != sorted(desired_owner_ids):
            updates["user_ids"] = [(6, 0, desired_owner_ids)]

        stage_name = spec.get("stage")
        if stage_name and task.get("stage_id") and stage_lookup[stage_name]["id"] is not None:
            # Check if stage_id is a list/tuple (m2o) or int
            current_stage_id = task["stage_id"][0] if isinstance(task["stage_id"], (list, tuple)) else task["stage_id"]
            if current_stage_id != stage_lookup[stage_name]["id"]:
                updates["stage_id"] = stage_lookup[stage_name]["id"]

        append_note = spec.get("append_note")
        if append_note:
            description = task.get("description") or ""
            if append_note not in description:
                updates["description"] = f"{description}{append_note}".strip()

        if updates:
            changes.append(Change("tasks", task["name"], f"wird auf Owner/Stage-Stand fuer '{spec['match']}' gezogen"))
            if apply:
                xmlrpc_call(session, "project.task", "write", [[task["id"]], updates])


def fetch_project_tasks(session: OdooSession, project_id: int) -> list[dict[str, Any]]:
    return xmlrpc_call(
        session,
        "project.task",
        "search_read",
        [[("project_id", "=", project_id)]],
        {
            "fields": ["name", "stage_id", "user_ids", "tag_ids", "description", "active"],
            "order": "id asc",
        },
    )


def collect_ownerless_open_tasks(tasks: list[dict[str, Any]], stage_lookup: dict[str, dict[str, Any]]) -> list[str]:
    done_stage_id = stage_lookup["✅ Erledigt"]["id"]
    ownerless = []
    for task in tasks:
        stage_id = task.get("stage_id", [None])[0] if task.get("stage_id") else None
        if stage_id == done_stage_id:
            continue
        if not task.get("user_ids"):
            ownerless.append(task["name"])
    return ownerless


def build_spec() -> dict[str, Any]:
    return {
        "project_name": CANONICAL_PROJECT_NAME,
        "stage_specs": STAGE_SPECS,
        "lane_tags": LANE_TAG_NAMES,
        "least_privilege_group_xmlids": LEAST_PRIVILEGE_GROUP_XMLIDS,
        "existing_task_rules": EXISTING_TASK_RULES,
        "new_task_specs": NEW_TASK_SPECS,
    }


def run_reconcile(apply: bool) -> int:
    print("Odoo Masterplan Sync")
    print(f"Modus: {'APPLY' if apply else 'DRY-RUN'}")

    session = connect(default_user=WOLF_LOGIN, prompt_for_username=True)
    print(f"Verbunden: {session.url} | DB: {session.db} | User: {session.username}")

    changes: list[Change] = []
    user_by_login = ensure_agent_user(session, apply=apply, changes=changes)
    project = ensure_project(session, apply=apply, changes=changes)
    if project.get("id") is None:
        print_changes(changes, title="Geplante Aenderungen")
        print("Dry-run endet vor Task-Abgleich, weil das Projekt erst im Apply-Lauf angelegt wuerde.")
        return 0

    tag_lookup = ensure_lane_tags(session)
    stage_lookup = ensure_stages(session, int(project["id"]), apply=apply, changes=changes)
    existing_tasks = fetch_project_tasks(session, int(project["id"]))
    upsert_new_tasks(
        session,
        int(project["id"]),
        stage_lookup,
        tag_lookup,
        user_by_login,
        existing_tasks,
        apply=apply,
        changes=changes,
    )
    existing_tasks = fetch_project_tasks(session, int(project["id"]))
    reconcile_existing_tasks(
        session,
        existing_tasks,
        stage_lookup,
        user_by_login,
        apply=apply,
        changes=changes,
    )
    final_tasks = fetch_project_tasks(session, int(project["id"]))
    ownerless_open = collect_ownerless_open_tasks(final_tasks, stage_lookup)

    print_changes(changes, title="Geplante Aenderungen" if not apply else "Ausgefuehrte Aenderungen")

    if ownerless_open:
        print("Ownerlose offene Tasks:")
        for name in ownerless_open:
            print(f"  - {name}")
        return 1

    print("Keine offenen ownerlosen Tasks mehr im Masterprojekt.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Kanonischer Odoo-Sync fuer das Homeserver-Masterprojekt")
    parser.add_argument("--apply", action="store_true", help="Aenderungen wirklich in Odoo schreiben")
    parser.add_argument("--dry-run", action="store_true", help="Nur geplante Aenderungen ausgeben")
    parser.add_argument("--print-spec", action="store_true", help="Desired-State-Spezifikation als JSON ausgeben")
    args = parser.parse_args(argv)

    if args.print_spec:
        print(json.dumps(build_spec(), indent=2, ensure_ascii=False))
        return 0

    apply = args.apply
    if args.apply and args.dry_run:
        parser.error("--apply und --dry-run sind gegenseitig exklusiv")
    if not args.apply:
        apply = False

    return run_reconcile(apply=apply)


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from typing import Any

from odoo_rpc_client import OdooSession, connect


DEFAULT_PROJECT_ID = 21
PROJECT_NAME_NEEDLE = "Homeserver 2027: Masterplan"
AGENT_LOGIN = "agent@frawo-tech.de"
ELEVATED_GROUP_PATTERNS = [
    "admin",
    "administrator",
    "settings",
    "einstellungen",
    "studio",
    "access rights",
    "zugriffsrechte",
]


def normalize_label(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stripped = re.sub(r"[^0-9A-Za-zäöüÄÖÜß ]+", " ", stripped)
    return re.sub(r"\s+", " ", stripped).strip().lower()


def xmlrpc_call(
    session: OdooSession,
    model: str,
    method: str,
    args: list[Any] | None = None,
    kwargs: dict[str, Any] | None = None,
) -> Any:
    return session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        model,
        method,
        args or [],
        kwargs or {},
    )


def find_project(session: OdooSession, project_id: int) -> dict[str, Any] | None:
    project = xmlrpc_call(
        session,
        "project.project",
        "search_read",
        [[("id", "=", project_id)]],
        {
            "fields": [
                "name",
                "privacy_visibility",
                "alias_name",
                "alias_status",
                "alias_contact",
                "alias_model_id",
                "alias_defaults",
                "alias_force_thread_id",
                "alias_email",
                "alias_full_name",
                "alias_domain_id",
            ],
            "limit": 1,
        },
    )
    if project:
        return project[0]

    projects = xmlrpc_call(
        session,
        "project.project",
        "search_read",
        [[]],
        {
            "fields": [
                "name",
                "privacy_visibility",
                "alias_name",
                "alias_status",
                "alias_contact",
                "alias_model_id",
                "alias_defaults",
                "alias_force_thread_id",
                "alias_email",
                "alias_full_name",
                "alias_domain_id",
            ],
            "order": "id asc",
        },
    )
    for candidate in projects:
        if normalize_label(PROJECT_NAME_NEEDLE) in normalize_label(candidate.get("name", "")):
            return candidate
    return None


def fetch_agent(session: OdooSession) -> dict[str, Any] | None:
    records = xmlrpc_call(
        session,
        "res.users",
        "search_read",
        [[("login", "=", AGENT_LOGIN)]],
        {
            "fields": [
                "name",
                "login",
                "active",
                "share",
                "notification_type",
                "groups_id",
                "totp_enabled",
                "api_key_ids",
            ],
            "limit": 1,
        },
    )
    return records[0] if records else None


def fetch_group_names(session: OdooSession, group_ids: list[int]) -> list[str]:
    if not group_ids:
        return []
    groups = xmlrpc_call(
        session,
        "res.groups",
        "search_read",
        [[("id", "in", group_ids)]],
        {"fields": ["name"], "order": "id asc"},
    )
    return [group.get("name", "") for group in groups]


def fetch_mail_servers(session: OdooSession) -> list[dict[str, Any]]:
    return xmlrpc_call(
        session,
        "ir.mail_server",
        "search_read",
        [[]],
        {"fields": ["name", "smtp_host", "active"], "order": "id asc"},
    )


def fetch_fetchmail_servers(session: OdooSession) -> list[dict[str, Any]]:
    return xmlrpc_call(
        session,
        "fetchmail.server",
        "search_read",
        [[]],
        {"fields": ["name", "server", "port", "is_ssl"], "order": "id asc"},
    )


def fetch_alias_contact_options(session: OdooSession) -> list[dict[str, str]]:
    fields_meta = xmlrpc_call(
        session,
        "project.project",
        "fields_get",
        [["alias_contact"]],
        {"attributes": ["selection"]},
    )
    selection = fields_meta.get("alias_contact", {}).get("selection", [])
    return [{"value": value, "label": label} for value, label in selection]


def fetch_open_agent_tasks(session: OdooSession, project_id: int, agent_user_id: int) -> list[dict[str, Any]]:
    return xmlrpc_call(
        session,
        "project.task",
        "search_read",
        [[("project_id", "=", project_id), ("user_ids", "in", [agent_user_id])]],
        {"fields": ["name", "stage_id"], "order": "id asc"},
    )


def build_report(session: OdooSession, project_id: int) -> dict[str, Any]:
    project = find_project(session, project_id)
    if not project:
        raise RuntimeError(f"Projekt nicht gefunden: {project_id}")

    agent = fetch_agent(session)
    if not agent:
        raise RuntimeError(f"Agent-User nicht gefunden: {AGENT_LOGIN}")

    group_names = fetch_group_names(session, agent.get("groups_id", []))
    mail_servers = fetch_mail_servers(session)
    fetchmail_servers = fetch_fetchmail_servers(session)
    alias_contact_options = fetch_alias_contact_options(session)
    open_agent_tasks = fetch_open_agent_tasks(session, int(project["id"]), int(agent["id"]))

    elevated_groups = [
        name
        for name in group_names
        if any(pattern in normalize_label(name) for pattern in ELEVATED_GROUP_PATTERNS)
    ]

    report = {
        "project": {
            "id": project["id"],
            "name": project.get("name"),
            "privacy_visibility": project.get("privacy_visibility"),
            "alias_name": project.get("alias_name") or None,
            "alias_status": project.get("alias_status"),
            "alias_contact": project.get("alias_contact"),
            "alias_model": project.get("alias_model_id", [None, None])[1] if project.get("alias_model_id") else None,
            "alias_defaults": project.get("alias_defaults"),
            "alias_force_thread_id": project.get("alias_force_thread_id"),
            "alias_email": project.get("alias_email") or None,
            "alias_full_name": project.get("alias_full_name") or None,
            "alias_domain": project.get("alias_domain_id", [None, None])[1] if project.get("alias_domain_id") else None,
        },
        "agent": {
            "id": agent["id"],
            "name": agent.get("name"),
            "login": agent.get("login"),
            "active": bool(agent.get("active")),
            "share": bool(agent.get("share")),
            "notification_type": agent.get("notification_type"),
            "totp_enabled": bool(agent.get("totp_enabled")),
            "api_key_count": len(agent.get("api_key_ids", [])),
            "group_names": group_names,
            "elevated_groups": elevated_groups,
        },
        "mail_servers": {
            "count": len(mail_servers),
            "names": [server.get("name") for server in mail_servers],
        },
        "incoming_mail_transport": {
            "fetchmail_count": len(fetchmail_servers),
            "fetchmail_names": [server.get("name") for server in fetchmail_servers],
        },
        "alias_policy": {
            "current_contact_scope": project.get("alias_contact"),
            "options": alias_contact_options,
            "recommended_scope_for_internal_pilot": "employees",
        },
        "open_agent_tasks": [
            {
                "name": task.get("name"),
                "stage": task.get("stage_id", [None, None])[1] if task.get("stage_id") else None,
            }
            for task in open_agent_tasks
        ],
        "readiness": {
            "project_task_ssot_ready": bool(project.get("name")),
            "agent_least_privilege_like": bool(agent.get("active")) and not bool(agent.get("share")) and not elevated_groups,
            "api_key_present": len(agent.get("api_key_ids", [])) > 0,
            "incoming_alias_live": bool(project.get("alias_name")) or bool(project.get("alias_email")),
            "incoming_alias_prepared_only": not bool(project.get("alias_name")) and bool(project.get("alias_domain_id")),
            "incoming_mail_transport_present": len(fetchmail_servers) > 0,
        },
        "next_actions": [
            "API-Key fuer agent@ bewusst erzeugen und ausserhalb des Repos speichern",
            "Projekt-Alias erst nach Review des alias_contact-Scopes und des Mailpfads aktivieren",
            "Fuer einen internen Pilot zuerst alias_contact=employees oder bewusst enger waehlen",
            "Incoming-Mail-Transport ergaenzen, sonst bleibt agent@ nur alias-seitig vorbereitet",
            "Nach API-Key-Setup erneut pruefen, ob api_key_count > 0 und elevated_groups leer bleiben",
        ],
    }
    return report


def print_human_summary(report: dict[str, Any]) -> None:
    print("Odoo Agent Readiness Audit")
    print(f"Projekt: {report['project']['name']} (ID {report['project']['id']})")
    print(f"Agent aktiv: {report['agent']['active']} | Share: {report['agent']['share']} | API-Keys: {report['agent']['api_key_count']}")
    print(
        "Alias: "
        f"name={report['project']['alias_name'] or '-'} | "
        f"domain={report['project']['alias_domain'] or '-'} | "
        f"status={report['project']['alias_status'] or '-'} | "
        f"contact={report['project']['alias_contact'] or '-'}"
    )
    print(
        f"Incoming-Mail-Transport: fetchmail_count={report['incoming_mail_transport']['fetchmail_count']}"
    )
    print(
        "Alias-Scope-Optionen: "
        + ", ".join(
            f"{option['value']}={option['label']}" for option in report["alias_policy"]["options"]
        )
    )
    if report["agent"]["elevated_groups"]:
        print("Erhoehte Gruppen gefunden:")
        for group in report["agent"]["elevated_groups"]:
            print(f"  - {group}")
    else:
        print("Keine erkennbaren Admin-/Settings-/Studio-Gruppen am agent@-User.")

    print("Offene agent@-Tasks:")
    for task in report["open_agent_tasks"]:
        print(f"  - {task['name']} [{task['stage']}]")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only Audit fuer agent@, Alias- und Mail-Readiness in Odoo")
    parser.add_argument("--project-id", type=int, default=DEFAULT_PROJECT_ID, help="Projekt-ID des Homeserver-Masterprojekts")
    parser.add_argument("--json", action="store_true", help="JSON statt Menschenausgabe schreiben")
    parser.add_argument(
        "--require-api-key",
        action="store_true",
        help="Mit Exit-Code 1 beenden, wenn fuer agent@ noch kein API-Key vorhanden ist",
    )
    args = parser.parse_args(argv)

    session = connect(default_user="wolf@frawo-tech.de", prompt_for_username=True)
    report = build_report(session, args.project_id)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human_summary(report)

    if args.require_api_key and not report["readiness"]["api_key_present"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

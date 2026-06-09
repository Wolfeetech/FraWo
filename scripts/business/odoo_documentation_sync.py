import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.append(os.path.abspath("."))

from scripts.business.odoo_rpc_client import connect

CANONICAL_PROJECT_NAME = "🚀 Homeserver 2027: Masterplan"
DOCUMENTATION_TASK_NAME = "📚 SSOT Contract & Canonical Repo Pointers"
WOLF_LOGIN = "wolf@frawo-tech.de"
AGENT_LOGIN = "agent@frawo-tech.de"
REPO_BLOB_BASE = "https://github.com/Wolfeetech/FraWo/blob/main"
CANONICAL_DOCS = [
    ("LIVE_CONTEXT.md", "Runtime- und Node-Wahrheit"),
    ("NETWORK_PLAN.md", "Netz-, Service- und Abhaengigkeitswahrheit"),
    ("ROADMAP.md", "Prioritaeten, Entscheidungen und Odoo-Bridge"),
    ("MASTERPLAN.md", "Zielarchitektur und Strategie"),
    ("OPERATIONS/ODOO_OPERATIONS.md", "Task-SSOT-Vertrag fuer Odoo"),
    ("STATUS.md", "Auditreport, nicht Governance"),
]


def repo_link(path: str) -> str:
    return f"{REPO_BLOB_BASE}/{path}"


def build_summary_html() -> str:
    links = "".join(
        f"<li><a href='{repo_link(path)}'>{path}</a> — {label}</li>"
        for path, label in CANONICAL_DOCS
    )
    return (
        "<h2>SSOT Contract</h2>"
        "<ul>"
        "<li>Odoo bleibt ausschliesslich Task-SSOT fuer Status, Owner, Prioritaet, Blocker, Review und Abschluss.</li>"
        "<li>Das Repo bleibt technische und betriebliche Wahrheit fuer Runtime, Netzwerk, Infrastruktur und Auditbelege.</li>"
        "<li>Keine Vollspiegel von MASTERPLAN.md, LIVE_CONTEXT.md oder STATUS.md in Odoo-Tasks.</li>"
        "<li>Odoo-Aufgaben enthalten nur eine knappe Summary und Verweise auf die kanonischen Repo-Dateien.</li>"
        "</ul>"
        "<h2>Kanonische Repo-Dateien</h2>"
        f"<ul>{links}</ul>"
        "<h2>Hinweis fuer Agenten</h2>"
        "<p>Claude Code bleibt auf Website-, Odoo-Content- und kuratierte Business-Syncs beschraenkt. "
        "Direkte Infra-Mutationen laufen ueber Handoff an Codex oder den Operator.</p>"
    )


def find_stage_id(session, project_id: int) -> int | bool:
    stage_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.task.type",
        "search",
        [[["project_ids", "in", [project_id]], ["name", "=", "⚙️ Planung & Vorbereitung"]]],
    )
    return stage_ids[0] if stage_ids else False


def resolve_assignees(session) -> list[int]:
    user_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "res.users",
        "search",
        [[["login", "in", [WOLF_LOGIN, AGENT_LOGIN]]]],
    )
    if not user_ids:
        return []
    users = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "res.users",
        "read",
        [user_ids, ["login"]],
    )
    return [user["id"] for user in users if user.get("login") in {WOLF_LOGIN, AGENT_LOGIN}]


def remove_legacy_attachments(session, task_id: int) -> None:
    attachment_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "ir.attachment",
        "search",
        [[["res_model", "=", "project.task"], ["res_id", "=", task_id]]],
    )
    if attachment_ids:
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "ir.attachment",
            "unlink",
            [attachment_ids],
        )


def main():
    print("Starte Odoo SSOT-Summary-Synchronisation...")
    session = connect(default_user=WOLF_LOGIN, prompt_for_username=False)
    print(f"Verbunden mit Odoo ({session.url}) | DB: {session.db}")

    project_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.project",
        "search",
        [[["name", "ilike", "Masterplan"]]],
    )
    if not project_ids:
        raise RuntimeError("Masterplan-Projekt nicht gefunden.")
    project_id = project_ids[0]
    stage_id = find_stage_id(session, project_id)
    assignees = resolve_assignees(session)

    task_ids = session.models.execute_kw(
        session.db,
        session.uid,
        session.secret,
        "project.task",
        "search",
        [[["project_id", "=", project_id], ["name", "=", DOCUMENTATION_TASK_NAME]]],
    )

    task_payload = {
        "name": DOCUMENTATION_TASK_NAME,
        "project_id": project_id,
        "description": build_summary_html(),
        "user_ids": [(6, 0, assignees)],
    }
    if stage_id:
        task_payload["stage_id"] = stage_id

    if task_ids:
        task_id = task_ids[0]
        print(f"Aktualisiere Task {task_id}...")
        session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "write",
            [[task_id], task_payload],
        )
    else:
        print("Erstelle Summary-Task...")
        task_id = session.models.execute_kw(
            session.db,
            session.uid,
            session.secret,
            "project.task",
            "create",
            [task_payload],
        )

    remove_legacy_attachments(session, task_id)
    print("Odoo SSOT-Summary erfolgreich aktualisiert.")

if __name__ == "__main__":
    main()

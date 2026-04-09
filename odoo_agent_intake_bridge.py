from __future__ import annotations

import argparse
import email
import html
import imaplib
import os
import re
import ssl
from dataclasses import dataclass
from email.header import decode_header
from email.message import Message
from email.utils import getaddresses, parsedate_to_datetime
from typing import Any

from odoo_rpc_client import OdooSession, connect


DEFAULT_PROJECT_ID = 21
DEFAULT_FOLDER = "Aliases.Agent"
DEFAULT_PROCESSED_FOLDER = "Aliases.Agent.Processed"
DEFAULT_PROJECT_NAME_NEEDLE = "Homeserver 2027: Masterplan"
DEFAULT_STAGE_NAME = "Backlog"
DEFAULT_STAGE_FALLBACKS = [
    "📝 Backlog",
    "Backlog",
]

ODOO_CONTEXT = {
    "tracking_disable": True,
    "mail_create_nosubscribe": True,
    "mail_auto_subscribe_no_notify": True,
    "mail_notify_force_send": False,
    "default_notify": False,
}


@dataclass
class IntakeMessage:
    uid: bytes
    subject: str
    from_display: str
    recipients: list[str]
    message_id: str | None
    date_display: str
    body_excerpt: str


def decode_header_value(value: str) -> str:
    parts: list[str] = []
    for chunk, encoding in decode_header(value or ""):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts).strip()


def normalize_spaces(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


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


def fetch_raw_message(mailbox: imaplib.IMAP4_SSL, uid: bytes) -> Message:
    status, data = mailbox.uid("fetch", uid, "(RFC822)")
    if status != "OK" or not data or not data[0]:
        raise RuntimeError(f"RFC822-Fetch fehlgeschlagen fuer UID {uid.decode()}")
    return email.message_from_bytes(data[0][1])


def ensure_folder(mailbox: imaplib.IMAP4_SSL, folder: str) -> None:
    status, _ = mailbox.create(folder)
    if status not in {"OK", "NO"}:
        raise RuntimeError(f"Ordner konnte nicht erstellt werden: {folder}")


def move_message(mailbox: imaplib.IMAP4_SSL, uid: bytes, target_folder: str) -> None:
    status, _ = mailbox.uid("MOVE", uid, target_folder)
    if status == "OK":
        return

    status, _ = mailbox.uid("COPY", uid, target_folder)
    if status != "OK":
        raise RuntimeError(f"Copy fehlgeschlagen fuer UID {uid.decode()} -> {target_folder}")
    status, _ = mailbox.uid("STORE", uid, "+FLAGS.SILENT", r"(\Deleted)")
    if status != "OK":
        raise RuntimeError(f"Delete-Flag fehlgeschlagen fuer UID {uid.decode()}")
    status, _ = mailbox.expunge()
    if status != "OK":
        raise RuntimeError(f"Expunge fehlgeschlagen fuer UID {uid.decode()}")


def extract_plain_text_from_part(part: Message) -> str:
    payload = part.get_payload(decode=True)
    if payload is None:
        return ""
    charset = part.get_content_charset() or "utf-8"
    return payload.decode(charset, errors="replace")


def strip_html_tags(value: str) -> str:
    without_breaks = re.sub(r"(?i)<\s*br\s*/?\s*>", "\n", value)
    without_blocks = re.sub(r"(?i)</\s*(p|div|li|tr|h[1-6])\s*>", "\n", without_breaks)
    without_tags = re.sub(r"<[^>]+>", " ", without_blocks)
    return html.unescape(without_tags)


def extract_body_excerpt(msg: Message, *, max_chars: int) -> str:
    plain_candidates: list[str] = []
    html_candidates: list[str] = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = (part.get_content_type() or "").lower()
            disposition = (part.get("Content-Disposition") or "").lower()
            if "attachment" in disposition:
                continue
            if content_type == "text/plain":
                plain_candidates.append(extract_plain_text_from_part(part))
            elif content_type == "text/html":
                html_candidates.append(strip_html_tags(extract_plain_text_from_part(part)))
    else:
        content_type = (msg.get_content_type() or "").lower()
        body = extract_plain_text_from_part(msg)
        if content_type == "text/html":
            html_candidates.append(strip_html_tags(body))
        else:
            plain_candidates.append(body)

    text = "\n".join(candidate for candidate in plain_candidates if candidate.strip()).strip()
    if not text:
        text = "\n".join(candidate for candidate in html_candidates if candidate.strip()).strip()

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = normalize_spaces(text.replace("\r", "\n"))
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
    return text


def extract_recipients(msg: Message) -> list[str]:
    values = []
    for header in ("to", "cc", "delivered-to", "x-original-to", "resent-to"):
        values.extend(msg.get_all(header, []))
    recipients = [addr.lower() for _, addr in getaddresses(values) if addr]
    return sorted(set(recipients))


def format_date(value: str | None) -> str:
    if not value:
        return "-"
    try:
        return parsedate_to_datetime(value).isoformat()
    except (TypeError, ValueError, IndexError):
        return normalize_spaces(value)


def load_messages(
    mailbox: imaplib.IMAP4_SSL,
    folder: str,
    *,
    unseen_only: bool,
    limit: int | None,
    body_chars: int,
) -> list[IntakeMessage]:
    status, _ = mailbox.select(folder)
    if status != "OK":
        raise RuntimeError(f"Ordner konnte nicht geoeffnet werden: {folder}")

    criteria = ["UNSEEN"] if unseen_only else ["ALL"]
    status, data = mailbox.uid("search", None, *criteria)
    if status != "OK":
        raise RuntimeError(f"Suche fehlgeschlagen in {folder}")

    uids = [uid for uid in data[0].split() if uid]
    if limit is not None:
        uids = uids[-limit:]

    messages: list[IntakeMessage] = []
    for uid in uids:
        raw = fetch_raw_message(mailbox, uid)
        subject = decode_header_value(raw.get("Subject", "")) or "(ohne Betreff)"
        senders = getaddresses(raw.get_all("from", []))
        from_display = normalize_spaces(
            ", ".join(
                f"{decode_header_value(name)} <{addr}>".strip()
                if name and addr
                else (addr or decode_header_value(name))
                for name, addr in senders
                if name or addr
            )
        ) or "-"
        messages.append(
            IntakeMessage(
                uid=uid,
                subject=subject,
                from_display=from_display,
                recipients=extract_recipients(raw),
                message_id=normalize_spaces(raw.get("Message-ID", "")) or None,
                date_display=format_date(raw.get("Date")),
                body_excerpt=extract_body_excerpt(raw, max_chars=body_chars),
            )
        )
    return messages


def resolve_project(session: OdooSession, project_id: int, project_name_needle: str) -> dict[str, Any]:
    records = xmlrpc_call(
        session,
        "project.project",
        "search_read",
        [[("id", "=", project_id)]],
        {"fields": ["name"], "limit": 1},
    )
    if records:
        return records[0]

    records = xmlrpc_call(
        session,
        "project.project",
        "search_read",
        [[]],
        {"fields": ["name"], "order": "id asc"},
    )
    for record in records:
        if project_name_needle.lower() in (record.get("name") or "").lower():
            return record
    raise RuntimeError(f"Projekt nicht gefunden: {project_id} / {project_name_needle}")


def resolve_stage_id(session: OdooSession, project_id: int, stage_name: str) -> int | None:
    stages = xmlrpc_call(
        session,
        "project.task.type",
        "search_read",
        [[("project_ids", "in", [project_id])]],
        {"fields": ["name", "sequence"], "order": "sequence asc, id asc"},
    )
    normalized_requested = stage_name.strip().lower()
    candidates = [stage_name, *DEFAULT_STAGE_FALLBACKS]
    for candidate in candidates:
        normalized_candidate = candidate.strip().lower()
        for stage in stages:
            if (stage.get("name") or "").strip().lower() == normalized_candidate:
                return int(stage["id"])
        if normalized_candidate == normalized_requested:
            continue
    return None


def resolve_user_ids(session: OdooSession, logins: list[str]) -> list[int]:
    if not logins:
        return []
    users = xmlrpc_call(
        session,
        "res.users",
        "search_read",
        [[("login", "in", logins)]],
        {"fields": ["login"], "order": "id asc"},
    )
    found_by_login = {user["login"]: int(user["id"]) for user in users}
    missing = [login for login in logins if login not in found_by_login]
    if missing:
        raise RuntimeError(f"Owner-Logins nicht gefunden: {', '.join(missing)}")
    return [found_by_login[login] for login in logins]


def resolve_tag_id(session: OdooSession, tag_name: str | None) -> int | None:
    if not tag_name:
        return None
    tags = xmlrpc_call(
        session,
        "project.tags",
        "search_read",
        [[("name", "=", tag_name)]],
        {"fields": ["name"], "limit": 1},
    )
    if not tags:
        raise RuntimeError(f"Tag nicht gefunden: {tag_name}")
    return int(tags[0]["id"])


def find_existing_task_id(session: OdooSession, project_id: int, message_id: str) -> int | None:
    marker = f"HS27-Agent-Message-ID: {message_id}"
    records = xmlrpc_call(
        session,
        "project.task",
        "search_read",
        [[("project_id", "=", project_id), ("description", "ilike", marker)]],
        {"fields": ["name"], "limit": 1},
    )
    if not records:
        return None
    return int(records[0]["id"])


def build_task_description(message: IntakeMessage) -> str:
    rows = [
        "<p><strong>Agent Intake</strong></p>",
        "<ul>",
        f"<li><strong>From:</strong> {html.escape(message.from_display)}</li>",
        f"<li><strong>To:</strong> {html.escape(', '.join(message.recipients) or '-')}</li>",
        f"<li><strong>Date:</strong> {html.escape(message.date_display)}</li>",
    ]
    if message.message_id:
        rows.append(f"<li><strong>Message-ID:</strong> {html.escape(message.message_id)}</li>")
    rows.extend(
        [
            "</ul>",
            f"<p><strong>Inhalt:</strong> {html.escape(message.body_excerpt or '(kein lesbarer Textausschnitt)')}</p>",
        ]
    )
    if message.message_id:
        rows.append(f"<p><code>HS27-Agent-Message-ID: {html.escape(message.message_id)}</code></p>")
    return "".join(rows)


def create_task(
    session: OdooSession,
    *,
    project_id: int,
    stage_id: int | None,
    owner_ids: list[int],
    tag_id: int | None,
    message: IntakeMessage,
) -> int:
    payload: dict[str, Any] = {
        "name": f"[agent@] {message.subject}",
        "project_id": project_id,
        "description": build_task_description(message),
    }
    if stage_id is not None:
        payload["stage_id"] = stage_id
    if owner_ids:
        payload["user_ids"] = [(6, 0, owner_ids)]
    if tag_id is not None:
        payload["tag_ids"] = [(6, 0, [tag_id])]
    return int(xmlrpc_call(session, "project.task", "create", [[payload]]))


def print_summary(
    *,
    project_name: str,
    folder: str,
    processed_folder: str,
    apply: bool,
    messages: list[IntakeMessage],
    skipped_duplicates: list[tuple[IntakeMessage, int]],
) -> None:
    print(
        f"folder={folder} checked={len(messages)} apply={'yes' if apply else 'no'} "
        f"processed_folder={processed_folder} project={project_name}"
    )
    for message in messages:
        print(
            f"uid={message.uid.decode()} subject={message.subject!r} "
            f"from={message.from_display!r} message_id={message.message_id or '-'}"
        )
    for message, task_id in skipped_duplicates:
        print(
            f"duplicate=yes uid={message.uid.decode()} subject={message.subject!r} existing_task_id={task_id}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Liest den dedizierten agent@-IMAP-Ordner und legt daraus Odoo-Tasks an."
    )
    parser.add_argument("--imap-host", default=os.getenv("HS27_IMAP_HOST", "imap.strato.de"))
    parser.add_argument("--imap-port", type=int, default=int(os.getenv("HS27_IMAP_PORT", "993")))
    parser.add_argument("--imap-user", default=os.getenv("HS27_IMAP_USER"))
    parser.add_argument("--imap-password", default=os.getenv("HS27_IMAP_PASSWORD"))
    parser.add_argument("--folder", default=os.getenv("HS27_AGENT_INTAKE_FOLDER", DEFAULT_FOLDER))
    parser.add_argument(
        "--processed-folder",
        default=os.getenv("HS27_AGENT_INTAKE_PROCESSED_FOLDER", DEFAULT_PROCESSED_FOLDER),
    )
    parser.add_argument("--project-id", type=int, default=DEFAULT_PROJECT_ID)
    parser.add_argument("--project-name-needle", default=DEFAULT_PROJECT_NAME_NEEDLE)
    parser.add_argument("--stage", default=DEFAULT_STAGE_NAME)
    parser.add_argument(
        "--owner",
        action="append",
        default=[],
        metavar="LOGIN",
        help="Odoo-Owner-Login; mehrfach nutzbar. Standard: wolf@ + agent@",
    )
    parser.add_argument("--tag", default=None, help="Optionaler Lane-Tag-Name")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--body-chars", type=int, default=700)
    parser.add_argument("--unseen-only", action="store_true")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    if not args.imap_user or not args.imap_password:
        raise SystemExit("IMAP-Zugang fehlt. Nutze HS27_IMAP_USER und HS27_IMAP_PASSWORD.")

    owner_logins = args.owner or ["wolf@frawo-tech.de", "agent@frawo-tech.de"]
    context = ssl.create_default_context()
    with imaplib.IMAP4_SSL(args.imap_host, args.imap_port, ssl_context=context) as mailbox:
        mailbox.login(args.imap_user, args.imap_password)
        messages = load_messages(
            mailbox,
            args.folder,
            unseen_only=args.unseen_only,
            limit=args.limit,
            body_chars=args.body_chars,
        )

        session = connect(default_user="wolf@frawo-tech.de", prompt_for_username=True)
        project = resolve_project(session, args.project_id, args.project_name_needle)
        stage_id = resolve_stage_id(session, int(project["id"]), args.stage)
        owner_ids = resolve_user_ids(session, owner_logins)
        tag_id = resolve_tag_id(session, args.tag)

        skipped_duplicates: list[tuple[IntakeMessage, int]] = []
        actionable: list[IntakeMessage] = []
        for message in messages:
            if message.message_id:
                existing_task_id = find_existing_task_id(session, int(project["id"]), message.message_id)
                if existing_task_id is not None:
                    skipped_duplicates.append((message, existing_task_id))
                    continue
            actionable.append(message)

        print_summary(
            project_name=project["name"],
            folder=args.folder,
            processed_folder=args.processed_folder,
            apply=args.apply,
            messages=actionable,
            skipped_duplicates=skipped_duplicates,
        )

        if args.apply:
            ensure_folder(mailbox, args.processed_folder)
            for message in actionable:
                create_task(
                    session,
                    project_id=int(project["id"]),
                    stage_id=stage_id,
                    owner_ids=owner_ids,
                    tag_id=tag_id,
                    message=message,
                )
                move_message(mailbox, message.uid, args.processed_folder)
            print(f"created={len(actionable)} moved={len(actionable)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

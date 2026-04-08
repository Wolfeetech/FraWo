from __future__ import annotations

import argparse
import email
import imaplib
import os
import ssl
from dataclasses import dataclass
from email.header import decode_header
from email.utils import getaddresses
from typing import Iterable


DEFAULT_ALIAS_MAP = {
    "agent@frawo-tech.de": "Aliases.Agent",
    "info@frawo-tech.de": "Aliases.Info",
}


@dataclass
class MessageDecision:
    uid: bytes
    subject: str
    recipients: list[str]
    target_folder: str | None


def decode_header_value(value: str) -> str:
    parts: list[str] = []
    for chunk, encoding in decode_header(value or ""):
        if isinstance(chunk, bytes):
            parts.append(chunk.decode(encoding or "utf-8", errors="replace"))
        else:
            parts.append(chunk)
    return "".join(parts)


def parse_alias_map(raw_values: Iterable[str]) -> dict[str, str]:
    alias_map = dict(DEFAULT_ALIAS_MAP)
    for raw in raw_values:
        if "=" not in raw:
            raise ValueError(f"Ungueltiges Mapping: {raw!r}")
        alias, folder = raw.split("=", 1)
        alias_map[alias.strip().lower()] = folder.strip()
    return alias_map


def extract_recipients(msg: email.message.Message) -> list[str]:
    values = []
    for header in ("to", "cc", "delivered-to", "x-original-to", "resent-to"):
        values.extend(msg.get_all(header, []))
    recipients = [addr.lower() for _, addr in getaddresses(values) if addr]
    return sorted(set(recipients))


def fetch_message_headers(mailbox: imaplib.IMAP4_SSL, uid: bytes) -> email.message.Message:
    status, data = mailbox.uid(
        "fetch",
        uid,
        "(BODY.PEEK[HEADER.FIELDS (TO CC DELIVERED-TO X-ORIGINAL-TO RESENT-TO SUBJECT)])",
    )
    if status != "OK" or not data or not data[0]:
        raise RuntimeError(f"Header-Fetch fehlgeschlagen fuer UID {uid.decode()}")
    header_bytes = data[0][1]
    return email.message_from_bytes(header_bytes)


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


def decide_messages(
    mailbox: imaplib.IMAP4_SSL,
    alias_map: dict[str, str],
    *,
    unseen_only: bool,
    limit: int | None,
) -> list[MessageDecision]:
    status, _ = mailbox.select("INBOX")
    if status != "OK":
        raise RuntimeError("INBOX konnte nicht geoeffnet werden")

    criteria = ["UNSEEN"] if unseen_only else ["ALL"]
    status, data = mailbox.uid("search", None, *criteria)
    if status != "OK":
        raise RuntimeError("Inbox-Suche fehlgeschlagen")

    uids = [uid for uid in data[0].split() if uid]
    if limit is not None:
        uids = uids[-limit:]

    decisions: list[MessageDecision] = []
    for uid in uids:
        msg = fetch_message_headers(mailbox, uid)
        recipients = extract_recipients(msg)
        subject = decode_header_value(msg.get("subject", ""))
        target_folder = None
        for alias, folder in alias_map.items():
            if alias in recipients:
                target_folder = folder
                break
        decisions.append(
            MessageDecision(
                uid=uid,
                subject=subject,
                recipients=recipients,
                target_folder=target_folder,
            )
        )
    return decisions


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verschiebt Alias-Mails aus einer Shared-INBOX in getrennte IMAP-Ordner."
    )
    parser.add_argument("--imap-host", default=os.getenv("HS27_IMAP_HOST", "imap.strato.de"))
    parser.add_argument("--imap-port", type=int, default=int(os.getenv("HS27_IMAP_PORT", "993")))
    parser.add_argument("--imap-user", default=os.getenv("HS27_IMAP_USER"))
    parser.add_argument("--imap-password", default=os.getenv("HS27_IMAP_PASSWORD"))
    parser.add_argument("--unseen-only", action="store_true", help="Nur ungelesene Mails pruefen")
    parser.add_argument("--limit", type=int, default=None, help="Nur die letzten N Inbox-Mails pruefen")
    parser.add_argument("--apply", action="store_true", help="Verschiebungen wirklich ausfuehren")
    parser.add_argument(
        "--map",
        action="append",
        default=[],
        metavar="ALIAS=ORDNER",
        help="Zusatz- oder Override-Mapping, z. B. agent@frawo-tech.de=INBOX/Aliases/Agent",
    )
    args = parser.parse_args()

    if not args.imap_user or not args.imap_password:
        raise SystemExit("IMAP-Zugang fehlt. Nutze HS27_IMAP_USER und HS27_IMAP_PASSWORD.")

    alias_map = parse_alias_map(args.map)

    context = ssl.create_default_context()
    with imaplib.IMAP4_SSL(args.imap_host, args.imap_port, ssl_context=context) as mailbox:
        mailbox.login(args.imap_user, args.imap_password)
        decisions = decide_messages(
            mailbox,
            alias_map,
            unseen_only=args.unseen_only,
            limit=args.limit,
        )

        matched = [decision for decision in decisions if decision.target_folder]
        print(f"checked={len(decisions)} matched={len(matched)} apply={'yes' if args.apply else 'no'}")
        for decision in matched:
            print(
                f"uid={decision.uid.decode()} folder={decision.target_folder} "
                f"subject={decision.subject!r} recipients={','.join(decision.recipients)}"
            )

        if args.apply:
            for folder in sorted({decision.target_folder for decision in matched if decision.target_folder}):
                ensure_folder(mailbox, folder)
            for decision in matched:
                move_message(mailbox, decision.uid, decision.target_folder or "INBOX")
            print("moved=yes")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

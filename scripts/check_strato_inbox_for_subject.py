#!/usr/bin/env python3
"""Read-only IMAP proof that a STRATO mailbox received a message with a given subject."""

from __future__ import annotations

import argparse
import imaplib
import os
import socket
import sys
from email import message_from_bytes
from email.header import decode_header, make_header


def env_or_error(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"missing_env={name}")
    return value


def decode_mime_header(raw: str | None) -> str:
    if not raw:
        return ""
    try:
        return str(make_header(decode_header(raw)))
    except Exception:
        return raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--mailbox", default="INBOX")
    parser.add_argument("--imap-host", default="imap.strato.de")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    password = env_or_error("HS27_MAILBOX_PASSWORD")
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(args.timeout)

    try:
        client = imaplib.IMAP4_SSL(args.imap_host, args.imap_port)
        try:
            client.login(args.username, password)
            status, _ = client.select(args.mailbox, readonly=True)
            if status != "OK":
                print(f"mailbox_username={args.username}")
                print(f"mailbox_name={args.mailbox}")
                print("inbox_proof=no")
                print("error=select_failed")
                return 1

            status, data = client.search(None, "SUBJECT", f'"{args.subject}"')
            if status != "OK":
                print(f"mailbox_username={args.username}")
                print(f"mailbox_name={args.mailbox}")
                print(f"search_subject={args.subject}")
                print("inbox_proof=no")
                print("error=search_failed")
                return 1

            ids = [item for item in (data[0] or b"").split() if item]
            print(f"mailbox_username={args.username}")
            print(f"mailbox_name={args.mailbox}")
            print(f"search_subject={args.subject}")
            print(f"matching_messages={len(ids)}")

            if not ids:
                print("inbox_proof=no")
                print("recommendation=verify_mail_arrival_in_target_mailbox_or_repeat_send_test")
                return 1

            latest_id = ids[-1]
            status, fetched = client.fetch(latest_id, "(BODY.PEEK[HEADER.FIELDS (DATE FROM SUBJECT)])")
            if status != "OK" or not fetched or not isinstance(fetched[0], tuple):
                print("inbox_proof=no")
                print("error=fetch_failed")
                return 1

            header_bytes = fetched[0][1]
            msg = message_from_bytes(header_bytes)
            latest_date = decode_mime_header(msg.get("Date"))
            latest_from = decode_mime_header(msg.get("From"))
            latest_subject = decode_mime_header(msg.get("Subject"))

            print(f"latest_from={latest_from}")
            print(f"latest_subject={latest_subject}")
            print(f"latest_date={latest_date}")
            print("inbox_proof=yes")
            print("recommendation=update_release_gate_manual_evidence_if_subject_matches_expected_test_mail")
            return 0
        finally:
            try:
                client.logout()
            except Exception:
                pass
    except Exception as exc:
        print(f"mailbox_username={args.username}")
        print(f"mailbox_name={args.mailbox}")
        print(f"search_subject={args.subject}")
        print("inbox_proof=no")
        print(f"error={exc}")
        return 1
    finally:
        socket.setdefaulttimeout(previous_timeout)


if __name__ == "__main__":
    sys.exit(main())

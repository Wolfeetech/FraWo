#!/usr/bin/env python3
"""Non-destructive STRATO mailbox auth check for IMAP and SMTP."""

from __future__ import annotations

import argparse
import imaplib
import os
import smtplib
import socket
import sys


def env_or_error(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise SystemExit(f"missing_env={name}")
    return value


def test_imap(host: str, port: int, username: str, password: str, timeout: float) -> tuple[bool, str]:
    previous_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(timeout)
    try:
        client = imaplib.IMAP4_SSL(host, port)
        try:
            client.login(username, password)
            return True, "ok"
        finally:
            try:
                client.logout()
            except Exception:
                pass
    except Exception as exc:  # pragma: no cover - runtime probe
        return False, str(exc)
    finally:
        socket.setdefaulttimeout(previous_timeout)


def test_smtp_starttls(host: str, port: int, username: str, password: str, timeout: float) -> tuple[bool, str]:
    try:
        client = smtplib.SMTP(host, port, timeout=timeout)
        try:
            client.ehlo()
            client.starttls()
            client.ehlo()
            client.login(username, password)
            return True, "ok"
        finally:
            try:
                client.quit()
            except Exception:
                pass
    except Exception as exc:  # pragma: no cover - runtime probe
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--username", required=True)
    parser.add_argument("--imap-host", default="imap.strato.de")
    parser.add_argument("--imap-port", type=int, default=993)
    parser.add_argument("--smtp-host", default="smtp.strato.de")
    parser.add_argument("--smtp-port", type=int, default=587)
    parser.add_argument("--timeout", type=float, default=10.0)
    args = parser.parse_args()

    password = env_or_error("HS27_MAILBOX_PASSWORD")

    imap_ok, imap_detail = test_imap(args.imap_host, args.imap_port, args.username, password, args.timeout)
    smtp_ok, smtp_detail = test_smtp_starttls(args.smtp_host, args.smtp_port, args.username, password, args.timeout)

    print(f"mailbox_username={args.username}")
    print(f"imap_auth_ok={'yes' if imap_ok else 'no'}")
    print(f"smtp_auth_ok={'yes' if smtp_ok else 'no'}")

    if imap_ok and smtp_ok:
        print("mailbox_ready=yes")
        print("recommendation=store_verified_mailbox_in_vaultwarden_and_client_setup")
        return 0

    if not imap_ok:
        print(f"imap_error={imap_detail}")
    if not smtp_ok:
        print(f"smtp_error={smtp_detail}")
    print("mailbox_ready=no")
    print("recommendation=verify_real_mailbox_password_or_provider_side_mailbox_state")
    return 1


if __name__ == "__main__":
    sys.exit(main())

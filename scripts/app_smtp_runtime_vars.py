#!/usr/bin/env python3
"""Resolve effective SMTP runtime variables without committing live secrets."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import yaml


ROOT_DIR = Path(__file__).resolve().parents[1]
MAIN_VARS_PATH = ROOT_DIR / "ansible" / "inventory" / "group_vars" / "all" / "main.yml"
LOCAL_RUNTIME_VARS_PATH = ROOT_DIR / "ansible" / "inventory" / "group_vars" / "all" / "mail_runtime.local.yml"

MAIL_RUNTIME_KEYS = [
    "homeserver_mail_provider",
    "homeserver_mail_imap_host",
    "homeserver_mail_pop3_host",
    "homeserver_mail_smtp_host",
    "homeserver_mail_smtp_port",
    "homeserver_mail_smtp_secure",
    "homeserver_mail_sender_name",
    "homeserver_mail_sender_email",
    "homeserver_mail_smtp_auth_username",
    "homeserver_mail_app_smtp_enabled",
    "homeserver_vault_mail_smtp_password",
]

ENV_VAR_MAP = {
    "homeserver_mail_smtp_auth_username": "HOMESERVER_MAIL_SMTP_AUTH_USERNAME",
    "homeserver_mail_app_smtp_enabled": "HOMESERVER_MAIL_APP_SMTP_ENABLED",
    "homeserver_vault_mail_smtp_password": "HOMESERVER_MAIL_SMTP_PASSWORD",
}


def load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    return data


def parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value!r}")


def effective_vars() -> dict:
    resolved = load_yaml(MAIN_VARS_PATH)
    resolved.update(load_yaml(LOCAL_RUNTIME_VARS_PATH))

    for key, env_var in ENV_VAR_MAP.items():
        raw = os.getenv(env_var)
        if raw is None or raw == "":
            continue
        if key == "homeserver_mail_app_smtp_enabled":
            resolved[key] = parse_bool(raw)
        else:
            resolved[key] = raw

    return resolved


def missing_ready_fields(resolved: dict) -> list[str]:
    missing: list[str] = []
    if not bool(resolved.get("homeserver_mail_app_smtp_enabled")):
        missing.append("homeserver_mail_app_smtp_enabled must be true")
    if not str(resolved.get("homeserver_mail_smtp_host", "")).strip():
        missing.append("homeserver_mail_smtp_host is missing")
    if not str(resolved.get("homeserver_mail_smtp_port", "")).strip():
        missing.append("homeserver_mail_smtp_port is missing")
    if not str(resolved.get("homeserver_mail_sender_email", "")).strip():
        missing.append("homeserver_mail_sender_email is missing")
    if not str(resolved.get("homeserver_mail_smtp_auth_username", "")).strip():
        missing.append("homeserver_mail_smtp_auth_username is missing")
    if not str(resolved.get("homeserver_vault_mail_smtp_password", "")).strip():
        missing.append("homeserver_vault_mail_smtp_password is missing")
    return missing


def stringify(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--get", metavar="KEY", help="Print one effective SMTP runtime variable.")
    parser.add_argument(
        "--write-extra-vars",
        metavar="PATH",
        help="Write effective SMTP runtime variables to a YAML file for ansible-playbook --extra-vars.",
    )
    parser.add_argument(
        "--validate-ready",
        action="store_true",
        help="Exit non-zero when required SMTP runtime variables are incomplete.",
    )
    args = parser.parse_args()

    try:
        resolved = effective_vars()
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if args.validate_ready:
        missing = missing_ready_fields(resolved)
        if missing:
            for item in missing:
                print(item, file=sys.stderr)
            return 1

    if args.write_extra_vars:
        extra_vars = {
            key: resolved[key]
            for key in MAIL_RUNTIME_KEYS
            if key in resolved and stringify(resolved[key]) != ""
        }
        output_path = Path(args.write_extra_vars)
        with output_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(extra_vars, handle, sort_keys=True)

    if args.get:
        print(stringify(resolved.get(args.get, "")))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

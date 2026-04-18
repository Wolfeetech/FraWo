from __future__ import annotations

import getpass
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class OdooConnectionSettings:
    url: str
    db: str
    user: str
    secret: str


def resolve_named_secret(*env_names: str, prompt_label: str) -> str:
    for env_name in env_names:
        value = os.getenv(env_name)
        if value:
            return value

    if sys.stdin is not None and sys.stdin.isatty():
        return getpass.getpass(f"{prompt_label}: ")

    raise RuntimeError(
        f"Setze {' oder '.join(env_names)}, bevor du dieses Skript startest."
    )


def resolve_secret(prompt_label: str = "Odoo Passwort oder API-Key") -> str:
    return resolve_named_secret(
        "ODOO_RPC_API_KEY",
        "ODOO_RPC_PASSWORD",
        prompt_label=prompt_label,
    )


def resolve_db_password(prompt_label: str = "Odoo DB Passwort") -> str:
    return resolve_named_secret(
        "ODOO_DB_PASSWORD",
        prompt_label=prompt_label,
    )


def resolve_connection(
    default_url: str,
    default_db: str,
    default_user: str,
) -> OdooConnectionSettings:
    return OdooConnectionSettings(
        url=os.getenv("ODOO_RPC_URL", default_url),
        db=os.getenv("ODOO_RPC_DB", default_db),
        user=os.getenv("ODOO_RPC_USER", default_user),
        secret=resolve_secret(),
    )

#!/usr/bin/env python3
"""
update_odoo_base_url.py
FraWo GbR – Setzt web.base.url in Odoo auf die öffentliche Domain.
Wird lokal vom StudioPC via RPC ausgeführt (kein SSH nötig).
"""
import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
import odoo_rpc_client


def main() -> int:
    target_url = os.getenv("ODOO_BASE_URL", "https://www.frawo-tech.de")

    print(f"=== Odoo web.base.url Updater ===")
    print(f"Ziel-URL: {target_url}")

    session = odoo_rpc_client.connect(default_user="admin")

    # Aktuelle web.base.url lesen
    ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        "ir.config_parameter", "search",
        [[["key", "=", "web.base.url"]]]
    )

    if ids:
        current = session.models.execute_kw(
            session.db, session.uid, session.secret,
            "ir.config_parameter", "read",
            [ids, ["key", "value"]]
        )
        print(f"Aktuell: {current[0]['value']}")
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            "ir.config_parameter", "write",
            [ids, {"value": target_url}]
        )
    else:
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            "ir.config_parameter", "create",
            [{"key": "web.base.url", "value": target_url}]
        )

    print(f"  ✓ web.base.url → {target_url}")

    # Auch website.domain setzen falls website-Modul aktiv
    website_ids = session.models.execute_kw(
        session.db, session.uid, session.secret,
        "website", "search", [[]]
    )
    if website_ids:
        session.models.execute_kw(
            session.db, session.uid, session.secret,
            "website", "write",
            [website_ids, {"domain": "https://www.frawo-tech.de"}]
        )
        print(f"  ✓ website.domain → https://www.frawo-tech.de")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\nFehler: {e}", file=sys.stderr)
        sys.exit(1)

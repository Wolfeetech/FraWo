#!/usr/bin/env python3
"""Stellt Odoo-Datensätze aus einem Sicherungsordner von ci_color_consolidate.py wieder her.

Benutzung:
  python3 scripts/ci_color_restore.py backups/ci-konsolidierung-20261007-194705 [--apply]

Ohne --apply wird nur aufgelistet, was zurückgeschrieben würde.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ci_color_consolidate import _api  # noqa: E402

NAME_RE = re.compile(r"^(?P<model>[a-z][a-z._]*[a-z])-(?P<id>\d+)-(?P<field>[a-z_]+)-.*\.bak-")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("backup_dir", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    files = sorted(p for p in args.backup_dir.iterdir() if p.is_file() and ".bak-" in p.name)
    if not files:
        sys.exit(f"Keine Sicherungsdateien in {args.backup_dir}")

    done = 0
    for path in files:
        match = NAME_RE.match(path.name)
        if not match:
            print(f"  ? übersprungen (Name unklar): {path.name}")
            continue
        model, rec_id, field = match["model"], int(match["id"]), match["field"]
        content = path.read_text(encoding="utf-8")
        if args.apply:
            _api(model, "write", {"ids": [rec_id], "vals": {field: content}})
            done += 1
            print(f"  ✓ {model} {rec_id}.{field} zurückgeschrieben ({len(content)} Zeichen)")
        else:
            print(f"  würde {model} {rec_id}.{field} zurückschreiben ({len(content)} Zeichen)")

    print(f"\n{done if args.apply else 0} Datensätze wiederhergestellt von {len(files)} Sicherungen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

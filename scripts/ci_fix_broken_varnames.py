#!/usr/bin/env python3
"""Reparatur: CSS-Variablennamen, die eine frühere Blind-Ersetzung zerschossen hat.

Was passiert war: Eine frühere Farbumstellung hat das Wort „cyan" überall ersetzt —
auch INNERHALB von Variablennamen. Daraus wurde z. B. `--fw-cyan` → `--fw-<hexwert>`.
Ein `#` ist in einem CSS-Variablennamen ungültig, und die zugehörige Definition hieß
weiterhin `--fw-accent`. Folge: `var(--fw-#...)` zeigte ins Leere, die Regeln waren
still tot — u. a. die Fokus-Rahmen für Tastaturbedienung (Barrierefreiheit).

Dieses Skript benennt die kaputten Namen gezielt um (keine Blind-Ersetzung) und
setzt die Werte auf die freigegebene CI v3.0 (SSOT/FRAWO_CI_GUIDELINES.md).

Benutzung:
  python3 scripts/ci_fix_broken_varnames.py --dry-run
  python3 scripts/ci_fix_broken_varnames.py --apply
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ci_color_consolidate import BACKUP_ROOT, REPO, _api  # noqa: E402

# Exakte Umbenennungen und Wertkorrekturen je Fundort.
# Reihenfolge wichtig: längere Namen zuerst, sonst frisst die kurze Regel das Präfix.
ODOO_RULES: dict[int, list[tuple[str, str]]] = {
    # website.user_custom_css — Akzent heißt bereits --fw-accent, die Verwendungen
    # zeigten aber auf den zerschossenen Namen.
    1988: [
        ("--fw-#9D4EDD-light", "--fw-accent-light"),
        ("--fw-#9D4EDD-dark", "--fw-accent-dark"),
        ("--fw-#9D4EDD", "--fw-accent"),
        ("--fw-accent: #9D4EDD", "--fw-accent: #a050f0"),      # CI-Akzent
        ("--fw-accent-dark: #0891b2", "--fw-accent-dark: #9d4edd"),  # Cyan-Rest -> CI-Hover
    ],
    # Radioseite
    3353: [
        ("--ff-accent-#A050F0", "--ff-accent-hover"),
        ("--ff-accent-#9D4EDD", "--ff-accent"),
    ],
    # DJ-Kiosk: tote Definition mit einem Violett, das in keiner CI steht.
    3447: [
        ("--ff-#A050F0: #7000FF", "--ff-accent: #a050f0"),
    ],
}

REPO_RULES: dict[str, list[tuple[str, str]]] = {
    "addons/frawo_agent/views/radio_page.xml": ODOO_RULES[3353],
}

BROKEN_NAME = re.compile(r"--[a-zA-Z0-9-]*-?#[0-9A-Fa-f]{6}")


def apply_rules(text: str, rules: list[tuple[str, str]]) -> tuple[str, int]:
    count = 0
    for old, new in rules:
        n = text.count(old)
        if n:
            text = text.replace(old, new)
            count += n
    return text, count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_ROOT / f"varnamen-reparatur-{stamp}"
    if args.apply:
        backup_dir.mkdir(parents=True, exist_ok=True)

    total = 0

    for rel, rules in REPO_RULES.items():
        path = REPO / rel
        old = path.read_text(encoding="utf-8")
        new, n = apply_rules(old, rules)
        rest = BROKEN_NAME.findall(new)
        print(f"repo {rel}: {n} Korrekturen, {len(rest)} kaputte Namen übrig")
        total += n
        if args.apply and n:
            (backup_dir / f"repo-{rel.replace('/', '_')}.bak-{stamp}").write_text(old, encoding="utf-8")
            path.write_text(new, encoding="utf-8")

    for view_id, rules in ODOO_RULES.items():
        rec = _api("ir.ui.view", "search_read", {
            "domain": [["id", "=", view_id]], "fields": ["id", "key", "name", "arch_db"], "limit": 1,
        })[0]
        old = rec.get("arch_db") or ""
        new, n = apply_rules(old, rules)
        rest = BROKEN_NAME.findall(new)
        label = rec.get("key") or rec.get("name")
        print(f"odoo {view_id} {label}: {n} Korrekturen, {len(rest)} kaputte Namen übrig")
        total += n
        if args.apply and n:
            (backup_dir / f"ir.ui.view-{view_id}-arch_db.bak-{stamp}").write_text(old, encoding="utf-8")
            _api("ir.ui.view", "write", {"ids": [view_id], "vals": {"arch_db": new}})

    if args.apply:
        print(f"\n{total} Korrekturen angewandt. Sicherungen: {backup_dir}")
    else:
        print(f"\n{total} Korrekturen würden angewandt (Trockenlauf).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

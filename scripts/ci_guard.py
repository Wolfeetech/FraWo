#!/usr/bin/env python3
"""CI-Wächter: findet Farb-Abweichungen, bevor daraus wieder ein Provisorium wird.

Warum es das gibt: Im Oktober 2026 standen drei Farbwelten gleichzeitig im System,
weil jede Welle eine neue Doku und neue Hex-Werte mitbrachte, ohne die alte
abzuräumen. Vorsätze haben das nicht verhindert — eine Dauerprüfung tut es.

Geprüft wird gegen die EINZIGE Farbquelle SSOT/ci_tokens.json:
  1. Live-Odoo: alle ir.ui.view sowie website.custom_code_head/footer
  2. Repo: Web-Quelldateien (ohne die in ci_tokens.json genannten Ausnahmen)

Benutzung:
  python3 scripts/ci_guard.py              # beides prüfen
  python3 scripts/ci_guard.py --repo-only  # ohne Odoo-Zugang (z. B. vor dem Commit)
  python3 scripts/ci_guard.py --json       # Maschinenausgabe für Cron/Meldungen

Rückgabewert: 0 = sauber, 1 = Abweichungen gefunden. Damit taugt es für Cron
und für eine Prüfung vor dem Commit.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ci_color_consolidate import (  # noqa: E402
    DECISION_PATHS,
    REPO,
    TOKENS,
    VIEW_FIELD,
    WEBSITE_FIELDS,
    _api,
)

DEPRECATED = {
    old.lower(): entry
    for old, entry in TOKENS["abgeloest"].items()
    if not old.startswith("_")
}
EXCLUDED_PATHS = tuple(TOKENS["pruefung_ausnahmen"]["pfade"])
SOURCE_SUFFIXES = {".xml", ".html", ".css", ".scss", ".js", ".py", ".svg", ".md", ".json"}
_RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", re.I)


def _rgb_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def find_deprecated(text: str) -> dict[str, int]:
    """Zählt abgelöste Farben in Hex- und rgb()-Schreibweise."""
    if not text:
        return {}
    found: dict[str, int] = {}
    for match in re.findall(r"#[0-9A-Fa-f]{6}", text):
        key = match.lower()
        if key in DEPRECATED:
            found[key] = found.get(key, 0) + 1
    for r, g, b in _RGB_RE.findall(text):
        key = _rgb_hex(int(r), int(g), int(b))
        if key in DEPRECATED:
            found[key] = found.get(key, 0) + 1
    return found


def scan_repo() -> list[dict]:
    results = []
    for path in sorted(REPO.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(REPO).as_posix()
        if rel.startswith(".git/") or "/node_modules/" in f"/{rel}":
            continue
        if any(rel == ex or rel.startswith(ex) for ex in EXCLUDED_PATHS):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        found = find_deprecated(text)
        if found:
            # Marken-/Archiv-Pfade gelten nie als automatisch behebbar — dort würde
            # eine Teilumfärbung ein neues Provisorium erzeugen.
            entscheidung = any(rel == ex or rel.startswith(ex) for ex in DECISION_PATHS)
            results.append({
                "ort": "repo",
                "name": rel,
                "treffer": sum(found.values()),
                "farben": found,
                "behebbar": (not entscheidung) and all(DEPRECATED[c].get("auto") for c in found),
            })
    return results


def scan_odoo() -> list[dict]:
    results = []
    ids = [v["id"] for v in _api("ir.ui.view", "search_read", {
        "domain": [[VIEW_FIELD, "!=", False]], "fields": ["id"], "limit": 10000,
    })]
    for start in range(0, len(ids), 300):
        for rec in _api("ir.ui.view", "search_read", {
            "domain": [["id", "in", ids[start:start + 300]]],
            "fields": ["id", "name", "key", VIEW_FIELD], "limit": 300,
        }):
            found = find_deprecated(rec.get(VIEW_FIELD) or "")
            if found:
                results.append({
                    "ort": "odoo:ir.ui.view",
                    "name": f"{rec['id']} {rec.get('key') or rec.get('name') or ''}",
                    "treffer": sum(found.values()),
                    "farben": found,
                    "behebbar": all(DEPRECATED[c].get("auto") for c in found),
                })
    for rec in _api("website", "search_read", {
        "domain": [], "fields": ["id", "name", *WEBSITE_FIELDS], "limit": 50,
    }):
        for field in WEBSITE_FIELDS:
            found = find_deprecated(rec.get(field) or "")
            if found:
                results.append({
                    "ort": "odoo:website",
                    "name": f"{rec['id']} {rec.get('name')}·{field}",
                    "treffer": sum(found.values()),
                    "farben": found,
                    "behebbar": all(DEPRECATED[c].get("auto") for c in found),
                })
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-only", action="store_true", help="nur Repo prüfen, kein Odoo-Zugang nötig")
    parser.add_argument("--json", action="store_true", help="Maschinenausgabe")
    args = parser.parse_args()

    findings = scan_repo()
    if not args.repo_only:
        findings += scan_odoo()
    findings.sort(key=lambda f: -f["treffer"])
    total = sum(f["treffer"] for f in findings)
    auto = sum(f["treffer"] for f in findings if f["behebbar"])

    if args.json:
        print(json.dumps({
            "treffer_gesamt": total,
            "davon_automatisch_behebbar": auto,
            "datensaetze": findings,
        }, ensure_ascii=False, indent=2))
        return 1 if total else 0

    if not total:
        print("✅ CI sauber — keine abgelösten Farben in Repo und Live-Odoo.")
        return 0

    print(f"⚠️  {total} abgelöste Farbangaben in {len(findings)} Datensätzen "
          f"({auto} davon automatisch behebbar mit ci_color_consolidate.py --apply)\n")
    for f in findings[:40]:
        flag = " " if f["behebbar"] else "!"
        colors = ", ".join(f"{c}×{n}" for c, n in sorted(f["farben"].items(), key=lambda kv: -kv[1]))
        print(f" {flag} {f['treffer']:4d}  {f['ort']:18s} {f['name'][:46]:46s} {colors}")
    if len(findings) > 40:
        print(f"    … und {len(findings) - 40} weitere")
    print("\n  ! = enthält Farben, die laut ci_tokens.json nur mit Wolfs Entscheidung "
          "geändert werden dürfen (Logo-/Druck-Ebene).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

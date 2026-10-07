#!/usr/bin/env python3
"""CI-Farbkonsolidierung für frawo.tech und alle Odoo-Ansichten.

Hintergrund: Im System standen drei Farbwelten gleichzeitig — die von Wolf am
12.07.2026 freigegebene CI v3.0 (SSOT/FRAWO_CI_GUIDELINES.md, Akzent #a050f0),
eine Cyan-Zwischenphase vom 01.09.2026 (Aufgabe #1229) und eine zweite
CI-Doku vom September (Aufgabe #1252, Akzent #a855f7). Entscheidung von Wolf
(07.10.2026): es gilt die freigegebene CI, alles andere wird zurückgebaut.

Die Farbkarte steht NICHT in diesem Skript, sondern in SSOT/ci_tokens.json —
damit es nur eine Stelle gibt, an der Farben definiert werden.

Benutzung:
  python3 scripts/ci_color_consolidate.py --check    # nur zählen, nichts ändern
  python3 scripts/ci_color_consolidate.py --dry-run   # zeigen, was passieren würde
  python3 scripts/ci_color_consolidate.py --apply     # live ändern (legt Backups an)

Standardmäßig werden Live-Odoo UND Repo-Dateien erfasst. Mit --nur-odoo bzw.
--nur-repo lässt sich das eingrenzen.

Zugang: Umgebungsvariable ODOO_API_KEY (Vaultwarden 'frawo-secret'), kein
Passwort im Repo. Backups landen unter backups/ci-konsolidierung-<stamp>/.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from typing import Any

ODOO_BASE = os.environ.get("ODOO_JSON_BASE", "http://10.1.0.112:8069/json/2/")
ODOO_DB = os.environ.get("ODOO_DB_NAME", "FraWo_GbR")

REPO = Path(__file__).resolve().parents[1]
BACKUP_ROOT = REPO / "backups"
TOKENS_FILE = REPO / "SSOT" / "ci_tokens.json"


def _load_tokens() -> dict:
    return json.loads(TOKENS_FILE.read_text(encoding="utf-8"))


TOKENS = _load_tokens()

# Alt -> Neu, nur die als 'auto' freigegebenen Ersetzungen.
# Begründung je Farbe steht in SSOT/ci_tokens.json.
COLOR_MAP = {
    old.lower(): entry["neu"].lower()
    for old, entry in TOKENS["abgeloest"].items()
    if not old.startswith("_") and entry.get("auto")
}


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


# rgb()/rgba()-Schreibweisen derselben Altfarben, sonst bleiben Schatten cyan.
RGB_MAP = {_hex_to_rgb(old): _hex_to_rgb(new) for old, new in COLOR_MAP.items()}

VIEW_FIELD = "arch_db"
WEBSITE_FIELDS = ("custom_code_head", "custom_code_footer")

# Repo-Dateitypen, in denen Farben vorkommen. Ausnahmen stehen in ci_tokens.json.
SOURCE_SUFFIXES = {".xml", ".html", ".css", ".scss", ".js", ".py", ".svg", ".md"}
EXCLUDED_PATHS = tuple(TOKENS["pruefung_ausnahmen"]["pfade"])
# Marken-/Archiv-Ebene: nicht automatisch anfassen (halbe Umfärbung wäre ein Provisorium).
DECISION_PATHS = tuple(TOKENS["nur_mit_entscheidung_pfade"]["pfade"])


def _api(model: str, method: str, payload: dict) -> Any:
    key = os.environ.get("ODOO_API_KEY")
    if not key:
        sys.exit("ODOO_API_KEY fehlt — Schlüssel aus Vaultwarden 'frawo-secret' exportieren.")
    req = urllib.request.Request(
        f"{ODOO_BASE}{model}/{method}",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": "bearer " + key,
            "X-Odoo-Database": ODOO_DB,
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


_RGB_RE = re.compile(r"rgba?\(\s*(\d{1,3})\s*,\s*(\d{1,3})\s*,\s*(\d{1,3})", re.I)


def convert(text: str) -> tuple[str, int]:
    """Ersetzt Altfarben CI-konform. Gibt (neuer_text, anzahl_ersetzungen) zurück."""
    if not text:
        return text, 0
    count = 0

    def hex_sub(match: re.Match) -> str:
        nonlocal count
        found = match.group(0)
        new = COLOR_MAP.get(found.lower())
        if not new:
            return found
        count += 1
        # Großschreibung der Quelle beibehalten (#00BFFF -> #A855F7).
        return new.upper() if found[1:].isupper() else new

    text = re.sub(r"#[0-9A-Fa-f]{6}", hex_sub, text)

    def rgb_sub(match: re.Match) -> str:
        nonlocal count
        triple = (int(match.group(1)), int(match.group(2)), int(match.group(3)))
        new = RGB_MAP.get(triple)
        if not new:
            return match.group(0)
        count += 1
        head = match.group(0).split("(")[0]
        return f"{head}({new[0]}, {new[1]}, {new[2]}"

    text = _RGB_RE.sub(rgb_sub, text)
    return text, count


def collect_repo() -> list[dict]:
    """Repo-Quelldateien mit abgelösten Farben sammeln."""
    jobs: list[dict] = []
    for path in sorted(REPO.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        rel = path.relative_to(REPO).as_posix()
        if rel.startswith(".git/") or "/node_modules/" in f"/{rel}":
            continue
        if any(rel == ex or rel.startswith(ex) for ex in EXCLUDED_PATHS):
            continue
        if any(rel == ex or rel.startswith(ex) for ex in DECISION_PATHS):
            continue
        try:
            old = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        new, n = convert(old)
        if n:
            jobs.append({
                "model": "repo",
                "id": 0,
                "label": rel,
                "field": "datei",
                "old": old,
                "new": new,
                "count": n,
                "path": path,
            })
    return jobs


def collect_odoo() -> list[dict]:
    """Betroffene Odoo-Datensätze mit ihrem neuen Inhalt sammeln."""
    jobs: list[dict] = []

    views = _api("ir.ui.view", "search_read", {
        "domain": [[VIEW_FIELD, "!=", False]],
        "fields": ["id"],
        "limit": 10000,
    })
    ids = [v["id"] for v in views]
    for start in range(0, len(ids), 300):
        chunk = _api("ir.ui.view", "search_read", {
            "domain": [["id", "in", ids[start:start + 300]]],
            "fields": ["id", "name", "key", VIEW_FIELD],
            "limit": 300,
        })
        for rec in chunk:
            old = rec.get(VIEW_FIELD) or ""
            new, n = convert(old)
            if n:
                jobs.append({
                    "model": "ir.ui.view",
                    "id": rec["id"],
                    "label": rec.get("key") or rec.get("name") or "",
                    "field": VIEW_FIELD,
                    "old": old,
                    "new": new,
                    "count": n,
                })

    sites = _api("website", "search_read", {
        "domain": [],
        "fields": ["id", "name", *WEBSITE_FIELDS],
        "limit": 50,
    })
    for rec in sites:
        for field in WEBSITE_FIELDS:
            old = rec.get(field) or ""
            new, n = convert(old)
            if n:
                jobs.append({
                    "model": "website",
                    "id": rec["id"],
                    "label": f"{rec.get('name')}·{field}",
                    "field": field,
                    "old": old,
                    "new": new,
                    "count": n,
                })
    return jobs


def collect(odoo: bool = True, repo: bool = True) -> list[dict]:
    jobs: list[dict] = []
    if repo:
        jobs += collect_repo()
    if odoo:
        jobs += collect_odoo()
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="nur zählen")
    mode.add_argument("--dry-run", action="store_true", help="zeigen, was passieren würde")
    mode.add_argument("--apply", action="store_true", help="live ändern")
    parser.add_argument("--nur-odoo", action="store_true", help="nur Live-Odoo")
    parser.add_argument("--nur-repo", action="store_true", help="nur Repo-Dateien")
    args = parser.parse_args()

    scope = {"odoo": not args.nur_repo, "repo": not args.nur_odoo}
    jobs = collect(**scope)
    total = sum(j["count"] for j in jobs)

    if args.check:
        print(f"{total} Treffer in {len(jobs)} Datensätzen")
        for job in sorted(jobs, key=lambda j: -j["count"]):
            print(f"  {job['model']:12s} {job['id']:5d} {job['label'][:50]:50s} {job['count']:4d}")
        return 1 if total else 0

    if not jobs:
        print("Nichts zu tun — bereits CI-konform.")
        return 0

    if args.dry_run:
        print(f"Würde {total} Farbangaben in {len(jobs)} Datensätzen ersetzen:")
        for job in sorted(jobs, key=lambda j: -j["count"]):
            print(f"  {job['model']:12s} {job['id']:5d} {job['label'][:50]:50s} {job['count']:4d}")
        return 0

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = BACKUP_ROOT / f"ci-konsolidierung-{stamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    changed = 0
    for job in jobs:
        if job["model"] == "repo":
            safe = re.sub(r"[^A-Za-z0-9._-]", "_", job["label"])[:80]
            (backup_dir / f"repo-{safe}.bak-{stamp}").write_text(job["old"], encoding="utf-8")
            job["path"].write_text(job["new"], encoding="utf-8")
            changed += job["count"]
            print(f"  ✓ repo {job['label'][:60]} ({job['count']})")
            continue
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", job["label"])[:60]
        name = f"{job['model']}-{job['id']}-{job['field']}-{safe}.bak-{stamp}"
        (backup_dir / name).write_text(job["old"], encoding="utf-8")
        # Odoo /json/2 erwartet den Schlüssel 'vals' (nicht 'values') — sonst HTTP 422.
        _api(job["model"], "write", {"ids": [job["id"]], "vals": {job["field"]: job["new"]}})
        changed += job["count"]
        print(f"  ✓ {job['model']} {job['id']} {job['label'][:50]} ({job['count']})")

    print(f"\n{changed} Farbangaben CI-konform ersetzt. Backups: {backup_dir}")

    rest = sum(j["count"] for j in collect(**scope))
    print(f"Nachprüfung: {rest} Treffer übrig")
    return 0 if rest == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())

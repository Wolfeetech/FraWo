#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from fnmatch import fnmatch


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def iter_markdown_files(root: Path) -> list[str]:
    paths = []
    for file_path in root.rglob("*.md"):
        if any(part == ".git" for part in file_path.parts):
            continue
        rel = file_path.relative_to(root).as_posix()
        paths.append(rel)
    return sorted(paths)


def resolve_owner(path: str, manifest: dict) -> tuple[str | None, list[str]]:
    matches: list[str] = []

    for owner, payload in manifest.get("explicit_paths", {}).items():
        if path in payload:
            matches.append(owner)

    for rule in manifest.get("glob_rules", []):
        pattern = rule["pattern"]
        if fnmatch(path, pattern):
            matches.append(rule["owner"])

    unique_matches = sorted(set(matches))
    if len(unique_matches) == 1:
        return unique_matches[0], unique_matches
    return None, unique_matches


def build_report(root: Path, manifest_path: Path) -> dict:
    manifest = load_manifest(manifest_path)
    owners = set(manifest.get("owners", {}).keys())
    files = iter_markdown_files(root)

    duplicates: dict[str, list[str]] = {}
    covered: dict[str, list[str]] = {owner: [] for owner in owners}
    missing: list[str] = []
    ambiguous: dict[str, list[str]] = {}

    explicit_seen: dict[str, list[str]] = {}
    for owner, payload in manifest.get("explicit_paths", {}).items():
        for path in payload:
            explicit_seen.setdefault(path, []).append(owner)
    for path, path_owners in explicit_seen.items():
        if len(path_owners) > 1:
            duplicates[path] = sorted(path_owners)

    for path in files:
        owner, matches = resolve_owner(path, manifest)
        if owner is None:
            if matches:
                ambiguous[path] = matches
            else:
                missing.append(path)
            continue
        covered[owner].append(path)

    manifest_only = []
    for owner, payload in manifest.get("explicit_paths", {}).items():
        for path in payload:
            if path not in files:
                manifest_only.append({"path": path, "owner": owner})

    return {
        "owners": manifest.get("owners", {}),
        "counts": {owner: len(paths) for owner, paths in covered.items()},
        "covered": covered,
        "missing": missing,
        "ambiguous": ambiguous,
        "duplicates": duplicates,
        "manifest_only": manifest_only,
        "all_green": not missing and not ambiguous and not duplicates and not manifest_only,
        "scanned_file_count": len(files),
    }


def write_markdown_report(report: dict, output_path: Path) -> None:
    lines = [
        "# Document Ownership Report",
        "",
        f"Scanned markdown files: `{report['scanned_file_count']}`",
        f"All green: `{str(report['all_green']).lower()}`",
        "",
        "## Counts",
        "",
    ]

    for owner, count in sorted(report["counts"].items()):
        lines.append(f"- `{owner}`: `{count}`")

    lines.extend(["", "## Missing Ownership", ""])
    if report["missing"]:
        for path in report["missing"]:
            lines.append(f"- `{path}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Ambiguous Ownership", ""])
    if report["ambiguous"]:
        for path, owners in sorted(report["ambiguous"].items()):
            lines.append(f"- `{path}`: `{', '.join(owners)}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Duplicate Explicit Entries", ""])
    if report["duplicates"]:
        for path, owners in sorted(report["duplicates"].items()):
            lines.append(f"- `{path}`: `{', '.join(owners)}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Manifest Entries Without File", ""])
    if report["manifest_only"]:
        for item in report["manifest_only"]:
            lines.append(f"- `{item['path']}` owned by `{item['owner']}`")
    else:
        lines.append("- none")

    lines.extend(["", "## Paths By Owner", ""])
    for owner, paths in sorted(report["covered"].items()):
        lines.append(f"### {owner}")
        lines.append("")
        for path in paths:
            lines.append(f"- `{path}`")
        if not paths:
            lines.append("- none")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="manifests/document_ownership/document_ownership.json")
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    manifest_path = root / args.manifest
    report = build_report(root, manifest_path)

    print(f"document_count={report['scanned_file_count']}")
    for owner, count in sorted(report["counts"].items()):
        print(f"owner_{owner}_count={count}")
    print(f"missing_count={len(report['missing'])}")
    print(f"ambiguous_count={len(report['ambiguous'])}")
    print(f"duplicate_count={len(report['duplicates'])}")
    print(f"manifest_only_count={len(report['manifest_only'])}")
    print(f"ownership_check_status={'green' if report['all_green'] else 'red'}")

    if args.report:
        output_path = root / args.report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        write_markdown_report(report, output_path)
        print(f"report_path={output_path}")

    return 0 if report["all_green"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

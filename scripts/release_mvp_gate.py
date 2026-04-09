#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
MANUAL_CHECKS_FILE = ROOT_DIR / "manifests" / "release_mvp_gate" / "manual_checks.json"
AUDIT_ROOT = ROOT_DIR / "artifacts" / "release_mvp_audit"
OUTPUT_ROOT = ROOT_DIR / "artifacts" / "release_mvp_gate"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
LATEST_JSON_PATH = OUTPUT_ROOT / "latest_release_mvp_gate.json"
LATEST_MD_PATH = OUTPUT_ROOT / "latest_release_mvp_gate.md"
LATEST_POINTER_PATH = OUTPUT_ROOT / "latest.txt"

CRITICAL_CODEX_CHECKS = [
    "document-ownership-check",
    "inventory-check",
    "ansible-ping",
    "qga-check",
    "business-drift-check",
    "toolbox-network-check",
    "toolbox-portal-status-check",
    "vaultwarden-smtp-check",
    "proxmox-local-backup-check",
    "security-baseline-check",
    "core-app-smtp-check",
]


def find_latest_summary() -> Path:
    candidates = sorted(
        path / "summary.tsv"
        for path in AUDIT_ROOT.iterdir()
        if path.is_dir() and path.name[:8].isdigit()
    )
    if not candidates:
        raise FileNotFoundError("release_mvp_summary_not_found")
    return candidates[-1]


def run_document_ownership_check(log_path: Path) -> str:
    completed = subprocess.run(
        [sys.executable, "./scripts/document_ownership_check.py"],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")
    return "passed" if completed.returncode == 0 else "failed"


def main() -> int:
    summary_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_latest_summary()
    if not summary_path.is_file():
        print("release_mvp_gate_error=summary_not_found", file=sys.stderr)
        return 1
    if not MANUAL_CHECKS_FILE.is_file():
        print("release_mvp_gate_error=manual_checks_file_not_found", file=sys.stderr)
        return 1

    report_dir = OUTPUT_ROOT / TIMESTAMP
    report_dir.mkdir(parents=True, exist_ok=True)
    json_report_path = report_dir / "release_mvp_gate.json"
    md_report_path = report_dir / "release_mvp_gate.md"
    ownership_log = report_dir / "document-ownership-check.log"
    ownership_status = run_document_ownership_check(ownership_log)

    summary_rows = list(csv.DictReader(summary_path.open("r", encoding="utf-8"), delimiter="\t"))
    summary_by_id = {row["id"]: row for row in summary_rows}
    summary_by_id["document-ownership-check"] = {
        "id": "document-ownership-check",
        "status": ownership_status,
        "log": str(ownership_log),
        "executor": "codex",
        "command_or_action": f"{sys.executable} ./scripts/document_ownership_check.py",
    }

    manual_data = json.loads(MANUAL_CHECKS_FILE.read_text(encoding="utf-8"))
    manual_checks = manual_data.get("checks", [])

    blocked_reasons: list[str] = []
    codex_results: list[dict[str, object]] = []
    for check_id in CRITICAL_CODEX_CHECKS:
        row = summary_by_id.get(check_id)
        if row is None:
            codex_results.append(
                {
                    "id": check_id,
                    "status": "missing",
                    "critical": True,
                    "log": "",
                    "executor": "codex",
                    "command_or_action": "",
                }
            )
            blocked_reasons.append(f"missing critical MVP Codex check: {check_id}")
            continue

        codex_results.append(
            {
                "id": check_id,
                "status": row["status"],
                "critical": True,
                "log": row["log"],
                "executor": "codex",
                "command_or_action": row["command_or_action"],
            }
        )
        if row["status"] != "passed":
            blocked_reasons.append(f"critical MVP Codex check not green: {check_id}={row['status']}")

    manual_results: list[dict[str, object]] = []
    for check in manual_checks:
        entry = {
            "id": check["id"],
            "title": check["title"],
            "executor": check["executor"],
            "critical": bool(check.get("critical", False)),
            "status": check.get("status", "pending"),
            "last_verified": check.get("last_verified", ""),
            "evidence": check.get("evidence", ""),
        }
        manual_results.append(entry)
        if entry["critical"] and entry["status"] != "passed":
            blocked_reasons.append(f"critical MVP manual evidence not green: {entry['id']}={entry['status']}")

    decision = "MVP_READY" if not blocked_reasons else "BLOCKED"
    report = {
        "decision": decision,
        "summary_source": str(summary_path),
        "manual_checks_source": str(MANUAL_CHECKS_FILE),
        "critical_codex_checks": codex_results,
        "manual_checks": manual_results,
        "blocked_reasons": blocked_reasons,
        "scope_note": (
            "This gate covers the current business MVP only. "
            "It is separate from the public website release track and from the full internal production certification."
        ),
    }
    json_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    LATEST_JSON_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Release MVP Gate",
        "",
        f"Decision: `{decision}`",
        "",
        f"MVP audit summary: `{summary_path}`",
        f"Manual evidence: `{MANUAL_CHECKS_FILE}`",
        "",
        "## Scope Note",
        "",
        "This gate covers the current business MVP only.",
        "It is not the same as the public website track or the full internal production seal.",
        "",
        "## Critical MVP Codex Checks",
        "",
    ]
    for row in codex_results:
        lines.append(f"- `{row['id']}`: `{row['status']}`")

    lines.extend(["", "## Critical MVP Manual Evidence", ""])
    for row in manual_results:
        detail = row["title"]
        if row["last_verified"]:
            detail += f"; last_verified={row['last_verified']}"
        if row["evidence"]:
            detail += f"; evidence={row['evidence']}"
        lines.append(f"- `{row['id']}`: `{row['status']}` - {detail}")

    lines.extend(["", "## Blocked Reasons", ""])
    if blocked_reasons:
        for reason in blocked_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- none")
    markdown_text = "\n".join(lines)
    md_report_path.write_text(markdown_text, encoding="utf-8")
    LATEST_MD_PATH.write_text(markdown_text, encoding="utf-8")
    LATEST_POINTER_PATH.write_text(
        "\n".join(
            [
                f"latest_report_dir={report_dir}",
                f"latest_json={json_report_path}",
                f"latest_markdown={md_report_path}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"decision={decision}")
    print(f"json_report={json_report_path}")
    print(f"markdown_report={md_report_path}")
    print(f"release_mvp_gate_report_dir={report_dir}")
    if blocked_reasons:
        print(f"blocked_reason_count={len(blocked_reasons)}")
    return 0 if decision == "MVP_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())

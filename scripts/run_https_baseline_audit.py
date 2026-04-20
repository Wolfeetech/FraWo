#!/usr/bin/env python3
from __future__ import annotations

import csv
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT_DIR / "artifacts" / "https_baseline_audit" / datetime.now().strftime("%Y%m%d_%H%M%S")
SUMMARY_TSV = REPORT_DIR / "summary.tsv"
REPORT_MD = REPORT_DIR / "report.md"


CODEX_CHECKS: list[tuple[str, list[str]]] = [
    ("public-dns-check", [sys.executable, "./scripts/public_dns_check.py"]),
    ("public-http-redirect-check", [sys.executable, "./scripts/public_http_redirect_check.py"]),
    ("public-https-check", [sys.executable, "./scripts/public_https_check.py"]),
]

MANUAL_TASKS: list[tuple[str, str, str]] = [
    (
        "public_browser_acceptance_https",
        "operator",
        "Open http://frawo-tech.de, https://frawo-tech.de, http://www.frawo-tech.de and https://www.frawo-tech.de and confirm the public behavior matches the HTTPS-baseline goal.",
    ),
    (
        "public_scope_guardrail",
        "operator",
        "Confirm no admin UI is exposed publicly while the HTTPS baseline is being activated.",
    ),
]


def run_check(check_id: str, command: list[str]) -> dict[str, str]:
    log_path = REPORT_DIR / f"{check_id}.log"
    completed = subprocess.run(
        command,
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    log_path.write_text((completed.stdout or "") + (completed.stderr or ""), encoding="utf-8")
    return {
        "id": check_id,
        "executor": "codex",
        "status": "passed" if completed.returncode == 0 else "failed",
        "command_or_action": " ".join(command),
        "log": str(log_path),
    }


def build_report(rows: list[dict[str, str]]) -> None:
    by_executor: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_executor[row["executor"]].append(row)

    lines = [
        "# HTTPS Baseline Audit Report",
        "",
        f"Generated from `{SUMMARY_TSV}`.",
        "",
        "This audit covers only the minimal public HTTPS baseline for frawo-tech.de and www.frawo-tech.de.",
        "It is intentionally smaller than the full website-release gate.",
        "",
    ]

    labels = {
        "codex": "Codex",
        "operator": "Operator",
    }
    for executor in ("codex", "operator"):
        lines.append(f"## {labels[executor]}")
        lines.append("")
        executor_rows = by_executor.get(executor, [])
        if not executor_rows:
            lines.append("- none")
            lines.append("")
            continue
        for row in executor_rows:
            detail = row["command_or_action"]
            if row["log"] != "-":
                detail = f"{detail} (`{row['log']}`)"
            lines.append(f"- `{row['id']}`: `{row['status']}` - {detail}")
        lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, str]] = []
    for check_id, command in CODEX_CHECKS:
        rows.append(run_check(check_id, command))

    for check_id, executor, action in MANUAL_TASKS:
        rows.append(
            {
                "id": check_id,
                "executor": executor,
                "status": "pending_manual",
                "command_or_action": action,
                "log": "-",
            }
        )

    with SUMMARY_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["id", "executor", "status", "command_or_action", "log"],
            delimiter="\t",
        )
        writer.writeheader()
        writer.writerows(rows)

    build_report(rows)

    print(f"https_baseline_audit_report_dir={REPORT_DIR}")
    print(f"https_baseline_audit_summary={SUMMARY_TSV}")
    print(f"https_baseline_audit_report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

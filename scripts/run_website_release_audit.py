#!/usr/bin/env python3
from __future__ import annotations

import csv
import subprocess
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT_DIR / "artifacts" / "website_release_audit" / datetime.now().strftime("%Y%m%d_%H%M%S")
SUMMARY_TSV = REPORT_DIR / "summary.tsv"
REPORT_MD = REPORT_DIR / "report.md"


CODEX_CHECKS: list[tuple[str, list[str]]] = [
    ("document-ownership-check", [sys.executable, "./scripts/document_ownership_check.py"]),
    ("public-dns-check", [sys.executable, "./scripts/public_dns_check.py"]),
    ("public-http-redirect-check", [sys.executable, "./scripts/public_http_redirect_check.py"]),
    ("public-dualstack-edge-check", [sys.executable, "./scripts/public_dualstack_edge_check.py"]),
    ("public-https-check", [sys.executable, "./scripts/public_https_check.py"]),
    ("public-mail-dns-check", [sys.executable, "./scripts/public_mail_dns_check.py"]),
    ("public-edge-preview-check", [sys.executable, "./scripts/public_edge_preview_check.py"]),
]

MANUAL_TASKS: list[tuple[str, str, str]] = [
    ("website_target_system_verified", "admin_only", "Confirm the target system is the public Odoo website frontend on VM220 and not a public Odoo admin path."),
    ("website_content_verified", "wolfi", "Confirm the public Odoo-managed website content is the intended GbR release content."),
    ("public_browser_acceptance_verified", "gemini_browser_ai", "Visibly verify apex and www browser behavior for the website release scope."),
    ("public_radio_integration_verified", "gemini_browser_ai", "Visibly verify the public website includes the intended radio presence or player path."),
    ("public_mail_model_verified", "admin_only", "Confirm webmaster, franz, info and noreply are correct for the public release."),
    ("tls_automation_verified", "admin_only", "Confirm the chosen public TLS automation path is configured and documented."),
    ("spf_dkim_dmarc_verified", "admin_only", "Confirm SPF, DKIM and DMARC are all intentionally configured for release."),
    ("rollback_runbook_verified", "admin_only", "Confirm rollback for DNS, TLS and host-switch is complete and usable."),
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
        "# Website Release Audit Report",
        "",
        f"Generated from `{SUMMARY_TSV}`.",
        "",
        "This audit covers the website release track only.",
        "It is separate from the business MVP gate and from full internal certification.",
        "",
    ]

    labels = {
        "codex": "Codex",
        "gemini_browser_ai": "Gemini Browser AI",
        "admin_only": "Admin-only",
        "wolfi": "Wolfi",
    }
    for executor in ("codex", "gemini_browser_ai", "admin_only", "wolfi"):
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

    print(f"website_release_audit_report_dir={REPORT_DIR}")
    print(f"website_release_audit_summary={SUMMARY_TSV}")
    print(f"website_release_audit_report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import sys
from datetime import datetime
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT_DIR / "artifacts" / "https_baseline_audit"
OUTPUT_ROOT = ROOT_DIR / "artifacts" / "https_baseline_gate"
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

CRITICAL_CODEX_CHECKS = [
    "public-dns-check",
    "public-http-redirect-check",
    "public-https-check",
]


def find_latest_summary() -> Path:
    candidates = sorted(
        path / "summary.tsv"
        for path in AUDIT_ROOT.iterdir()
        if path.is_dir() and path.name[:8].isdigit()
    )
    if not candidates:
        raise FileNotFoundError("https_baseline_summary_not_found")
    return candidates[-1]


def main() -> int:
    summary_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_latest_summary()
    if not summary_path.is_file():
        print("https_baseline_gate_error=summary_not_found", file=sys.stderr)
        return 1

    report_dir = OUTPUT_ROOT / TIMESTAMP
    report_dir.mkdir(parents=True, exist_ok=True)
    json_report_path = report_dir / "https_baseline_gate.json"
    md_report_path = report_dir / "https_baseline_gate.md"

    summary_rows = list(csv.DictReader(summary_path.open("r", encoding="utf-8"), delimiter="\t"))
    summary_by_id = {row["id"]: row for row in summary_rows}

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
            blocked_reasons.append(f"missing critical https-baseline check: {check_id}")
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
            blocked_reasons.append(f"critical https-baseline check not green: {check_id}={row['status']}")

    decision = "HTTPS_BASELINE_READY" if not blocked_reasons else "BLOCKED"
    report = {
        "decision": decision,
        "summary_source": str(summary_path),
        "critical_codex_checks": codex_results,
        "blocked_reasons": blocked_reasons,
        "scope_note": (
            "This gate covers only the minimal public HTTPS baseline for frawo-tech.de and www.frawo-tech.de. "
            "It is intentionally smaller than the full website release gate."
        ),
    }
    json_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# HTTPS Baseline Gate",
        "",
        f"Decision: `{decision}`",
        "",
        f"HTTPS baseline audit summary: `{summary_path}`",
        "",
        "## Scope Note",
        "",
        "This gate covers only the minimal public HTTPS baseline for frawo-tech.de and www.frawo-tech.de.",
        "It is intentionally smaller than the full website-release gate.",
        "",
        "## Critical HTTPS-Baseline Checks",
        "",
    ]
    for row in codex_results:
        lines.append(f"- `{row['id']}`: `{row['status']}`")

    lines.extend(["", "## Blocked Reasons", ""])
    if blocked_reasons:
        for reason in blocked_reasons:
            lines.append(f"- {reason}")
    else:
        lines.append("- none")
    md_report_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"decision={decision}")
    print(f"json_report={json_report_path}")
    print(f"markdown_report={md_report_path}")
    print(f"https_baseline_gate_report_dir={report_dir}")
    if blocked_reasons:
        print(f"blocked_reason_count={len(blocked_reasons)}")
    return 0 if decision == "HTTPS_BASELINE_READY" else 1


if __name__ == "__main__":
    raise SystemExit(main())

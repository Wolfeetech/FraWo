#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MANUAL_CHECKS_FILE="${ROOT_DIR}/manifests/release_mvp_gate/manual_checks.json"
AUDIT_ROOT="${ROOT_DIR}/artifacts/release_mvp_audit"
OUTPUT_ROOT="${ROOT_DIR}/artifacts/release_mvp_gate"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"

find_latest_summary() {
  local latest_dir
  latest_dir="$(
    find "${AUDIT_ROOT}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null \
      | while IFS= read -r dir; do
          base="$(basename "${dir}")"
          [[ "${base}" =~ ^[0-9]{8}_[0-9]{6}$ ]] || continue
          printf '%s\n' "${dir}"
        done \
      | sort \
      | tail -n 1
  )"
  if [[ -z "${latest_dir}" ]]; then
    return 1
  fi
  printf '%s/summary.tsv\n' "${latest_dir}"
}

SUMMARY_PATH="${1:-}"
if [[ -z "${SUMMARY_PATH}" ]]; then
  SUMMARY_PATH="$(find_latest_summary)"
fi

if [[ ! -f "${SUMMARY_PATH}" ]]; then
  echo "release_mvp_gate_error=summary_not_found" >&2
  exit 1
fi

if [[ ! -f "${MANUAL_CHECKS_FILE}" ]]; then
  echo "release_mvp_gate_error=manual_checks_file_not_found" >&2
  exit 1
fi

REPORT_DIR="${OUTPUT_ROOT}/${TIMESTAMP}"
mkdir -p "${REPORT_DIR}"

JSON_REPORT="${REPORT_DIR}/release_mvp_gate.json"
MD_REPORT="${REPORT_DIR}/release_mvp_gate.md"
OWNERSHIP_LOG="${REPORT_DIR}/document-ownership-check.log"
OWNERSHIP_STATUS="passed"

if ! bash -lc "cd ${ROOT_DIR@Q} && make document-ownership-check" >"${OWNERSHIP_LOG}" 2>&1; then
  OWNERSHIP_STATUS="failed"
fi

python3 - <<'PY' "${SUMMARY_PATH}" "${MANUAL_CHECKS_FILE}" "${JSON_REPORT}" "${MD_REPORT}" "${OWNERSHIP_STATUS}" "${OWNERSHIP_LOG}"
import csv
import json
import sys
from pathlib import Path

summary_path = Path(sys.argv[1])
manual_path = Path(sys.argv[2])
json_report_path = Path(sys.argv[3])
md_report_path = Path(sys.argv[4])
ownership_status = sys.argv[5]
ownership_log = sys.argv[6]

critical_codex_checks = [
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

summary_rows = list(csv.DictReader(summary_path.open("r", encoding="utf-8"), delimiter="\t"))
manual_data = json.loads(manual_path.read_text(encoding="utf-8"))
manual_checks = manual_data.get("checks", [])

summary_by_id = {row["id"]: row for row in summary_rows}
summary_by_id["document-ownership-check"] = {
    "id": "document-ownership-check",
    "status": ownership_status,
    "log": ownership_log,
    "executor": "codex",
    "command_or_action": "make document-ownership-check",
}

codex_results = []
blocked_reasons = []

for check_id in critical_codex_checks:
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

manual_results = []
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
    "manual_checks_source": str(manual_path),
    "critical_codex_checks": codex_results,
    "manual_checks": manual_results,
    "blocked_reasons": blocked_reasons,
    "scope_note": (
        "This gate covers the current business MVP only. PBS, Radio/AzuraCast integration, "
        "shared frontend certification, and the full production seal remain outside this decision."
    ),
}

json_report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

lines = [
    "# Release MVP Gate",
    "",
    f"Decision: `{decision}`",
    "",
    f"MVP audit summary: `{summary_path}`",
    f"Manual evidence: `{manual_path}`",
    "",
    "## Scope Note",
    "",
    "This gate covers the current business MVP only.",
    "It is not the same as the full internal production certification.",
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

md_report_path.write_text("\n".join(lines), encoding="utf-8")

print(f"decision={decision}")
print(f"json_report={json_report_path}")
print(f"markdown_report={md_report_path}")
if blocked_reasons:
    print(f"blocked_reason_count={len(blocked_reasons)}")
PY

echo "release_mvp_gate_report_dir=${REPORT_DIR}"

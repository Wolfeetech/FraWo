#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/release_mvp_audit/${TIMESTAMP}"
SUMMARY_TSV="${REPORT_DIR}/summary.tsv"
REPORT_MD="${REPORT_DIR}/report.md"

mkdir -p "${REPORT_DIR}"

cat >"${SUMMARY_TSV}" <<'EOF'
id	executor	status	command_or_action	log
EOF

refine_release_mvp_status() {
  local id="$1"
  local current_status="$2"
  local log_path="$3"

  if [[ "${current_status}" != "passed" ]]; then
    printf '%s\n' "${current_status}"
    return 0
  fi

  case "${id}" in
    core-app-smtp-check)
      grep -q '^core_business_app_smtp_ready=yes$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    *)
      echo "passed"
      ;;
  esac
}

run_codex_check() {
  local id="$1"
  local command="$2"
  local log_path="${REPORT_DIR}/${id}.log"
  local status="passed"

  if ! bash -lc "cd ${ROOT_DIR@Q} && ${command}" >"${log_path}" 2>&1; then
    status="failed"
  fi
  status="$(refine_release_mvp_status "${id}" "${status}" "${log_path}")"

  printf '%s\t%s\t%s\t%s\t%s\n' "${id}" "codex" "${status}" "${command}" "${log_path}" >>"${SUMMARY_TSV}"
}

append_manual_task() {
  local id="$1"
  local executor="$2"
  local action="$3"
  printf '%s\t%s\t%s\t%s\t%s\n' "${id}" "${executor}" "pending_manual" "${action}" "-" >>"${SUMMARY_TSV}"
}

CODEX_CHECKS=(
  "document-ownership-check|make document-ownership-check"
  "inventory-check|make inventory-check"
  "ansible-ping|make ansible-ping"
  "qga-check|make qga-check"
  "business-drift-check|make business-drift-check"
  "toolbox-network-check|make toolbox-network-check"
  "toolbox-portal-status-check|make toolbox-portal-status-check"
  "vaultwarden-smtp-check|make vaultwarden-smtp-check"
  "proxmox-local-backup-check|make proxmox-local-backup-check"
  "security-baseline-check|make security-baseline-check"
  "core-app-smtp-check|bash ./scripts/app_smtp_check.sh"
)

for entry in "${CODEX_CHECKS[@]}"; do
  IFS='|' read -r id command <<<"${entry}"
  run_codex_check "${id}" "${command}"
done

append_manual_task "frawo-access-verified" "gemini_browser_ai" "Verify Franz can open FraWo and see the required collections and core entries."
append_manual_task "vaultwarden-visible-spotcheck" "gemini_browser_ai" "Open core imported entries in the Vaultwarden UI and verify they are usable."
append_manual_task "wolf-login-walkthrough" "gemini_browser_ai" "Walk Wolf through Vault, Nextcloud, Paperless and Odoo."
append_manual_task "franz-login-walkthrough" "gemini_browser_ai" "Walk Franz through Vault, Nextcloud, Paperless and Odoo."
append_manual_task "strato-mail-model-verified" "admin_only" "Visibly verify send and receive for webmaster, franz and noreply."
append_manual_task "device-rollout-verified" "admin_only" "Verify Franz Surface Laptop and iPhone direct entrypoints and device-local rollout."
append_manual_task "core-app-smtp-functional-test-verified" "admin_only" "Perform visible test mails for Nextcloud, Paperless and Odoo."
append_manual_task "vaultwarden-recovery-material-verified" "admin_only" "Verify the offline Vaultwarden recovery material in two separate copies."

python3 - <<'PY' "${SUMMARY_TSV}" "${REPORT_MD}"
import csv
import sys
from collections import defaultdict
from pathlib import Path

summary_path = Path(sys.argv[1])
report_path = Path(sys.argv[2])
rows = list(csv.DictReader(summary_path.open("r", encoding="utf-8"), delimiter="\t"))
by_executor = defaultdict(list)
for row in rows:
    by_executor[row["executor"]].append(row)

lines = [
    "# Release MVP Audit Report",
    "",
    f"Generated from `{summary_path}`.",
    "",
    "This audit is intentionally narrower than the full production gate.",
    "It covers the current business MVP only.",
    "",
]

for executor in ("codex", "gemini_browser_ai", "admin_only"):
    label = {
        "codex": "Codex",
        "gemini_browser_ai": "Gemini Browser AI",
        "admin_only": "Admin-only",
    }[executor]
    lines.append(f"## {label}")
    lines.append("")
    if not by_executor[executor]:
        lines.append("- none")
        lines.append("")
        continue
    for row in by_executor[executor]:
        detail = row["command_or_action"]
        if row["log"] != "-":
            detail = f"{detail} (`{row['log']}`)"
        lines.append(f"- `{row['id']}`: `{row['status']}` - {detail}")
    lines.append("")

report_path.write_text("\n".join(lines), encoding="utf-8")
PY

echo "release_mvp_audit_report_dir=${REPORT_DIR}"
echo "release_mvp_audit_summary=${SUMMARY_TSV}"
echo "release_mvp_audit_report=${REPORT_MD}"

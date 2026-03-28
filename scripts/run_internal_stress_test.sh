#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/stress_tests/${TIMESTAMP}"
SUMMARY_TSV="${REPORT_DIR}/summary.tsv"
REPORT_MD="${REPORT_DIR}/report.md"

mkdir -p "${REPORT_DIR}"

cat >"${SUMMARY_TSV}" <<'EOF'
id	executor	status	command_or_action	log
EOF

refine_codex_status() {
  local id="$1"
  local current_status="$2"
  local log_path="$3"

  case "${id}" in
    backup-list|proxmox-local-backup-check)
      if grep -Eq '^no qemu backups present in /var/lib/vz/dump$|^no_qemu_archives$' "${log_path}"; then
        echo "failed"
      elif grep -Eq '/var/lib/vz/dump/vzdump-qemu-[0-9]+-.*\.vma\.zst' "${log_path}"; then
        echo "passed"
      else
        printf '%s\n' "${current_status}"
      fi
      return 0
      ;;
  esac

  if [[ "${current_status}" != "passed" ]]; then
    printf '%s\n' "${current_status}"
    return 0
  fi

  case "${id}" in
    security-baseline-check)
      grep -q '^security_status=ok$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    pbs-stage-gate)
      grep -q '^pbs_stage_gate_ready=yes$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    pbs-proof-check)
      if grep -q '^pbs_storage_active=yes$' "${log_path}" && grep -q '^pbs_proof_backup_exists=yes$' "${log_path}"; then
        echo "passed"
      else
        echo "failed"
      fi
      ;;
    rpi-radio-integration-check)
      grep -q '^rpi_radio_integrated=yes$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    rpi-radio-usb-check)
      grep -q '^rpi_radio_usb_music_ready=yes$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    app-smtp-check)
      grep -q '^app_smtp_ready=yes$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    haos-stage-gate)
      grep -q '^haos_stage_gate_ready=yes$' "${log_path}" && echo "passed" || echo "failed"
      ;;
    surface-go-check)
      if grep -q '^surface_go_remote_admin_ready=yes$' "${log_path}" && grep -q '^surface_go_portal_service_active=active$' "${log_path}" && grep -q '^surface_go_local_portal_http=ok$' "${log_path}"; then
        echo "passed"
      else
        echo "failed"
      fi
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
  status="$(refine_codex_status "${id}" "${status}" "${log_path}")"

  printf '%s\t%s\t%s\t%s\t%s\n' "${id}" "codex" "${status}" "${command}" "${log_path}" >>"${SUMMARY_TSV}"
}

append_manual_task() {
  local id="$1"
  local executor="$2"
  local action="$3"
  printf '%s\t%s\t%s\t%s\t%s\n' "${id}" "${executor}" "pending_manual" "${action}" "-" >>"${SUMMARY_TSV}"
}

summary_status() {
  local id="$1"
  awk -F'\t' -v id="${id}" 'NR > 1 && $1 == id {print $3; exit}' "${SUMMARY_TSV}"
}

CODEX_CHECKS=(
  "document-ownership-check|make document-ownership-check"
  "inventory-check|make inventory-check"
  "ansible-ping|make ansible-ping"
  "qga-check|make qga-check"
  "business-drift-check|make business-drift-check"
  "toolbox-network-check|make toolbox-network-check"
  "toolbox-portal-status-check|make toolbox-portal-status-check"
  "toolbox-media-check|make toolbox-media-check"
  "toolbox-tailscale-check|make toolbox-tailscale-check"
  "vaultwarden-smtp-check|make vaultwarden-smtp-check"
  "rpi-radio-integration-check|make rpi-radio-integration-check"
  "rpi-radio-usb-check|make rpi-radio-usb-check"
  "haos-reverse-proxy-check|make haos-reverse-proxy-check"
  "backup-list|make backup-list"
  "proxmox-local-backup-check|make proxmox-local-backup-check"
  "pbs-stage-gate|make pbs-stage-gate"
  "pbs-proof-check|make pbs-proof-check"
  "app-smtp-check|make app-smtp-check"
  "haos-stage-gate|make haos-stage-gate"
  "security-baseline-check|make security-baseline-check"
  "surface-go-check|make surface-go-check"
)

for entry in "${CODEX_CHECKS[@]}"; do
  IFS='|' read -r id command <<<"${entry}"
  run_codex_check "${id}" "${command}"
done

append_manual_task "vaultwarden-visible-spotcheck" "gemini_browser_ai" "Invite Franz to FraWo, verify shared collections, and spot-check imported Vaultwarden entries in the UI."
append_manual_task "internal-app-login-walkthrough" "gemini_browser_ai" "Walk Wolf and Franz through Portal, Nextcloud, Paperless, Odoo, Jellyfin, and Radio browser logins and record visible issues."
append_manual_task "surface-laptop-and-iphone-acceptance" "gemini_browser_ai" "Open the Franz start surface on Surface Laptop and iPhone and verify direct website/app entrypoints."
append_manual_task "shared-frontend-acceptance" "gemini_browser_ai" "Verify the shared surface-go-frontend and TV/Jellyfin shared path within the certified internal scope."
append_manual_task "strato-browser-verification" "gemini_browser_ai" "Review STRATO aliases/postboxes in the browser and capture the confirmed mailbox model."

append_manual_task "strato-mailbox-control" "admin_only" "Create, alter, or remove STRATO postboxes and aliases; verify send/receive with real accounts."
append_manual_task "device-local-rollout" "admin_only" "Install homescreen shortcuts, saved passwords, Tailscale, and local trust prompts on Franz Surface Laptop and iPhone."
append_manual_task "app-smtp-functional-test" "admin_only" "Send and receive visible test mails for Nextcloud, Paperless, Odoo and AzuraCast after SMTP baseline deployment."
append_manual_task "vaultwarden-recovery-material" "admin_only" "Verify the offline Vaultwarden recovery sheet and second separate offline copy."

if [[ "$(summary_status "ansible-ping")" != "passed" || "$(summary_status "qga-check")" != "passed" ]]; then
  append_manual_task "ssh-auth-repair" "admin_only" "Repair missing SSH keys/password distribution for proxmox, toolbox, nextcloud_vm, odoo_vm, paperless_vm, and pbs if Codex checks fail on auth."
fi

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
    "# Internal Stress Test Report",
    "",
    f"Generated from `{summary_path}`.",
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
      status = row["status"]
      if row["log"] != "-":
        detail = f"{detail} (`{row['log']}`)"
      lines.append(f"- `{row['id']}`: `{status}` - {detail}")
    lines.append("")

report_path.write_text("\n".join(lines), encoding="utf-8")
PY

echo "stress_test_report_dir=${REPORT_DIR}"
echo "stress_test_summary=${SUMMARY_TSV}"
echo "stress_test_report=${REPORT_MD}"

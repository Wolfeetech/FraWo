#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

business_health="no"
if "${ROOT_DIR}/scripts/business_service_drift_check.sh" >/dev/null 2>&1; then
  business_health="yes"
fi

capacity_output="$("${ROOT_DIR}/scripts/capacity_review_check.sh")"
configured_guest_memory_pct_of_host="$(extract_value configured_guest_memory_pct_of_host "${capacity_output}")"
capacity_risk="$(extract_value capacity_risk "${capacity_output}")"

backups_current="no"
for vmid in 200 220; do
  if ssh proxmox "ls -1 /var/lib/vz/dump/vzdump-qemu-${vmid}-*.vma.zst >/dev/null 2>&1"; then
    backups_current="yes"
  else
    backups_current="no"
    break
  fi
done

echo "business_health=${business_health}"
echo "configured_guest_memory_pct_of_host=${configured_guest_memory_pct_of_host}"
echo "capacity_risk=${capacity_risk}"
echo "backups_current=${backups_current}"
echo "maintenance_window_required=yes"

if [[ "${business_health}" == "yes" && "${backups_current}" == "yes" && "${capacity_risk}" == "overcommitted" ]]; then
  echo "rightsize_stage_gate_ready=yes"
  echo "recommendation=schedule_nextcloud_and_odoo_rightsizing_in_a_maintenance_window"
else
  echo "rightsize_stage_gate_ready=no"
  echo "recommendation=clear_health_or_backup_gaps_before_rightsizing"
fi

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

log() {
  printf '[pbs-stage-gate] %s\n' "$*"
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

backup_timer_live="no"
if ssh proxmox "systemctl is-enabled --quiet homeserver2027-local-business-backup.timer && systemctl is-active --quiet homeserver2027-local-business-backup.timer" >/dev/null 2>&1; then
  backup_timer_live="yes"
fi

local_backup_archives_present="no"
if ssh proxmox "ls /var/lib/vz/dump/vzdump-qemu-200-*.vma.zst /var/lib/vz/dump/vzdump-qemu-210-*.vma.zst /var/lib/vz/dump/vzdump-qemu-220-*.vma.zst /var/lib/vz/dump/vzdump-qemu-230-*.vma.zst >/dev/null 2>&1"; then
  local_backup_archives_present="yes"
fi

log "Reading PBS preflight output"
preflight_output="$("${ROOT_DIR}/scripts/pbs_preflight_check.sh")"
printf '%s\n' "$preflight_output"

vm240_exists="$(extract_value vm240_exists "$preflight_output")"
pbs_4gb_fit="$(extract_value pbs_4gb_fit "$preflight_output")"
pbs_system_disk_fit="$(extract_value pbs_system_disk_fit "$preflight_output")"
pbs_iso_present="$(extract_value pbs_iso_present "$preflight_output")"
separate_backup_storage_ready="$(extract_value separate_backup_storage_ready "$preflight_output")"

pbs_stage_gate_ready="no"
if [[ "$backup_timer_live" == "yes" && "$local_backup_archives_present" == "yes" && "$vm240_exists" == "no" && "$pbs_4gb_fit" == "yes" && "$pbs_system_disk_fit" == "yes" && "$pbs_iso_present" == "yes" && "$separate_backup_storage_ready" == "yes" ]]; then
  pbs_stage_gate_ready="yes"
fi

echo "backup_timer_live=${backup_timer_live}"
echo "local_backup_archives_present=${local_backup_archives_present}"
echo "pbs_stage_gate_ready=${pbs_stage_gate_ready}"

if [[ "$pbs_stage_gate_ready" == "yes" ]]; then
  echo "recommendation=build_pbs_vm_240_now"
elif [[ "$separate_backup_storage_ready" != "yes" ]]; then
  echo "recommendation=wait_for_separate_backup_storage_before_building_pbs_vm"
elif [[ "$pbs_iso_present" != "yes" ]]; then
  echo "recommendation=stage_official_pbs_iso_then_build_vm240"
else
  echo "recommendation=hold_pbs_vm_until_preflight_is_green"
fi

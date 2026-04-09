#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

log() {
  printf '[pbs-stage-gate] %s\n' "$*"
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

backup_timer_live="no"
if run_proxmox_remote "systemctl is-enabled --quiet homeserver2027-local-business-backup.timer && systemctl is-active --quiet homeserver2027-local-business-backup.timer" >/dev/null 2>&1; then
  backup_timer_live="yes"
fi

local_backup_archives_present="no"
if run_proxmox_remote "ls /var/lib/vz/dump/vzdump-qemu-200-*.vma.zst /var/lib/vz/dump/vzdump-qemu-210-*.vma.zst /var/lib/vz/dump/vzdump-qemu-220-*.vma.zst /var/lib/vz/dump/vzdump-qemu-230-*.vma.zst >/dev/null 2>&1"; then
  local_backup_archives_present="yes"
fi

log "Reading PBS preflight output"
preflight_output="$("${ROOT_DIR}/scripts/pbs_preflight_check.sh")"
printf '%s\n' "$preflight_output"

vm240_exists="$(extract_value vm240_exists "$preflight_output")"
vm240_system_storage_expected="$(extract_value vm240_system_storage_expected "$preflight_output")"
vm240_data_storage_expected="$(extract_value vm240_data_storage_expected "$preflight_output")"
pbs_4gb_fit="$(extract_value pbs_4gb_fit "$preflight_output")"
pbs_system_disk_fit="$(extract_value pbs_system_disk_fit "$preflight_output")"
pbs_iso_present="$(extract_value pbs_iso_present "$preflight_output")"
separate_backup_storage_ready="$(extract_value separate_backup_storage_ready "$preflight_output")"
guest_postinstall_output="$("${ROOT_DIR}/scripts/pbs_guest_postinstall_check.sh")"
pbs_guest_postinstall_ready="$(extract_value pbs_guest_postinstall_ready "$guest_postinstall_output")"
proof_backup_output="$("${ROOT_DIR}/scripts/pbs_proof_backup_check.sh")"
pbs_storage_active="$(extract_value pbs_storage_active "$proof_backup_output")"
pbs_proof_backup_exists="$(extract_value pbs_proof_backup_exists "$proof_backup_output")"

pbs_stage_gate_ready="no"
if [[ "$backup_timer_live" == "yes" && "$local_backup_archives_present" == "yes" && "$pbs_guest_postinstall_ready" == "yes" && "$pbs_storage_active" == "yes" && "$pbs_proof_backup_exists" == "yes" ]]; then
  pbs_stage_gate_ready="yes"
fi

echo "backup_timer_live=${backup_timer_live}"
echo "local_backup_archives_present=${local_backup_archives_present}"
echo "pbs_guest_postinstall_ready=${pbs_guest_postinstall_ready}"
echo "pbs_storage_active=${pbs_storage_active}"
echo "pbs_proof_backup_exists=${pbs_proof_backup_exists}"
echo "pbs_stage_gate_ready=${pbs_stage_gate_ready}"

if [[ "$pbs_stage_gate_ready" == "yes" ]]; then
  echo "recommendation=begin_restore_drills_on_pbs_v1"
elif [[ "$pbs_guest_postinstall_ready" == "yes" && "$pbs_storage_active" == "yes" && "$pbs_proof_backup_exists" != "yes" ]]; then
  echo "recommendation=stabilize_proof_backup_on_active_pbs"
elif [[ "$vm240_exists" == "yes" && ( "$vm240_system_storage_expected" != "yes" || "$vm240_data_storage_expected" != "yes" ) ]]; then
  echo "recommendation=rebuild_vm240_to_match_runner_storage_contract"
elif [[ "$vm240_exists" == "yes" ]]; then
  echo "recommendation=finish_guest_install_for_existing_vm240"
elif [[ "$separate_backup_storage_ready" != "yes" ]]; then
  echo "recommendation=wait_for_separate_backup_storage_before_building_pbs_vm"
elif [[ "$pbs_iso_present" != "yes" ]]; then
  echo "recommendation=stage_official_pbs_iso_then_build_vm240"
else
  echo "recommendation=hold_pbs_vm_until_preflight_is_green"
fi

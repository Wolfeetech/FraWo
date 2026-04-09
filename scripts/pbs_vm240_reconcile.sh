#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/pbs_vm240_reconcile/${TIMESTAMP}"
REPORT_MD="${REPORT_DIR}/report.md"

mkdir -p "${REPORT_DIR}"

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "${ROOT_DIR}/ansible/inventory/host_vars/proxmox.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

VMID="$(read_hostvar proxmox_pbs_vmid)"
RUNNER_PATH="$(read_hostvar proxmox_pbs_runner_script_path)"

EXECUTE_MODE="${PBS_VM240_EXECUTE:-no}"
ALLOW_DESTROY="${PBS_VM240_ALLOW_DESTROY:-no}"

contract_output="$("${ROOT_DIR}/scripts/pbs_rebuild_contract_check.sh")"
contract_report="$(extract_value pbs_rebuild_contract_report "${contract_output}")"
contract_recommendation="$(extract_value pbs_rebuild_contract_recommendation "${contract_output}")"

preflight_output="$("${ROOT_DIR}/scripts/pbs_preflight_check.sh")"
vm_exists="$(extract_value vm240_exists "${preflight_output}")"
vm_system_storage_expected="$(extract_value vm240_system_storage_expected "${preflight_output}")"
vm_data_storage_expected="$(extract_value vm240_data_storage_expected "${preflight_output}")"
pbs_iso_present="$(extract_value pbs_iso_present "${preflight_output}")"
separate_backup_storage_ready="$(extract_value separate_backup_storage_ready "${preflight_output}")"

guest_output="$("${ROOT_DIR}/scripts/pbs_guest_postinstall_check.sh")"
pbs_guest_postinstall_ready="$(extract_value pbs_guest_postinstall_ready "${guest_output}")"

runner_present="no"
if run_proxmox_remote "test -x ${RUNNER_PATH@Q}"; then
  runner_present="yes"
fi

vm_status="absent"
if [[ "${vm_exists}" == "yes" ]]; then
  vm_status="$(run_proxmox_remote "qm status ${VMID} | awk '{print \$2}'")"
fi

vm_reconcile_required="no"
if [[ "${vm_exists}" == "yes" && ( "${vm_system_storage_expected}" != "yes" || "${vm_data_storage_expected}" != "yes" ) ]]; then
  vm_reconcile_required="yes"
fi

safe_to_rebuild="no"
if [[ "${contract_recommendation}" == "ready_for_guarded_pbs_datastore_prepare" \
      && "${pbs_iso_present}" == "yes" \
      && "${separate_backup_storage_ready}" == "yes" \
      && "${runner_present}" == "yes" ]]; then
  safe_to_rebuild="yes"
fi

action_taken="none"
recommendation="wait_for_contract_and_datastore_prepare"

if [[ "${vm_reconcile_required}" == "no" && "${vm_exists}" == "yes" ]]; then
  recommendation="vm240_matches_storage_contract_validate_guest_install"
elif [[ "${safe_to_rebuild}" == "yes" ]]; then
  recommendation="ready_for_guarded_vm240_rebuild"
fi

if [[ "${EXECUTE_MODE}" == "yes" ]]; then
  if [[ "${safe_to_rebuild}" != "yes" ]]; then
    recommendation="execution_blocked_until_contract_iso_and_datastore_are_green"
  elif [[ "${ALLOW_DESTROY}" != "yes" ]]; then
    recommendation="execution_blocked_until_PBS_VM240_ALLOW_DESTROY=yes"
  elif [[ "${vm_exists}" == "yes" && "${pbs_guest_postinstall_ready}" != "no" ]]; then
    recommendation="execution_blocked_existing_vm240_has_guest_signals_manual_migration_required"
  elif [[ "${vm_exists}" == "yes" && "${vm_status}" != "stopped" ]]; then
    recommendation="execution_blocked_stop_vm240_before_destroy_rebuild"
  else
    if [[ "${vm_exists}" == "yes" ]]; then
      run_proxmox_remote "qm destroy ${VMID} --destroy-unreferenced-disks 1 --purge 1"
      action_taken="destroyed_existing_vm240"
    fi
    run_proxmox_remote "${RUNNER_PATH@Q}"
    if [[ "${action_taken}" == "none" ]]; then
      action_taken="created_vm240_via_runner"
    else
      action_taken="${action_taken}_and_recreated_via_runner"
    fi
    recommendation="complete_pbs_installer_in_vm240_console"
    vm_exists="yes"
    vm_status="$(run_proxmox_remote "qm status ${VMID} | awk '{print \$2}'")"
  fi
fi

{
  echo "# PBS VM240 Reconcile"
  echo
  echo "- Execute mode: \`${EXECUTE_MODE}\`"
  echo "- Allow destroy: \`${ALLOW_DESTROY}\`"
  echo "- Contract recommendation: \`${contract_recommendation}\`"
  echo "- Contract report: \`${contract_report}\`"
  echo "- PBS ISO present: \`${pbs_iso_present}\`"
  echo "- Separate datastore ready: \`${separate_backup_storage_ready}\`"
  echo "- Runner present: \`${runner_present}\`"
  echo "- VM exists: \`${vm_exists}\`"
  echo "- VM status: \`${vm_status}\`"
  echo "- VM system storage expected: \`${vm_system_storage_expected}\`"
  echo "- VM data storage expected: \`${vm_data_storage_expected}\`"
  echo "- VM reconcile required: \`${vm_reconcile_required}\`"
  echo "- PBS guest postinstall ready: \`${pbs_guest_postinstall_ready}\`"
  echo "- Safe to rebuild: \`${safe_to_rebuild}\`"
  echo "- Action taken: \`${action_taken}\`"
  echo "- Recommendation: \`${recommendation}\`"
} > "${REPORT_MD}"

echo "pbs_vm240_reconcile_report=${REPORT_MD}"
echo "pbs_vm240_execute_mode=${EXECUTE_MODE}"
echo "pbs_vm240_allow_destroy=${ALLOW_DESTROY}"
echo "pbs_vm240_contract_recommendation=${contract_recommendation}"
echo "pbs_vm240_pbs_iso_present=${pbs_iso_present}"
echo "pbs_vm240_separate_datastore_ready=${separate_backup_storage_ready}"
echo "pbs_vm240_runner_present=${runner_present}"
echo "pbs_vm240_exists=${vm_exists}"
echo "pbs_vm240_status=${vm_status}"
echo "pbs_vm240_system_storage_expected=${vm_system_storage_expected}"
echo "pbs_vm240_data_storage_expected=${vm_data_storage_expected}"
echo "pbs_vm240_reconcile_required=${vm_reconcile_required}"
echo "pbs_vm240_guest_postinstall_ready=${pbs_guest_postinstall_ready}"
echo "pbs_vm240_safe_to_rebuild=${safe_to_rebuild}"
echo "pbs_vm240_action_taken=${action_taken}"
echo "recommendation=${recommendation}"

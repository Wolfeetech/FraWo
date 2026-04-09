#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
REPORT_DIR="${ROOT_DIR}/artifacts/pbs_guarded_rebuild/${TIMESTAMP}"
REPORT_MD="${REPORT_DIR}/report.md"

mkdir -p "${REPORT_DIR}"

RUN_EXECUTE="${PBS_GUARDED_EXECUTE:-no}"
DATASTORE_DEVICE="${DEV:-${PBS_DATASTORE_DEVICE:-}}"

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

run_step() {
  local name="$1"
  shift
  local log_path="${REPORT_DIR}/${name}.log"
  if "$@" >"${log_path}" 2>&1; then
    echo "passed"
  else
    echo "failed"
  fi
}

audit_status="$(run_step pbs_rebuild_storage_audit bash -lc "cd ${ROOT_DIR@Q} && ./scripts/pbs_rebuild_storage_audit.sh")"
audit_log="${REPORT_DIR}/pbs_rebuild_storage_audit.log"
audit_recommendation="$(extract_value pbs_storage_recommendation "$(cat "${audit_log}")")"

contract_status="$(run_step pbs_rebuild_contract_check bash -lc "cd ${ROOT_DIR@Q} && ./scripts/pbs_rebuild_contract_check.sh")"
contract_log="${REPORT_DIR}/pbs_rebuild_contract_check.log"
contract_recommendation="$(extract_value pbs_rebuild_contract_recommendation "$(cat "${contract_log}")")"

runner_deploy_status="$(run_step pbs_runner_deploy bash -lc "cd ${ROOT_DIR@Q} && make pbs-runner-deploy")"

preflight_status="$(run_step pbs_preflight bash -lc "cd ${ROOT_DIR@Q} && ./scripts/pbs_preflight_check.sh")"
preflight_log="${REPORT_DIR}/pbs_preflight.log"
separate_backup_storage_ready="$(extract_value separate_backup_storage_ready "$(cat "${preflight_log}")")"
pbs_iso_present="$(extract_value pbs_iso_present "$(cat "${preflight_log}")")"

datastore_prepare_status="skipped"
vm_reconcile_status="skipped"
final_recommendation="wait_for_contract_and_datastore_prepare"

if [[ "${RUN_EXECUTE}" == "yes" ]]; then
  if [[ -z "${DATASTORE_DEVICE}" ]]; then
    final_recommendation="execution_blocked_missing_DEV_or_PBS_DATASTORE_DEVICE"
  elif [[ "${contract_recommendation}" != "ready_for_guarded_pbs_datastore_prepare" ]]; then
    final_recommendation="execution_blocked_contract_not_green"
  elif [[ "${pbs_iso_present}" != "yes" ]]; then
    final_recommendation="execution_blocked_iso_not_staged"
  else
    datastore_prepare_status="$(run_step pbs_datastore_prepare bash -lc "cd ${ROOT_DIR@Q} && DEV=${DATASTORE_DEVICE@Q} ./scripts/proxmox_prepare_pbs_datastore_device.sh ${DATASTORE_DEVICE@Q}")"
    if [[ "${datastore_prepare_status}" == "passed" ]]; then
      vm_reconcile_status="$(run_step pbs_vm240_reconcile bash -lc "cd ${ROOT_DIR@Q} && PBS_VM240_EXECUTE=yes PBS_VM240_ALLOW_DESTROY=yes ./scripts/pbs_vm240_reconcile.sh")"
      if [[ "${vm_reconcile_status}" == "passed" ]]; then
        final_recommendation="complete_pbs_installer_in_vm240_console"
      else
        final_recommendation="vm240_reconcile_failed_review_log"
      fi
    else
      final_recommendation="datastore_prepare_failed_review_log"
    fi
  fi
else
  if [[ "${contract_recommendation}" == "ready_for_guarded_pbs_datastore_prepare" && "${separate_backup_storage_ready}" == "yes" ]]; then
    final_recommendation="ready_for_execute_mode"
  fi
fi

{
  echo "# PBS Guarded Rebuild"
  echo
  echo "- Execute mode: \`${RUN_EXECUTE}\`"
  echo "- Datastore device: \`${DATASTORE_DEVICE:-missing}\`"
  echo "- Audit status: \`${audit_status}\`"
  echo "- Audit recommendation: \`${audit_recommendation:-unknown}\`"
  echo "- Contract check status: \`${contract_status}\`"
  echo "- Contract recommendation: \`${contract_recommendation:-unknown}\`"
  echo "- Runner deploy status: \`${runner_deploy_status}\`"
  echo "- Preflight status: \`${preflight_status}\`"
  echo "- ISO present: \`${pbs_iso_present:-unknown}\`"
  echo "- Separate datastore ready: \`${separate_backup_storage_ready:-unknown}\`"
  echo "- Datastore prepare status: \`${datastore_prepare_status}\`"
  echo "- VM reconcile status: \`${vm_reconcile_status}\`"
  echo "- Final recommendation: \`${final_recommendation}\`"
} > "${REPORT_MD}"

echo "pbs_guarded_rebuild_report=${REPORT_MD}"
echo "pbs_guarded_rebuild_execute_mode=${RUN_EXECUTE}"
echo "pbs_guarded_rebuild_audit_status=${audit_status}"
echo "pbs_guarded_rebuild_audit_recommendation=${audit_recommendation:-unknown}"
echo "pbs_guarded_rebuild_contract_status=${contract_status}"
echo "pbs_guarded_rebuild_contract_recommendation=${contract_recommendation:-unknown}"
echo "pbs_guarded_rebuild_runner_deploy_status=${runner_deploy_status}"
echo "pbs_guarded_rebuild_preflight_status=${preflight_status}"
echo "pbs_guarded_rebuild_iso_present=${pbs_iso_present:-unknown}"
echo "pbs_guarded_rebuild_separate_datastore_ready=${separate_backup_storage_ready:-unknown}"
echo "pbs_guarded_rebuild_datastore_prepare_status=${datastore_prepare_status}"
echo "pbs_guarded_rebuild_vm_reconcile_status=${vm_reconcile_status}"
echo "recommendation=${final_recommendation}"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

yes_no_from_command() {
  if "$@" >/dev/null 2>&1; then
    echo "yes"
  else
    echo "no"
  fi
}

unknown_review_count="$(awk '/zone: unknown-review/{count++} END {print count+0}' "${ROOT_DIR}/ansible/inventory/hosts.yml")"
inventory_finalized="yes"
if [[ "${unknown_review_count}" -gt 0 ]]; then
  inventory_finalized="no"
fi

business_stacks_ready="$(yes_no_from_command "${ROOT_DIR}/scripts/business_service_drift_check.sh")"
toolbox_network_ready="$(yes_no_from_command "${ROOT_DIR}/scripts/toolbox_network_check.sh")"
haos_internal_ready="$(yes_no_from_command "${ROOT_DIR}/scripts/haos_reverse_proxy_check.sh")"

tailscale_check_output="$("${ROOT_DIR}/scripts/toolbox_tailscale_check.sh" 2>/dev/null || true)"
tailscale_backend_state="$(extract_value backend_state "${tailscale_check_output}")"
tailscale_joined="no"
if [[ "${tailscale_backend_state}" == "Running" ]]; then
  tailscale_joined="yes"
fi

backup_restore_proven="no"
if [[ -f "${ROOT_DIR}/BACKUP_RESTORE_PROOF.md" ]] && ssh proxmox "ls /var/lib/vz/dump/vzdump-qemu-200-*.vma.zst /var/lib/vz/dump/vzdump-qemu-210-*.vma.zst /var/lib/vz/dump/vzdump-qemu-220-*.vma.zst /var/lib/vz/dump/vzdump-qemu-230-*.vma.zst >/dev/null 2>&1"; then
  backup_restore_proven="yes"
fi

pbs_preflight_output="$("${ROOT_DIR}/scripts/pbs_preflight_check.sh" 2>/dev/null || true)"
pbs_storage_ready="$(extract_value separate_backup_storage_ready "${pbs_preflight_output}")"
[[ -n "${pbs_storage_ready}" ]] || pbs_storage_ready="no"

maintenance_window_ready="no"
easybox_rollback_ready="yes"
gateway_cutover_ready="no"

if [[ "${business_stacks_ready}" == "yes" \
  && "${toolbox_network_ready}" == "yes" \
  && "${haos_internal_ready}" == "yes" \
  && "${tailscale_joined}" == "yes" \
  && "${backup_restore_proven}" == "yes" \
  && "${inventory_finalized}" == "yes" \
  && "${maintenance_window_ready}" == "yes" ]]; then
  gateway_cutover_ready="yes"
fi

echo "business_stacks_ready=${business_stacks_ready}"
echo "toolbox_network_ready=${toolbox_network_ready}"
echo "haos_internal_ready=${haos_internal_ready}"
echo "tailscale_backend_state=${tailscale_backend_state:-unknown}"
echo "tailscale_joined=${tailscale_joined}"
echo "backup_restore_proven=${backup_restore_proven}"
echo "pbs_storage_ready=${pbs_storage_ready}"
echo "inventory_unknown_review_count=${unknown_review_count}"
echo "inventory_finalized=${inventory_finalized}"
echo "maintenance_window_ready=${maintenance_window_ready}"
echo "easybox_rollback_ready=${easybox_rollback_ready}"
echo "gateway_cutover_ready=${gateway_cutover_ready}"

if [[ "${inventory_finalized}" != "yes" ]]; then
  echo "recommendation=finish_router_lease_reconciliation_and_close_unknown_review_hosts_before_gateway_cutover"
elif [[ "${maintenance_window_ready}" != "yes" ]]; then
  echo "recommendation=schedule_a_dedicated_gateway_maintenance_window_before_cutover"
elif [[ "${backup_restore_proven}" != "yes" ]]; then
  echo "recommendation=prove_backup_and_restore_before_gateway_cutover"
elif [[ "${toolbox_network_ready}" != "yes" || "${haos_internal_ready}" != "yes" ]]; then
  echo "recommendation=stabilize_internal_frontdoor_and_haos_before_gateway_cutover"
else
  echo "recommendation=gateway_cutover_can_be_planned"
fi

#!/usr/bin/env bash
set -euo pipefail

PROXMOX_HOST="${PROXMOX_HOST:-proxmox}"
APPLY="${APPLY:-0}"
SNAPSHOT_PREFIX="${SNAPSHOT_PREFIX:-codex-pre-rightsize}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
SSH_OPTS=(
  -o BatchMode=yes
  -o StrictHostKeyChecking=accept-new
)

TARGETS=(
  "200|nextcloud|2048|http://10.1.0.21/"
  "220|odoo|2048|http://10.1.0.22:8069/web/login"
)

log() {
  printf '[rightsize] %s\n' "$*"
}

remote() {
  ssh "${SSH_OPTS[@]}" "${PROXMOX_HOST}" "$@"
}

wait_for_vm_status() {
  local vmid="$1"
  local expected="$2"
  local attempts="${3:-24}"
  local delay="${4:-5}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    current="$(remote "qm status ${vmid} | awk '/^status:/ {print \$2}'")"
    if [[ "${current}" == "${expected}" ]]; then
      return 0
    fi
    sleep "${delay}"
  done

  return 1
}

wait_for_qga() {
  local vmid="$1"
  local attempts="${2:-24}"
  local delay="${3:-5}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    if remote "qm agent ${vmid} ping" >/dev/null 2>&1; then
      return 0
    fi
    sleep "${delay}"
  done

  return 1
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-24}"
  local delay="${3:-5}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    if curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}' "${url}" | grep -q '^200$'; then
      return 0
    fi
    sleep "${delay}"
  done

  return 1
}

for entry in "${TARGETS[@]}"; do
  IFS='|' read -r vmid name target_memory url <<<"${entry}"
  current_memory="$(remote "qm config ${vmid} | awk -F': ' '/^memory:/ {print \$2}'")"
  echo "vmid=${vmid}"
  echo "name=${name}"
  echo "current_memory_mb=${current_memory}"
  echo "target_memory_mb=${target_memory}"
  echo "verification_url=${url}"

  if [[ "${APPLY}" != "1" ]]; then
    echo "plan_action=snapshot_shutdown_resize_start_verify"
    echo
    continue
  fi

  snapshot_name="${SNAPSHOT_PREFIX}-${vmid}-${TIMESTAMP}"
  log "Creating snapshot ${snapshot_name} for VM ${vmid}"
  remote "qm snapshot ${vmid} ${snapshot_name} --description 'Homeserver 2027 pre-rightsize ${TIMESTAMP}'"

  log "Shutting down VM ${vmid}"
  remote "qm shutdown ${vmid} --timeout 180"
  wait_for_vm_status "${vmid}" "stopped" 36 5

  log "Setting VM ${vmid} memory to ${target_memory} MB"
  remote "qm set ${vmid} --memory ${target_memory}"

  log "Starting VM ${vmid}"
  remote "qm start ${vmid}"
  wait_for_vm_status "${vmid}" "running" 24 5
  wait_for_qga "${vmid}" 24 5

  log "Waiting for verification URL ${url}"
  wait_for_http "${url}" 36 5

  echo "applied_snapshot=${snapshot_name}"
  echo "applied_memory_mb=${target_memory}"
  echo "http_verify=ok"
  echo
done

if [[ "${APPLY}" == "1" ]]; then
  echo "recommendation=run_business_drift_check_and_keep_snapshots_until_post_change_validation_is_complete"
else
  echo "recommendation=review_plan_and_run_with_APPLY=1_in_a_maintenance_window"
fi

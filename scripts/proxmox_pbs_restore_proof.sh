#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROXMOX_HOST="${PROXMOX_HOST:-proxmox}"
RESTORE_STORAGE="${RESTORE_STORAGE:-local-lvm}"
RESTORE_SOURCE_VMID="${RESTORE_SOURCE_VMID:-220}"
RESTORE_TEST_VMID="${RESTORE_TEST_VMID:-920}"
RESTORE_TEST_IP="${RESTORE_TEST_IP:-192.168.2.240}"
RESTORE_TEST_URL="${RESTORE_TEST_URL:-http://${RESTORE_TEST_IP}:8069/web/login}"
SSH_OPTS=(
  -o BatchMode=yes
  -o StrictHostKeyChecking=accept-new
)

log() {
  printf '[pbs-restore-proof] %s\n' "$*"
}

read_pbs_hostvar() {
  local key="$1"
  python3 - <<'PY' "$ROOT_DIR/ansible/inventory/host_vars/pbs.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

BACKUP_STORAGE="${BACKUP_STORAGE:-$(read_pbs_hostvar pbs_proxmox_storage_id)}"

remote() {
  ssh "${SSH_OPTS[@]}" "${PROXMOX_HOST}" "$@"
}

cleanup_restore_vm() {
  if remote "qm status ${RESTORE_TEST_VMID} >/dev/null 2>&1"; then
    log "Cleaning up restore test VM ${RESTORE_TEST_VMID}"
    remote "qm stop ${RESTORE_TEST_VMID} --timeout 60 >/dev/null 2>&1 || true"
    remote "qm destroy ${RESTORE_TEST_VMID} --purge 1 >/dev/null 2>&1 || true"
  fi
}

wait_for_http() {
  local url="$1"
  local attempts="${2:-48}"
  local delay="${3:-5}"
  local i

  for ((i = 1; i <= attempts; i++)); do
    if curl --silent --show-error --fail --location --max-time 10 "$url" >/dev/null; then
      return 0
    fi
    sleep "$delay"
  done

  return 1
}

trap cleanup_restore_vm EXIT

log "Checking PBS backup target and restore test IP availability"
remote "pvesm status | awk '\$1==\"${BACKUP_STORAGE}\" {print}'"
if remote "ping -c 1 -W 1 ${RESTORE_TEST_IP} >/dev/null 2>&1"; then
  echo "Restore test IP ${RESTORE_TEST_IP} is already in use." >&2
  exit 1
fi

cleanup_restore_vm

archive_path="$(
  remote "pvesm list ${BACKUP_STORAGE} | awk '\$1 ~ /^${BACKUP_STORAGE}:backup\\/vm\\/${RESTORE_SOURCE_VMID}\\// {print \$1}' | sort | tail -n 1"
)"
if [[ -z "${archive_path}" ]]; then
  echo "No PBS backup snapshot found for source VM ${RESTORE_SOURCE_VMID} on ${BACKUP_STORAGE}." >&2
  exit 1
fi

log "Restoring ${archive_path} to test VM ${RESTORE_TEST_VMID}"
remote "qmrestore '${archive_path}' ${RESTORE_TEST_VMID} --storage ${RESTORE_STORAGE}"

log "Reconfiguring restored VM ${RESTORE_TEST_VMID} for isolated proof boot"
remote "qm set ${RESTORE_TEST_VMID} --name pbs-restore-test --onboot 0 --ipconfig0 ip=${RESTORE_TEST_IP}/24,gw=192.168.2.1 --net0 virtio,bridge=vmbr0"
remote "qm cloudinit update ${RESTORE_TEST_VMID} >/dev/null 2>&1 || true"

log "Starting restore test VM ${RESTORE_TEST_VMID}"
remote "qm start ${RESTORE_TEST_VMID}"

log "Waiting for service endpoint on ${RESTORE_TEST_URL}"
wait_for_http "${RESTORE_TEST_URL}" 48 5

log "PBS restore proof succeeded"
remote "qm agent ${RESTORE_TEST_VMID} ping >/dev/null 2>&1 && echo qga_ok || echo qga_not_ready"
curl --silent --show-error --fail --location --max-time 10 --write-out 'http_status=%{http_code}\n' --output /dev/null "${RESTORE_TEST_URL}"

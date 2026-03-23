#!/usr/bin/env bash
set -euo pipefail

PROXMOX_HOST="${PROXMOX_HOST:-proxmox}"
BACKUP_STORAGE="${BACKUP_STORAGE:-local}"
RESTORE_STORAGE="${RESTORE_STORAGE:-local-lvm}"
RESTORE_SOURCE_VMID="${RESTORE_SOURCE_VMID:-220}"
RESTORE_TEST_VMID="${RESTORE_TEST_VMID:-920}"
RESTORE_TEST_IP="${RESTORE_TEST_IP:-192.168.2.240}"
RESTORE_TEST_URL="${RESTORE_TEST_URL:-http://${RESTORE_TEST_IP}:8069/web/login}"
BACKUP_VMIDS="${BACKUP_VMIDS:-200 210 220 230}"
SSH_OPTS=(
  -o BatchMode=yes
  -o StrictHostKeyChecking=accept-new
)

log() {
  printf '[backup-proof] %s\n' "$*"
}

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
  local attempts="${2:-36}"
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

log "Checking backup target and restore test IP availability"
remote "pvesm status | awk '\$1==\"${BACKUP_STORAGE}\" {print}'"
if remote "ping -c 1 -W 1 ${RESTORE_TEST_IP} >/dev/null 2>&1"; then
  echo "Restore test IP ${RESTORE_TEST_IP} is already in use." >&2
  exit 1
fi

cleanup_restore_vm

for vmid in ${BACKUP_VMIDS}; do
  log "Creating vzdump backup for VM ${vmid} on storage ${BACKUP_STORAGE}"
  remote "vzdump ${vmid} --mode snapshot --compress zstd --storage ${BACKUP_STORAGE} --remove 0"
done

log "Latest backup archives"
for vmid in ${BACKUP_VMIDS}; do
  remote "ls -1t /var/lib/vz/dump/vzdump-qemu-${vmid}-*.vma.zst | head -n 1"
done

archive_path="$(remote "ls -1t /var/lib/vz/dump/vzdump-qemu-${RESTORE_SOURCE_VMID}-*.vma.zst | head -n 1")"
if [[ -z "${archive_path}" ]]; then
  echo "No backup archive found for source VM ${RESTORE_SOURCE_VMID}." >&2
  exit 1
fi

log "Restoring ${archive_path} to test VM ${RESTORE_TEST_VMID}"
remote "qmrestore '${archive_path}' ${RESTORE_TEST_VMID} --storage ${RESTORE_STORAGE}"

log "Reconfiguring restored VM ${RESTORE_TEST_VMID} for isolated proof boot"
remote "qm set ${RESTORE_TEST_VMID} --name odoo-restore-test --onboot 0 --ipconfig0 ip=${RESTORE_TEST_IP}/24,gw=192.168.2.1 --net0 virtio,bridge=vmbr0"
remote "qm cloudinit update ${RESTORE_TEST_VMID} >/dev/null 2>&1 || true"

log "Starting restore test VM ${RESTORE_TEST_VMID}"
remote "qm start ${RESTORE_TEST_VMID}"

log "Waiting for Odoo login page on ${RESTORE_TEST_URL}"
wait_for_http "${RESTORE_TEST_URL}" 48 5

log "Restore proof succeeded"
remote "qm agent ${RESTORE_TEST_VMID} ping >/dev/null 2>&1 && echo qga_ok || echo qga_not_ready"
curl --silent --show-error --fail --location --max-time 10 --write-out 'http_status=%{http_code}\n' --output /dev/null "${RESTORE_TEST_URL}"

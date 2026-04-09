#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

log() {
  printf '[proxmox-backup-check] %s\n' "$*"
}

log "Checking systemd timer and service"
run_proxmox_remote "systemctl is-enabled homeserver2027-local-business-backup.timer"
echo
run_proxmox_remote "systemctl is-active homeserver2027-local-business-backup.timer"
echo
run_proxmox_remote "systemctl status --no-pager homeserver2027-local-business-backup.timer | sed -n '1,20p'"
run_proxmox_remote "systemctl status --no-pager homeserver2027-local-business-backup.service | sed -n '1,20p' || true"

log "Checking current local archives"
run_proxmox_remote "ls -lah /var/lib/vz/dump/vzdump-qemu-*.vma.zst 2>/dev/null || echo no_qemu_archives"
echo

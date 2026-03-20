#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[proxmox-backup-check] %s\n' "$*"
}

log "Checking systemd timer and service"
ssh proxmox "systemctl is-enabled homeserver2027-local-business-backup.timer"
ssh proxmox "systemctl is-active homeserver2027-local-business-backup.timer"
ssh proxmox "systemctl status --no-pager homeserver2027-local-business-backup.timer | sed -n '1,20p'"
ssh proxmox "systemctl status --no-pager homeserver2027-local-business-backup.service | sed -n '1,20p' || true"

log "Checking current local archives"
ssh proxmox "ls -lah /var/lib/vz/dump/vzdump-qemu-*.vma.zst 2>/dev/null || echo no_qemu_archives"

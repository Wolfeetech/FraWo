#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

if run_proxmox_remote "blkid -L HS27_PORTABLEBK >/dev/null 2>&1"; then
  echo "[portable-backup-run] Prepared USB already present, skipping destructive prepare"
else
  "${ROOT_DIR}/scripts/proxmox_portable_backup_usb_autoprepare.sh" "${1:-}"
fi

"${ROOT_DIR}/scripts/proxmox_portable_backup_usb_fill.sh"
"${ROOT_DIR}/scripts/proxmox_portable_backup_usb_check.sh"

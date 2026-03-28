#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

remote_cmd="$(cat <<'EOF'
set -euo pipefail

MOUNT_PATH="/srv/portable-backup-usb"

mount_state="missing"
if mountpoint -q "${MOUNT_PATH}"; then
  mount_state="mounted"
fi

echo "portable_backup_usb_mount_state=${mount_state}"

if [[ "${mount_state}" == "mounted" ]]; then
  df_output="$(df -B1 "${MOUNT_PATH}" | awk 'NR==2 {print $2" "$3" "$4}')"
  read -r total used free <<<"${df_output}"
  echo "portable_backup_usb_total_bytes=${total}"
  echo "portable_backup_usb_used_bytes=${used}"
  echo "portable_backup_usb_free_bytes=${free}"
  echo "portable_backup_usb_archive_count=$(find "${MOUNT_PATH}/archives" -type f -name 'vzdump-qemu-*.vma.zst' 2>/dev/null | wc -l | awk '{print $1}')"
else
  echo "portable_backup_usb_total_bytes=0"
  echo "portable_backup_usb_used_bytes=0"
  echo "portable_backup_usb_free_bytes=0"
  echo "portable_backup_usb_archive_count=0"
fi

if [[ "${mount_state}" == "mounted" ]]; then
  echo "recommendation=portable_backup_usb_ready_for_archive_fill_or_offhost_storage"
else
  echo "recommendation=attach_and_prepare_portable_backup_usb_on_proxmox"
fi
EOF
)"

run_proxmox_remote "${remote_cmd}"

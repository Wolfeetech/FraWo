#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /dev/sdX" >&2
  exit 1
fi

DEVICE="$1"
LABEL="HS27_PORTABLEBK"
MOUNT_PATH="/srv/portable-backup-usb"

remote_cmd="$(cat <<EOF
set -euo pipefail

DEVICE="${DEVICE}"
PARTITION="\${DEVICE}1"
LABEL="${LABEL}"
MOUNT_PATH="${MOUNT_PATH}"

if [[ ! -b "\${DEVICE}" ]]; then
  echo "Portable backup USB device \${DEVICE} not found" >&2
  exit 1
fi

echo "[portable-backup-prepare] Destructive prepare target=\${DEVICE}"
umount "\${DEVICE}"* >/dev/null 2>&1 || true
wipefs -a "\${DEVICE}"
printf 'label: gpt\n,;\n' | sfdisk "\${DEVICE}"
blockdev --rereadpt "\${DEVICE}" || true
udevadm settle
mkfs.ext4 -F -L "\${LABEL}" "\${PARTITION}"
mkdir -p "\${MOUNT_PATH}"
mount "\${PARTITION}" "\${MOUNT_PATH}"
install -d -m 0755 "\${MOUNT_PATH}/archives" "\${MOUNT_PATH}/manifests"
cat > "\${MOUNT_PATH}/README.txt" <<TXT
Homeserver 2027 portable backup USB

Purpose:
- interim off-host shuttle for local Proxmox vzdump archives
- not a replacement for the planned PBS datastore

Prepared:
- label: \${LABEL}
- mount: \${MOUNT_PATH}
TXT
df -h "\${MOUNT_PATH}"
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT "\${DEVICE}"
EOF
)"

run_proxmox_remote "${remote_cmd}"

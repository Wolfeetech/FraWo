#!/usr/bin/env bash
set -euo pipefail

ssh proxmox "bash -s" <<'EOF'
set -euo pipefail

LABEL="HS27_PORTABLEBK"
USB_MOUNT="/srv/portable-backup-usb"
PBS_MOUNT="/srv/pbs-datastore"
STORAGE_ID="pbs-usb"

device="$(blkid -L "${LABEL}" || true)"
if [[ -z "${device}" ]]; then
  echo "Portable PBS USB with label ${LABEL} not found" >&2
  exit 1
fi

mkdir -p "${USB_MOUNT}" "${PBS_MOUNT}"

if ! mountpoint -q "${USB_MOUNT}"; then
  mount "${device}" "${USB_MOUNT}"
fi

pkill -f '/srv/portable-backup-usb/manifests/selection.txt' >/dev/null 2>&1 || true

if mountpoint -q "${PBS_MOUNT}"; then
  umount "${PBS_MOUNT}" >/dev/null 2>&1 || true
fi
mount --bind "${USB_MOUNT}" "${PBS_MOUNT}"

uuid="$(blkid -s UUID -o value "${device}")"

grep -q " ${USB_MOUNT} ext4 " /etc/fstab || \
  echo "UUID=${uuid} ${USB_MOUNT} ext4 defaults,nofail 0 2" >> /etc/fstab
grep -q " ${PBS_MOUNT} none bind,nofail " /etc/fstab || \
  echo "${USB_MOUNT} ${PBS_MOUNT} none bind,nofail 0 0" >> /etc/fstab

if pvesm status --storage "${STORAGE_ID}" >/dev/null 2>&1; then
  :
else
  pvesm add dir "${STORAGE_ID}" --path "${PBS_MOUNT}" --content images,backup
fi

echo "pbs_usb_device=${device}"
findmnt -rn "${USB_MOUNT}"
findmnt -rn "${PBS_MOUNT}"
df -h "${PBS_MOUNT}"
pvesm status --storage "${STORAGE_ID}"
EOF

#!/usr/bin/env bash
set -euo pipefail

resolve_operator_home() {
  if [[ -n "${SUDO_USER:-}" && "${SUDO_USER}" != "root" ]]; then
    getent passwd "${SUDO_USER}" | cut -d: -f6
  elif [[ -n "${HOME:-}" ]]; then
    printf '%s\n' "${HOME}"
  else
    getent passwd "$(id -un)" | cut -d: -f6
  fi
}

TARGET_DEV="${1:-/dev/sdd}"
OPERATOR_HOME="$(resolve_operator_home)"
BASE_DIR="${OPERATOR_HOME}/Downloads/Homeserver2027/install-media"
VENTOY_VERSION="1.1.10"
VENTOY_ARCHIVE="${BASE_DIR}/tools/ventoy-${VENTOY_VERSION}-linux.tar.gz"
VENTOY_DIR="${BASE_DIR}/tools/ventoy-${VENTOY_VERSION}"
SURFACE_ISO="${BASE_DIR}/surface/ubuntu-24.04.4-desktop-amd64.iso"
MOUNT_DIR="/mnt/homeserver2027-ventoy"
VENTOY_SHIM_DIR=""

cleanup() {
  umount "${MOUNT_DIR}" 2>/dev/null || true
  if [[ -n "${VENTOY_SHIM_DIR}" && -d "${VENTOY_SHIM_DIR}" ]]; then
    rm -rf "${VENTOY_SHIM_DIR}"
  fi
}

trap cleanup EXIT

if [[ "${EUID}" -ne 0 ]]; then
  echo "AKTION VON DIR ERFORDERLICH: dieses Script mit sudo ausfuehren." >&2
  echo "Beispiel: sudo $0 ${TARGET_DEV}" >&2
  exit 2
fi

if [[ ! -b "${TARGET_DEV}" ]]; then
  echo "Target device not found: ${TARGET_DEV}" >&2
  exit 1
fi

if [[ ! -f "${VENTOY_ARCHIVE}" || ! -f "${SURFACE_ISO}" ]]; then
  echo "Missing download artifacts. Run ./scripts/fetch_install_media.sh first." >&2
  exit 1
fi

if ! command -v mkexfatfs >/dev/null 2>&1; then
  if command -v mkfs.exfat >/dev/null 2>&1; then
    VENTOY_SHIM_DIR="$(mktemp -d)"
    ln -sf "$(command -v mkfs.exfat)" "${VENTOY_SHIM_DIR}/mkexfatfs"
    export PATH="${VENTOY_SHIM_DIR}:${PATH}"
    echo "[surface-usb] Added temporary mkexfatfs shim -> $(command -v mkfs.exfat)"
  else
    echo "Neither mkexfatfs nor mkfs.exfat is available." >&2
    exit 1
  fi
fi

echo "[surface-usb] Destructive write target=${TARGET_DEV}"
echo "[surface-usb] Replacing current contents with Ventoy and copying Surface ISO"

mkdir -p "${BASE_DIR}/tools"
tar -xf "${VENTOY_ARCHIVE}" -C "${BASE_DIR}/tools"

if [[ ! -x "${VENTOY_DIR}/Ventoy2Disk.sh" ]]; then
  echo "Ventoy2Disk.sh not found in ${VENTOY_DIR}" >&2
  exit 1
fi

for part in $(lsblk -nrpo PATH "${TARGET_DEV}" | tail -n +2); do
  umount "${part}" 2>/dev/null || true
done

(
  cd "${VENTOY_DIR}"
  printf 'y\ny\n' | ./Ventoy2Disk.sh -I "${TARGET_DEV}"
)
partprobe "${TARGET_DEV}" 2>/dev/null || true
udevadm settle 2>/dev/null || true
sleep 5

mkdir -p "${MOUNT_DIR}"
if ! lsblk -nrpo PATH,FSTYPE "${TARGET_DEV}" | awk '$1 ~ /1$/ && $2 == "exfat" {found=1} END {exit(found ? 0 : 1)}'; then
  echo "Ventoy did not create the expected exFAT first partition on ${TARGET_DEV}" >&2
  exit 1
fi
mount -t exfat "${TARGET_DEV}1" "${MOUNT_DIR}"
cp -f "${SURFACE_ISO}" "${MOUNT_DIR}/"
sync
umount "${MOUNT_DIR}"
rmdir "${MOUNT_DIR}" 2>/dev/null || true

echo "[surface-usb] Completed"
echo "target_device=${TARGET_DEV}"
echo "surface_iso_copied=$(basename "${SURFACE_ISO}")"

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

TARGET_DEV="${1:-/dev/mmcblk0}"
OPERATOR_HOME="$(resolve_operator_home)"
BASE_DIR="${OPERATOR_HOME}/Downloads/Homeserver2027/install-media"
RPI_IMG="${BASE_DIR}/rpi/ubuntu-22.04.5-preinstalled-server-arm64+raspi.img.xz"

if [[ "${EUID}" -ne 0 ]]; then
  echo "AKTION VON DIR ERFORDERLICH: dieses Script mit sudo ausfuehren." >&2
  echo "Beispiel: sudo $0 ${TARGET_DEV}" >&2
  exit 2
fi

if [[ ! -b "${TARGET_DEV}" ]]; then
  echo "Target device not found: ${TARGET_DEV}" >&2
  exit 1
fi

if [[ ! -f "${RPI_IMG}" ]]; then
  echo "Missing Raspberry Pi image. Run ./scripts/fetch_install_media.sh first." >&2
  exit 1
fi

echo "[flash-rpi-sd] Destructive write target=${TARGET_DEV}"
echo "[flash-rpi-sd] Writing $(basename "${RPI_IMG}")"

for part in $(lsblk -nrpo PATH "${TARGET_DEV}" | tail -n +2); do
  umount "${part}" 2>/dev/null || true
done

xzcat "${RPI_IMG}" | dd of="${TARGET_DEV}" bs=4M conv=fsync status=progress
sync

echo "[flash-rpi-sd] Completed"
echo "target_device=${TARGET_DEV}"
echo "image=$(basename "${RPI_IMG}")"

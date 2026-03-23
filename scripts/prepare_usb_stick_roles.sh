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

IMAGE_STICK="${1:-/dev/sdd}"
FAVORITES_STICK="${2:-/dev/sdc}"
OPERATOR_HOME="$(resolve_operator_home)"
BASE_DIR="${OPERATOR_HOME}/Downloads/Homeserver2027/install-media"
MOUNT_DIR="/mnt/homeserver2027-favorites"
FAVORITES_LABEL="FRAWO_FAVS"

if [[ "${EUID}" -ne 0 ]]; then
  echo "AKTION VON DIR ERFORDERLICH: dieses Script mit sudo ausfuehren." >&2
  echo "Beispiel: sudo $0 ${IMAGE_STICK} ${FAVORITES_STICK}" >&2
  exit 2
fi

if [[ "${IMAGE_STICK}" == "${FAVORITES_STICK}" ]]; then
  echo "Image- und Favorites-Stick duerfen nicht dasselbe Device sein." >&2
  exit 1
fi

for dev in "${IMAGE_STICK}" "${FAVORITES_STICK}"; do
  if [[ ! -b "${dev}" ]]; then
    echo "Target device not found: ${dev}" >&2
    exit 1
  fi
done

if [[ ! -f "${BASE_DIR}/surface/ubuntu-24.04.4-desktop-amd64.iso" ]]; then
  echo "Surface ISO fehlt unter ${BASE_DIR}/surface/ubuntu-24.04.4-desktop-amd64.iso" >&2
  exit 1
fi

if ! command -v mkfs.exfat >/dev/null 2>&1; then
  echo "mkfs.exfat ist nicht installiert." >&2
  exit 1
fi

if ! command -v parted >/dev/null 2>&1; then
  echo "parted ist nicht installiert." >&2
  exit 1
fi

echo "[usb-roles] Destructive write image_stick=${IMAGE_STICK} favorites_stick=${FAVORITES_STICK}"
echo "[usb-roles] Step 1/2: image stick -> Ventoy + Surface ISO"
"$(dirname "$0")/prepare_surface_usb_ventoy.sh" "${IMAGE_STICK}"

echo "[usb-roles] Step 2/2: favorites stick -> exFAT mobile favorites layout"
for part in $(lsblk -nrpo PATH "${FAVORITES_STICK}" | tail -n +2); do
  umount "${part}" 2>/dev/null || true
done

wipefs -a "${FAVORITES_STICK}"
parted -s "${FAVORITES_STICK}" mklabel gpt
parted -s "${FAVORITES_STICK}" mkpart primary 1MiB 100%
partprobe "${FAVORITES_STICK}"
sleep 2

FAVORITES_PART="${FAVORITES_STICK}1"
if [[ ! -b "${FAVORITES_PART}" ]]; then
  echo "Favorites partition was not created on ${FAVORITES_STICK}" >&2
  exit 1
fi

mkfs.exfat -n "${FAVORITES_LABEL}" "${FAVORITES_PART}"

mkdir -p "${MOUNT_DIR}"
mount "${FAVORITES_PART}" "${MOUNT_DIR}"
mkdir -p "${MOUNT_DIR}/Favorites" "${MOUNT_DIR}/Playlists" "${MOUNT_DIR}/To_Radio" "${MOUNT_DIR}/Archive"
cat >"${MOUNT_DIR}/README_FRAWO_FAVORITES.txt" <<'EOF'
FRAWO Favorites Stick

Rolle:
- mobiler Favoriten-Stick
- persoenliche oder kuratierte Lieblings-Tracks
- kein Boot- oder Installationsmedium

Ordner:
- Favorites: mobile Lieblingsmusik
- Playlists: exportierte oder manuelle Playlist-Dateien
- To_Radio: spaetere Uebergaben an den Radio-/Medienpfad
- Archive: alte oder ausgemusterte Stuecke

Hinweis:
- Der Install-/Image-Stick ist der blaue 8GB-Stick mit Ventoy.
- Die temporaere Gesamt-Musikbibliothek liegt aktuell auf dem USB-Medium am Raspberry Pi.
EOF
sync
umount "${MOUNT_DIR}"
rmdir "${MOUNT_DIR}" 2>/dev/null || true

echo "[usb-roles] Completed"
echo "image_stick=${IMAGE_STICK}"
echo "favorites_stick=${FAVORITES_STICK}"
echo "favorites_label=${FAVORITES_LABEL}"

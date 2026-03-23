#!/usr/bin/env bash
set -euo pipefail

TARGET_DEV="${1:-/dev/sdc}"
MOUNT_DIR="/mnt/homeserver2027-favorites"
FAVORITES_LABEL="FRAWO_FAVS"

cleanup() {
  umount "${MOUNT_DIR}" 2>/dev/null || true
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

if ! command -v mkfs.exfat >/dev/null 2>&1; then
  echo "mkfs.exfat ist nicht installiert." >&2
  exit 1
fi

if ! command -v parted >/dev/null 2>&1; then
  echo "parted ist nicht installiert." >&2
  exit 1
fi

echo "[favorites-usb] Destructive write target=${TARGET_DEV}"
echo "[favorites-usb] Replacing current contents with FRAWO favorites layout"

for part in $(lsblk -nrpo PATH "${TARGET_DEV}" | tail -n +2); do
  umount "${part}" 2>/dev/null || true
done

wipefs -a "${TARGET_DEV}"
parted -s "${TARGET_DEV}" mklabel gpt
parted -s "${TARGET_DEV}" mkpart primary 1MiB 100%
partprobe "${TARGET_DEV}"
udevadm settle 2>/dev/null || true
sleep 2

TARGET_PART="${TARGET_DEV}1"
if [[ ! -b "${TARGET_PART}" ]]; then
  echo "Favorites partition was not created on ${TARGET_DEV}" >&2
  exit 1
fi

mkfs.exfat -n "${FAVORITES_LABEL}" "${TARGET_PART}"

mkdir -p "${MOUNT_DIR}"
mount "${TARGET_PART}" "${MOUNT_DIR}"
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

echo "[favorites-usb] Completed"
echo "target_device=${TARGET_DEV}"
echo "favorites_label=${FAVORITES_LABEL}"

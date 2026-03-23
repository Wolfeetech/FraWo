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

partition_path() {
  local dev="$1"
  local number="$2"
  if [[ "${dev}" =~ [0-9]$ ]]; then
    printf '%sp%s\n' "${dev}" "${number}"
  else
    printf '%s%s\n' "${dev}" "${number}"
  fi
}

TARGET_DEV="${1:-/dev/mmcblk0}"
TARGET_HOSTNAME="radio-node"
TARGET_ADMIN_USER="wolf"
TARGET_TIMEZONE="Europe/Zurich"
OPERATOR_HOME="$(resolve_operator_home)"
PUBKEY_FILE="${OPERATOR_HOME}/.ssh/id_ed25519.pub"
BOOT_PART="$(partition_path "${TARGET_DEV}" 1)"
MOUNT_DIR="/mnt/homeserver2027-rpi-boot"
MOUNTED_TARGET=""
NEEDS_UMOUNT="no"

if [[ ! -b "${TARGET_DEV}" ]]; then
  echo "Target device not found: ${TARGET_DEV}" >&2
  exit 1
fi

if [[ ! -b "${BOOT_PART}" ]]; then
  echo "Boot partition not found: ${BOOT_PART}" >&2
  echo "Flash the Ubuntu Pi image first, then run this script." >&2
  exit 1
fi

if [[ ! -f "${PUBKEY_FILE}" ]]; then
  echo "Missing operator SSH public key: ${PUBKEY_FILE}" >&2
  exit 1
fi

PUBKEY_CONTENT="$(tr -d '\n' < "${PUBKEY_FILE}")"

MOUNTED_TARGET="$(findmnt -nr -o TARGET "${BOOT_PART}" 2>/dev/null || true)"

if [[ -n "${MOUNTED_TARGET}" && -w "${MOUNTED_TARGET}" ]]; then
  MOUNT_DIR="${MOUNTED_TARGET}"
else
  if [[ "${EUID}" -ne 0 ]]; then
    echo "AKTION VON DIR ERFORDERLICH: entweder die Boot-Partition zuerst schreibbar mounten oder das Script mit sudo ausfuehren." >&2
    echo "Beispiel mit sudo: sudo $0 ${TARGET_DEV}" >&2
    exit 2
  fi
  mkdir -p "${MOUNT_DIR}"
  mount "${BOOT_PART}" "${MOUNT_DIR}"
  NEEDS_UMOUNT="yes"
fi

trap 'if [[ "${NEEDS_UMOUNT}" == "yes" ]]; then umount "${MOUNT_DIR}" 2>/dev/null || true; fi' EXIT

for file in user-data network-config meta-data; do
  if [[ -f "${MOUNT_DIR}/${file}" && ! -f "${MOUNT_DIR}/${file}.orig" ]]; then
    cp "${MOUNT_DIR}/${file}" "${MOUNT_DIR}/${file}.orig"
  fi
done

cat > "${MOUNT_DIR}/user-data" <<EOF
#cloud-config
hostname: ${TARGET_HOSTNAME}
manage_etc_hosts: true
timezone: ${TARGET_TIMEZONE}
package_update: true
package_upgrade: true
packages:
  - openssh-server
  - curl
  - ca-certificates
  - unattended-upgrades
  - avahi-daemon
  - jq
users:
  - default
  - name: ${TARGET_ADMIN_USER}
    gecos: Homeserver 2027 Admin
    shell: /bin/bash
    groups:
      - adm
      - sudo
      - audio
      - video
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: true
    ssh_authorized_keys:
      - ${PUBKEY_CONTENT}
ssh_pwauth: false
disable_root: true
write_files:
  - path: /etc/motd
    owner: root:root
    permissions: '0644'
    content: |
      Homeserver 2027
      Raspberry Pi radio-node first boot
runcmd:
  - systemctl enable ssh
  - systemctl enable unattended-upgrades
  - systemctl enable avahi-daemon
EOF

cat > "${MOUNT_DIR}/network-config" <<EOF
version: 2
ethernets:
  eth0:
    dhcp4: true
    dhcp6: true
EOF

cat > "${MOUNT_DIR}/meta-data" <<EOF
instance-id: homeserver2027-radio-node
local-hostname: ${TARGET_HOSTNAME}
EOF

sync

echo "[rpi-seed] Completed"
echo "target_device=${TARGET_DEV}"
echo "boot_partition=${BOOT_PART}"
echo "hostname=${TARGET_HOSTNAME}"
echo "admin_user=${TARGET_ADMIN_USER}"
echo "pubkey_file=${PUBKEY_FILE}"

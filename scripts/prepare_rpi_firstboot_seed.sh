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

# Trusted Keys
KEY_STUDIOPC="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBcv7XLA8U9AFBTIATce451pNyO/WdmBYTmjqA4qzsOX studiopc@wolfstudioPC"
KEY_SURFACE="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAILjI7rqUniSmuSxs7G0eVq6iD6WaebDfNxZDWVtkbDeH Admin@Surface-Work"
KEY_SURFACE_2026="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAID6B6djoKYcD5MXnynkcXIjgZncm3E4Y6o0vg2nFP/bA wolf@wolf-surface-2026"

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
package_upgrade: false
packages:
  - openssh-server
  - curl
  - ca-certificates
  - unattended-upgrades
  - avahi-daemon
  - jq
  - tailscale
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
      - docker
    sudo: ALL=(ALL) NOPASSWD:ALL
    lock_passwd: false
    passwd: "11011995"
    ssh_authorized_keys:
      - ${KEY_STUDIOPC}
      - ${KEY_SURFACE}
      - ${KEY_SURFACE_2026}
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
  - systemctl enable tailscaled
  - tailscale up --authkey=tskey-auth-kkWC2C1Xmq11CNTRL-Z51zhJ7YZMcGq4555QEdLct4UjvUYkbyi --hostname=${TARGET_HOSTNAME} --accept-routes --ssh
EOF

cat > "${MOUNT_DIR}/network-config" <<EOF
version: 2
ethernets:
  eth0:
    dhcp4: true
    dhcp6: true
  wifis:
    wlan0:
      dhcp4: true
      dhcp6: true
      access-points:
        "EasyBox-WLAN":
          password: "11011995"
EOF

cat > "${MOUNT_DIR}/meta-data" <<EOF
instance-id: radio-node-v7
local-hostname: ${TARGET_HOSTNAME}
EOF

sync

echo "[rpi-seed] Completed"
echo "target_device=${TARGET_DEV}"
echo "boot_partition=${BOOT_PART}"
echo "hostname=${TARGET_HOSTNAME}"
echo "admin_user=${TARGET_ADMIN_USER}"
echo "keys_added=StudioPC, Surface, Surface-2026"

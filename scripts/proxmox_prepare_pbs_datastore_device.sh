#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /dev/sdX" >&2
  exit 64
fi

DEVICE="$1"
CONTRACT_FILE="${PBS_REBUILD_CONTRACT_FILE:-${ROOT_DIR}/manifests/pbs_rebuild/device_contract.json}"
DATASTORE_LABEL="${PBS_DATASTORE_LABEL:-HS27_PBS_DATA}"

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "${ROOT_DIR}/ansible/inventory/host_vars/proxmox.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

if [[ ! -f "${CONTRACT_FILE}" ]]; then
  echo "PBS rebuild contract file not found: ${CONTRACT_FILE}" >&2
  exit 1
fi

eval "$(
  python3 - <<'PY' "${CONTRACT_FILE}"
import json
import shlex
import sys

contract = json.load(open(sys.argv[1], "r", encoding="utf-8"))

boot_usb = contract.get("boot_usb", {})
datastore = contract.get("datastore_device", {})

values = {
    "BOOT_SERIAL": str(boot_usb.get("serial") or "").strip(),
    "DATASTORE_SERIAL": str(datastore.get("serial") or "").strip(),
    "DATASTORE_ALLOW_DESTROY": "yes" if datastore.get("allow_destroy") else "no",
    "DATASTORE_ALLOW_REFORMAT": "yes" if datastore.get("allow_reformat_existing_filesystem") else "no",
    "APPROVED_BY": str(contract.get("approved_by") or "").strip(),
    "APPROVED_AT": str(contract.get("approved_at") or "").strip(),
}

for key, value in values.items():
    print(f"{key}={shlex.quote(value)}")
PY
)"

if [[ -z "${DATASTORE_SERIAL}" || -z "${APPROVED_BY}" || -z "${APPROVED_AT}" ]]; then
  echo "PBS datastore prepare blocked: contract approval metadata or datastore serial is missing." >&2
  exit 1
fi

if [[ "${DATASTORE_ALLOW_DESTROY}" != "yes" ]]; then
  echo "PBS datastore prepare blocked: destructive approval is false in ${CONTRACT_FILE}." >&2
  exit 1
fi

DATASTORE_MOUNT_PATH="$(read_hostvar proxmox_pbs_datastore_mount_path)"
STORAGE_ID="$(read_hostvar proxmox_pbs_data_storage_id)"

remote_cmd="$(cat <<EOF
set -euo pipefail

DEVICE="${DEVICE}"
EXPECTED_SERIAL="${DATASTORE_SERIAL}"
BOOT_SERIAL="${BOOT_SERIAL}"
ALLOW_REFORMAT="${DATASTORE_ALLOW_REFORMAT}"
LABEL="${DATASTORE_LABEL}"
MOUNT_PATH="${DATASTORE_MOUNT_PATH}"
STORAGE_ID="${STORAGE_ID}"

if [[ ! -b "\${DEVICE}" ]]; then
  echo "PBS datastore device \${DEVICE} not found" >&2
  exit 1
fi

device_serial="\$(lsblk -dn -o SERIAL "\${DEVICE}" | xargs)"
if [[ -z "\${device_serial}" ]]; then
  echo "PBS datastore device \${DEVICE} has no readable serial" >&2
  exit 1
fi
if [[ "\${device_serial}" != "\${EXPECTED_SERIAL}" ]]; then
  echo "PBS datastore serial mismatch: expected \${EXPECTED_SERIAL}, got \${device_serial}" >&2
  exit 1
fi
if [[ -n "\${BOOT_SERIAL}" && "\${device_serial}" == "\${BOOT_SERIAL}" ]]; then
  echo "PBS datastore device matches the approved boot USB serial; role separation violated" >&2
  exit 1
fi

size_bytes="\$(lsblk -dn -b -o SIZE "\${DEVICE}" | tr -d ' ')"
if [[ -z "\${size_bytes}" || "\${size_bytes}" == "0" ]]; then
  echo "PBS datastore device \${DEVICE} reports zero capacity" >&2
  exit 1
fi

current_fstype="\$(lsblk -dn -o FSTYPE "\${DEVICE}" | xargs)"
if [[ -n "\${current_fstype}" && "\${ALLOW_REFORMAT}" != "yes" ]]; then
  echo "PBS datastore device \${DEVICE} already has filesystem \${current_fstype}, but reformat is not approved" >&2
  exit 1
fi

echo "[pbs-datastore-prepare] Destructive prepare target=\${DEVICE} serial=\${device_serial} mount=\${MOUNT_PATH}"
umount "\${DEVICE}"* >/dev/null 2>&1 || true
wipefs -a "\${DEVICE}"
printf 'label: gpt\n,;\n' | sfdisk "\${DEVICE}"
blockdev --rereadpt "\${DEVICE}" || true
udevadm settle
mkfs.ext4 -F -L "\${LABEL}" "\${DEVICE}1"
mkdir -p "\${MOUNT_PATH}"
uuid="\$(blkid -s UUID -o value "\${DEVICE}1")"
sed -i "\\# \${MOUNT_PATH} #d" /etc/fstab
printf 'UUID=%s %s ext4 defaults,nofail 0 2\n' "\${uuid}" "\${MOUNT_PATH}" >> /etc/fstab
mount "\${MOUNT_PATH}"

if pvesm status --storage "\${STORAGE_ID}" >/dev/null 2>&1; then
  pvesm set "\${STORAGE_ID}" --path "\${MOUNT_PATH}" --content images,backup --disable 0 --is_mountpoint yes
else
  pvesm add dir "\${STORAGE_ID}" --path "\${MOUNT_PATH}" --content images,backup --is_mountpoint yes
fi

findmnt -rn "\${MOUNT_PATH}"
df -h "\${MOUNT_PATH}"
lsblk -o NAME,SIZE,FSTYPE,LABEL,MOUNTPOINT,SERIAL "\${DEVICE}"
pvesm status --storage "\${STORAGE_ID}"
EOF
)"

run_proxmox_remote "${remote_cmd}"

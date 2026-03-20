#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "$ROOT_DIR/ansible/inventory/host_vars/proxmox.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

log() {
  printf '[pbs-iso-stage] %s\n' "$*"
}

ISO_DIR="$(read_hostvar proxmox_pbs_iso_dir)"
ISO_FILE="$(read_hostvar proxmox_pbs_iso_file)"
ISO_SOURCE_FILE="$(read_hostvar proxmox_pbs_iso_source_file)"
ISO_URL="$(read_hostvar proxmox_pbs_iso_url)"
ISO_SHA256="$(read_hostvar proxmox_pbs_iso_sha256)"

remote_cmd=$(cat <<EOF
set -euo pipefail
mkdir -p ${ISO_DIR@Q}
cd ${ISO_DIR@Q}
if [[ -f ${ISO_SOURCE_FILE@Q} ]]; then
  echo source_present
else
  curl -fL ${ISO_URL@Q} -o ${ISO_SOURCE_FILE@Q}
fi
echo "${ISO_SHA256}  ${ISO_SOURCE_FILE}" | sha256sum -c -
cp -f ${ISO_SOURCE_FILE@Q} ${ISO_FILE@Q}
sha256sum ${ISO_FILE@Q}
EOF
)

log "Staging official PBS ISO on Proxmox"
ssh proxmox "$remote_cmd"

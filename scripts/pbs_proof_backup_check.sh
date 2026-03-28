#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "$ROOT_DIR/ansible/inventory/host_vars/pbs.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

PBS_HOST="$(python3 - <<'PY' "$ROOT_DIR/ansible/inventory/hosts.yml"
import sys, yaml
with open(sys.argv[1], 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data["all"]["children"]["management"]["hosts"]["pbs"]["ansible_host"])
PY
)"

PBS_DATASTORE_MOUNTPOINT="$(read_hostvar pbs_datastore_mountpoint)"
PBS_DATASTORE_NAME="$(read_hostvar pbs_datastore_name)"
PBS_PROXMOX_STORAGE_ID="$(read_hostvar pbs_proxmox_storage_id)"

pbs_storage_active="no"
if run_proxmox_remote "pvesm status | awk '\$1 == \"${PBS_PROXMOX_STORAGE_ID}\" && \$2 == \"pbs\" && \$3 == \"active\" {found=1} END {exit(found ? 0 : 1)}'" >/dev/null 2>&1; then
  pbs_storage_active="yes"
fi

snapshot_path="$(
  run_inventory_remote "pbs" "find ${PBS_DATASTORE_MOUNTPOINT@Q}/vm/220 -mindepth 1 -maxdepth 1 -type d 2>/dev/null | sort | tail -n 1" "root" 2>/dev/null || true
)"

proof_backup_exists="no"
snapshot_name="none"
snapshot_index_present="no"
snapshot_fidx_present="no"

if [[ -n "${snapshot_path}" ]]; then
  snapshot_name="$(basename "${snapshot_path}")"
  if run_inventory_remote "pbs" "test -f ${snapshot_path@Q}/index.json.blob" "root"; then
    snapshot_index_present="yes"
  fi
  if run_inventory_remote "pbs" "find ${snapshot_path@Q} -maxdepth 1 -name '*.fidx' | grep -q ." "root"; then
    snapshot_fidx_present="yes"
  fi
  if [[ "${snapshot_index_present}" == "yes" && "${snapshot_fidx_present}" == "yes" ]]; then
    proof_backup_exists="yes"
  fi
fi

echo "pbs_storage_active=${pbs_storage_active}"
echo "pbs_proxmox_storage_id=${PBS_PROXMOX_STORAGE_ID}"
echo "pbs_datastore_name=${PBS_DATASTORE_NAME}"
echo "pbs_proof_vm220_snapshot=${snapshot_name}"
echo "pbs_proof_index_present=${snapshot_index_present}"
echo "pbs_proof_fidx_present=${snapshot_fidx_present}"
echo "pbs_proof_backup_exists=${proof_backup_exists}"

if [[ "${pbs_storage_active}" == "yes" && "${proof_backup_exists}" == "yes" ]]; then
  echo "recommendation=begin_restore_drill_planning"
elif [[ "${pbs_storage_active}" == "yes" ]]; then
  echo "recommendation=complete_first_green_pbs_backup"
else
  echo "recommendation=restore_pbs_storage_connectivity"
fi

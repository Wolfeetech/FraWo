#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

log() {
  printf '[pbs-preflight] %s\n' "$*"
}

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "$ROOT_DIR/ansible/inventory/host_vars/proxmox.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
value = data[key]
print(value)
PY
}

PBS_VMID="$(read_hostvar proxmox_pbs_vmid)"
PBS_MEMORY_MB="$(read_hostvar proxmox_pbs_memory_mb)"
PBS_SYSTEM_DISK_GB="$(read_hostvar proxmox_pbs_system_disk_gb)"
PBS_DATASTORE_MOUNT_PATH="$(read_hostvar proxmox_pbs_datastore_mount_path)"
PBS_DATASTORE_MIN_GIB="$(read_hostvar proxmox_pbs_datastore_min_gib)"
PBS_ISO_DIR="$(read_hostvar proxmox_pbs_iso_dir)"
PBS_ISO_FILE="$(read_hostvar proxmox_pbs_iso_file)"
PBS_SYSTEM_STORAGE_ID="$(read_hostvar proxmox_pbs_storage)"
PBS_DATA_STORAGE_ID="$(read_hostvar proxmox_pbs_data_storage_id)"

log "Checking whether VM ${PBS_VMID} already exists"
if run_proxmox_remote "qm status ${PBS_VMID} >/dev/null 2>&1"; then
  echo "vm${PBS_VMID}_exists=yes"
  vm_exists="yes"
else
  echo "vm${PBS_VMID}_exists=no"
  vm_exists="no"
fi

vm_system_storage_expected="unknown"
vm_data_storage_expected="unknown"
if [[ "${vm_exists}" == "yes" ]]; then
  vm_config="$(run_proxmox_remote "qm config ${PBS_VMID}")"
  if grep -q "^scsi0: ${PBS_SYSTEM_STORAGE_ID}:" <<<"${vm_config}"; then
    vm_system_storage_expected="yes"
  else
    vm_system_storage_expected="no"
  fi
  if grep -q "^scsi1: ${PBS_DATA_STORAGE_ID}:" <<<"${vm_config}"; then
    vm_data_storage_expected="yes"
  else
    vm_data_storage_expected="no"
  fi
fi
echo "vm${PBS_VMID}_system_storage_expected=${vm_system_storage_expected}"
echo "vm${PBS_VMID}_data_storage_expected=${vm_data_storage_expected}"

log "Collecting host memory baseline"
mem_info="$(run_proxmox_remote "awk '/MemTotal:/ {total=\$2} /MemAvailable:/ {avail=\$2} END {printf \"%.2f %.2f\\n\", total/1024/1024, avail/1024/1024}' /proc/meminfo")"
read -r mem_total_gib mem_available_gib <<<"${mem_info}"
echo "mem_total_gib=${mem_total_gib}"
echo "mem_available_gib=${mem_available_gib}"

pbs_4gb_fit="no"
if python3 - <<'PY' "$mem_available_gib" "$PBS_MEMORY_MB"
import sys
available_gib = float(sys.argv[1])
required_mb = int(sys.argv[2])
required_gib = required_mb / 1024
raise SystemExit(0 if available_gib >= required_gib else 1)
PY
then
  pbs_4gb_fit="yes"
fi
echo "pbs_4gb_fit=${pbs_4gb_fit}"

log "Collecting storage baseline"
local_lvm_info="$(run_proxmox_remote "lvs --noheadings --units g --nosuffix -o lv_size,data_percent pve/data | awk 'NF >= 2 {size=\$1; used=\$2; avail=size-(size*used/100); printf \"%.2f %.2f %.2f\\n\", size, used, avail}'")"
read -r local_lvm_total_gib local_lvm_data_percent local_lvm_available_gib <<<"${local_lvm_info}"
echo "local_lvm_total_gib=${local_lvm_total_gib}"
echo "local_lvm_available_gib=${local_lvm_available_gib}"

pbs_system_disk_fit="no"
if python3 - <<'PY' "$local_lvm_available_gib" "$PBS_SYSTEM_DISK_GB"
import sys
available_gib = float(sys.argv[1])
required_gib = float(sys.argv[2])
raise SystemExit(0 if available_gib >= required_gib else 1)
PY
then
  pbs_system_disk_fit="yes"
fi
echo "pbs_system_disk_fit=${pbs_system_disk_fit}"

log "Checking PBS installer ISO presence"
if run_proxmox_remote "test -f ${PBS_ISO_DIR@Q}/${PBS_ISO_FILE@Q}"; then
  echo "pbs_iso_present=yes"
else
  echo "pbs_iso_present=no"
fi

log "Checking separate backup-storage mount"
datastore_mount_state="missing"
datastore_mount_available_gib="0.00"
separate_backup_storage_ready="no"
if run_proxmox_remote "findmnt -rn ${PBS_DATASTORE_MOUNT_PATH@Q} >/dev/null 2>&1"; then
  datastore_mount_state="mounted"
  datastore_mount_available_gib="$(
    run_proxmox_remote "python3 - <<'PY'
import os
path = ${PBS_DATASTORE_MOUNT_PATH@Q}
stats = os.statvfs(path)
available = stats.f_frsize * stats.f_bavail / (1024 ** 3)
print(f\"{available:.2f}\")
PY"
  )"
  if python3 - <<'PY' "$datastore_mount_available_gib" "$PBS_DATASTORE_MIN_GIB"
import sys
available_gib = float(sys.argv[1])
required_gib = float(sys.argv[2])
raise SystemExit(0 if available_gib >= required_gib else 1)
PY
  then
    separate_backup_storage_ready="yes"
  fi
fi
echo "pbs_datastore_mount_path=${PBS_DATASTORE_MOUNT_PATH}"
echo "pbs_datastore_mount_state=${datastore_mount_state}"
echo "pbs_datastore_available_gib=${datastore_mount_available_gib}"
echo "separate_backup_storage_ready=${separate_backup_storage_ready}"

log "Recommendation"
if [[ "${vm_exists}" == "yes" && ( "${vm_system_storage_expected}" != "yes" || "${vm_data_storage_expected}" != "yes" ) ]]; then
  echo "recommendation=vm240_exists_rebuild_config_drift_detected"
elif [[ "${vm_exists}" == "yes" ]]; then
  echo "recommendation=vm240_exists_validate_guest_state"
elif [[ "${separate_backup_storage_ready}" == "yes" ]]; then
  echo "recommendation=stage_pbs_iso_then_build_vm240"
else
  echo "recommendation=mount_separate_backup_storage_before_building_pbs_vm"
fi

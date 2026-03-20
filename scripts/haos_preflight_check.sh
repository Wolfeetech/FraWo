#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[haos-preflight] %s\n' "$*"
}

remote() {
  ssh proxmox "$@"
}

log "Checking whether VM 210 already exists"
vm210_exists="no"
if remote "qm status 210 >/dev/null 2>&1"; then
  vm210_exists="yes"
fi
echo "vm210_exists=${vm210_exists}"

log "Collecting host memory baseline"
remote "python3 - <<'PY'
from pathlib import Path
data = {}
for line in Path('/proc/meminfo').read_text().splitlines():
    key, val = line.split(':', 1)
    data[key] = int(val.strip().split()[0])
total_gib = data['MemTotal'] / 1024 / 1024
avail_gib = data['MemAvailable'] / 1024 / 1024
print(f'mem_total_gib={total_gib:.2f}')
print(f'mem_available_gib={avail_gib:.2f}')
print('haos_4gb_fit=' + ('yes' if avail_gib >= 4.0 else 'no'))
PY"

log "Collecting configured memory footprint"
remote "python3 - <<'PY'
import subprocess
vmids = ['200', '220', '230']
assigned = 0
for vmid in vmids:
    cfg = subprocess.check_output(['qm', 'config', vmid], text=True)
    for line in cfg.splitlines():
        if line.startswith('memory:'):
            assigned += int(line.split(':', 1)[1].strip())
            break
ct_cfg = subprocess.check_output(['pct', 'config', '100'], text=True)
ct_mem = 0
for line in ct_cfg.splitlines():
    if line.startswith('memory:'):
        ct_mem = int(line.split(':', 1)[1].strip())
        break
print(f'business_vm_mem_mb={assigned}')
print(f'toolbox_mem_mb={ct_mem}')
print(f'combined_assigned_mb={assigned + ct_mem}')
PY"

log "Collecting storage baseline"
remote "python3 - <<'PY'
import subprocess
for line in subprocess.check_output(['pvesm', 'status'], text=True).splitlines()[1:]:
    cols = line.split()
    if len(cols) >= 6 and cols[0] == 'local-lvm':
        total_kib = int(cols[3])
        avail_kib = int(cols[5])
        print(f'local_lvm_total_gib={total_kib / 1024 / 1024:.2f}')
        print(f'local_lvm_available_gib={avail_kib / 1024 / 1024:.2f}')
        print('haos_32g_disk_fit=' + ('yes' if avail_kib >= 32 * 1024 * 1024 else 'no'))
        break
PY"

log "Collecting USB audit"
usb_output="$(remote "lsusb")"
printf '%s\n' "$usb_output"
serial_by_id="$(remote "ls -1 /dev/serial/by-id 2>/dev/null || true")"
if [[ -n "$serial_by_id" ]]; then
  printf '%s\n' "$serial_by_id"
else
  echo "serial_by_id=empty"
fi

usb_device_count="$(printf '%s\n' "$usb_output" | grep -c '^Bus ' || true)"
non_root_hub_count="$(printf '%s\n' "$usb_output" | grep '^Bus ' | grep -vc 'Linux Foundation .* root hub' || true)"
echo "usb_total_entries=${usb_device_count}"
echo "usb_candidate_devices=${non_root_hub_count}"

log "Recommendation"
if [[ "$vm210_exists" == "yes" && "$non_root_hub_count" -eq 0 ]]; then
  echo "usb_passthrough_ready=no"
  echo "recommendation=vm210_exists_continue_with_addressing_snapshot_and_later_usb_passthrough"
elif [[ "$vm210_exists" == "yes" ]]; then
  echo "usb_passthrough_ready=yes"
  echo "recommendation=vm210_exists_continue_with_addressing_and_detected_usb_planning"
elif [[ "$non_root_hub_count" -eq 0 ]]; then
  echo "usb_passthrough_ready=no"
  echo "recommendation=build_haos_baseline_only_after_network_stage_gate_or_wait_for_usb_adapters"
else
  echo "usb_passthrough_ready=yes"
  echo "recommendation=haos_usb_passthrough_can_be_planned_with_detected_adapters"
fi

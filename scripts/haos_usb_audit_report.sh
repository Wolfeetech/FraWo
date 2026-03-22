#!/usr/bin/env bash
set -euo pipefail

remote() {
  ssh proxmox "$@"
}

usb_output="$(remote "lsusb")"
serial_by_id="$(remote "ls -1 /dev/serial/by-id 2>/dev/null || true")"
serial_by_path="$(remote "ls -1 /dev/serial/by-path 2>/dev/null || true")"

printf '%s\n' "${usb_output}"
if [[ -n "${serial_by_id}" ]]; then
  printf '%s\n' "${serial_by_id}"
else
  echo "serial_by_id=empty"
fi
if [[ -n "${serial_by_path}" ]]; then
  printf '%s\n' "${serial_by_path}"
else
  echo "serial_by_path=empty"
fi

USB_AUDIT_SOURCE="${usb_output}" python3 - <<'PY'
import re
import os
import sys

lines = [line.strip() for line in os.environ.get("USB_AUDIT_SOURCE", "").splitlines() if line.strip()]
storage_patterns = [
    r'\bUSB Disk\b',
    r'\bMass Storage\b',
    r'\bFlash Disk\b',
    r'\bKingston\b',
    r'\bSanDisk\b',
]
candidate_patterns = [
    r'zigbee',
    r'skyconnect',
    r'conbee',
    r'sonoff',
    r'\bcp210',
    r'\bch340',
    r'\bftdi\b',
    r'\bbluetooth\b',
    r'\bthread\b',
    r'\bz-wave\b',
    r'\befr32\b',
    r'\bnordic\b',
]

root_hubs = []
storage_only = []
passthrough_candidates = []
other_usb = []

for line in lines:
    low = line.lower()
    if 'linux foundation' in low and 'root hub' in low:
        root_hubs.append(line)
    elif any(re.search(pattern, line, re.IGNORECASE) for pattern in storage_patterns):
        storage_only.append(line)
    elif any(re.search(pattern, line, re.IGNORECASE) for pattern in candidate_patterns):
        passthrough_candidates.append(line)
    else:
        other_usb.append(line)

print(f'usb_total_entries={len(lines)}')
print(f'usb_root_hub_count={len(root_hubs)}')
print(f'usb_storage_only_count={len(storage_only)}')
print(f'usb_passthrough_candidate_count={len(passthrough_candidates)}')
print(f'usb_other_device_count={len(other_usb)}')
print('usb_storage_only_present=' + ('yes' if storage_only else 'no'))
print('usb_passthrough_candidate_present=' + ('yes' if passthrough_candidates else 'no'))

if passthrough_candidates:
    print('usb_audit_recommendation=plan_vendor_product_and_port_mapping_for_detected_dongles')
elif storage_only:
    print('usb_audit_recommendation=ignore_storage_only_usb_and_wait_for_real_haos_dongles')
else:
    print('usb_audit_recommendation=no_external_haos_usb_candidates_detected')
PY

serial_count=0
if [[ -n "${serial_by_id}" ]]; then
  serial_count="$(printf '%s\n' "${serial_by_id}" | sed '/^$/d' | wc -l | awk '{print $1}')"
fi
echo "serial_by_id_count=${serial_count}"

if [[ "${serial_count}" -gt 0 ]]; then
  echo "serial_devices_present=yes"
else
  echo "serial_devices_present=no"
fi

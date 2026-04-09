#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

if [[ $# -gt 1 ]]; then
  echo "Usage: $0 [/dev/sdX]" >&2
  exit 1
fi

TARGET_DEVICE="${1:-}"

if [[ -z "${TARGET_DEVICE}" ]]; then
  TARGET_DEVICE="$(
    run_proxmox_remote "python3 - <<'PY'
import json
import subprocess
import sys

raw = subprocess.check_output(
    [
        'lsblk',
        '-J',
        '-b',
        '-d',
        '-o',
        'PATH,SIZE,TYPE,TRAN,RM,HOTPLUG,MOUNTPOINT,LABEL,MODEL',
    ],
    text=True,
)
data = json.loads(raw)
candidates = []
for item in data.get('blockdevices', []):
    if item.get('type') != 'disk':
        continue
    if item.get('tran') != 'usb':
        continue
    if item.get('mountpoint'):
        continue
    if item.get('label') == 'HS27_PORTABLEBK':
        continue
    try:
        size = int(item.get('size', '0'))
    except ValueError:
        continue
    if not (50 * 1024**3 <= size <= 70 * 1024**3):
        continue
    candidates.append(item.get('path'))

if len(candidates) != 1:
    print(f'portable_backup_usb_autodetect_candidates={len(candidates)}', file=sys.stderr)
    for candidate in candidates:
        print(candidate, file=sys.stderr)
    raise SystemExit(1)

print(candidates[0])
PY" 2>/dev/null || true
  )"

  if [[ -z "${TARGET_DEVICE}" ]]; then
    echo "Could not auto-detect exactly one raw 64GB-class USB disk on Proxmox" >&2
    echo "Attach only the backup USB stick, then rerun or pass /dev/sdX explicitly" >&2
    exit 1
  fi
fi

echo "portable_backup_usb_target_device=${TARGET_DEVICE}"
"${ROOT_DIR}/scripts/proxmox_portable_backup_usb_prepare.sh" "${TARGET_DEVICE}"

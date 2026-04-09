#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

MOUNT_PATH="/srv/portable-backup-usb"
ARCHIVE_DIR="/var/lib/vz/dump"
TARGET_DIR="${MOUNT_PATH}/archives"
MANIFEST_PATH="${MOUNT_PATH}/manifests/selection.txt"
RESERVE_GIB=4
MAX_USAGE_PERCENT=94
VMIDS=(200 210 220 230)

remote_cmd="$(cat <<'EOF'
set -euo pipefail

MOUNT_PATH="/srv/portable-backup-usb"
ARCHIVE_DIR="/var/lib/vz/dump"
TARGET_DIR="${MOUNT_PATH}/archives"
MANIFEST_PATH="${MOUNT_PATH}/manifests/selection.txt"
RESERVE_GIB=4
MAX_USAGE_PERCENT=94
VMIDS=(200 210 220 230)

if [[ ! -d "${MOUNT_PATH}" ]]; then
  echo "Portable backup USB mount path ${MOUNT_PATH} missing" >&2
  exit 1
fi

if ! mountpoint -q "${MOUNT_PATH}"; then
  DEVICE="$(blkid -L HS27_PORTABLEBK || true)"
  if [[ -z "${DEVICE}" ]]; then
    echo "Portable backup USB with label HS27_PORTABLEBK not found" >&2
    exit 1
  fi
  mount "${DEVICE}" "${MOUNT_PATH}"
fi

install -d -m 0755 "${TARGET_DIR}" "$(dirname "${MANIFEST_PATH}")"

python3 - <<'PY'
from pathlib import Path
import os
import shutil

mount_path = Path("/srv/portable-backup-usb")
archive_dir = Path("/var/lib/vz/dump")
target_dir = mount_path / "archives"
manifest_path = mount_path / "manifests" / "selection.txt"
reserve_gib = 4
max_usage_percent = 94
vmids = [200, 210, 220, 230]

usage = shutil.disk_usage(mount_path)
capacity = usage.total
budget = min(int(capacity * (max_usage_percent / 100.0)), capacity - reserve_gib * 1024**3)
if budget <= 0:
    raise SystemExit("Portable backup USB budget is not positive")

archives = []
for vmid in vmids:
    vm_archives = sorted(archive_dir.glob(f"vzdump-qemu-{vmid}-*.vma.zst"), key=lambda p: p.stat().st_mtime, reverse=True)
    archives.append((vmid, vm_archives))

selected = []
selected_set = set()
used = 0

for vmid, vm_archives in archives:
    if not vm_archives:
        continue
    candidate = vm_archives[0]
    size = candidate.stat().st_size
    if used + size <= budget:
      selected.append(candidate.name)
      selected_set.add(candidate.name)
      used += size

remaining = sorted(
    [p for _, vm_archives in archives for p in vm_archives[1:] if p.name not in selected_set],
    key=lambda p: p.stat().st_mtime,
    reverse=True,
)

for candidate in remaining:
    size = candidate.stat().st_size
    if used + size > budget:
        continue
    selected.append(candidate.name)
    selected_set.add(candidate.name)
    used += size

manifest_path.write_text("\n".join(selected) + ("\n" if selected else ""), encoding="utf-8")
print(f"portable_backup_budget_bytes={budget}")
print(f"portable_backup_selected_count={len(selected)}")
print(f"portable_backup_selected_bytes={used}")
PY

rsync -a --delete --files-from="${MANIFEST_PATH}" "${ARCHIVE_DIR}/" "${TARGET_DIR}/"

find "${TARGET_DIR}" -type f -name 'vzdump-qemu-*.vma.zst' | sort > "${MOUNT_PATH}/manifests/on_usb.txt"
du -sh "${TARGET_DIR}" || true
df -h "${MOUNT_PATH}"
EOF
)"

run_proxmox_remote "${remote_cmd}"

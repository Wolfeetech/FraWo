#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 /dev/sdX" >&2
  echo "Deprecated alias. Use scripts/proxmox_prepare_pbs_datastore_device.sh /dev/sdX instead." >&2
  exit 64
fi

echo "[pbs-usb-interim-prepare] Deprecated alias; delegating to guarded PBS datastore prepare" >&2
exec "${ROOT_DIR}/scripts/proxmox_prepare_pbs_datastore_device.sh" "$1"

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

if [[ $# -eq 0 ]]; then
  echo "usage: proxmox_remote_exec.sh '<command>'" >&2
  exit 64
fi

run_proxmox_remote "$*"

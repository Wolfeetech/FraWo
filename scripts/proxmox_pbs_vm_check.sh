#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

log() {
  printf '[pbs-vm-check] %s\n' "$*"
}

remote() {
  run_proxmox_remote "$*"
}

RUNNER_PATH="/usr/local/sbin/homeserver2027-deploy-pbs-vm.sh"

log "Checking PBS runner presence on Proxmox"
if remote "test -x ${RUNNER_PATH@Q}"; then
  echo "pbs_runner_installed=yes"
else
  echo "pbs_runner_installed=no"
fi

log "Checking whether VM 240 exists"
if remote "qm status 240 >/dev/null 2>&1"; then
  echo "vm240_exists=yes"
  remote "qm config 240 | sed -n '1,160p'"
else
  echo "vm240_exists=no"
fi

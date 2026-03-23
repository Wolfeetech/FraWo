#!/usr/bin/env bash
set -euo pipefail

log() {
  printf '[haos-vm-check] %s\n' "$*"
}

remote() {
  ssh proxmox "$@"
}

RUNNER_PATH="/usr/local/sbin/homeserver2027-deploy-haos-vm.sh"

log "Checking HAOS runner presence on Proxmox"
if remote "test -x ${RUNNER_PATH@Q}"; then
  echo "haos_runner_installed=yes"
else
  echo "haos_runner_installed=no"
fi

log "Checking whether VM 210 exists"
if remote "qm status 210 >/dev/null 2>&1"; then
  echo "vm210_exists=yes"
  remote "qm config 210 | sed -n '1,160p'"
else
  echo "vm210_exists=no"
fi

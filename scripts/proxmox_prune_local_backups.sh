#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

KEEP_LAST="${KEEP_LAST:-2}"
VMIDS="${VMIDS:-200 210 220 230}"
APPLY="${APPLY:-0}"

log() {
  printf '[backup-prune] %s\n' "$*"
}

remote() {
  run_proxmox_remote "$1"
}

log "Retention policy: keep latest ${KEEP_LAST} local qemu backups per VM"
if [[ "${APPLY}" != "1" ]]; then
  log "Dry run only. Set APPLY=1 to delete older archives."
fi

for vmid in ${VMIDS}; do
  log "Reviewing VM ${vmid}"
  archives="$(remote "ls -1t /var/lib/vz/dump/vzdump-qemu-${vmid}-*.vma.zst 2>/dev/null || true")"

  if [[ -z "${archives}" ]]; then
    log "No local backup archives found for VM ${vmid}"
    continue
  fi

  old_archives="$(printf '%s\n' "${archives}" | awk -v keep="${KEEP_LAST}" 'NR > keep {print}')"

  if [[ -z "${old_archives}" ]]; then
    log "Nothing to prune for VM ${vmid}"
    continue
  fi

  printf '%s\n' "${old_archives}" | while IFS= read -r archive; do
    [[ -n "${archive}" ]] || continue
    if [[ "${APPLY}" == "1" ]]; then
      log "Deleting ${archive}"
      remote "rm -f '${archive}'"
    else
      log "Would delete ${archive}"
    fi
  done
done

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

run_toolbox_remote() {
  local remote_command="$1"
  local toolbox_vmid="${HOMESERVER_TOOLBOX_VMID:-100}"
  local payload

  if run_inventory_remote "toolbox" "${remote_command}" "root" 2>/dev/null; then
    return 0
  fi

  payload="$(printf '%s' "${remote_command}" | base64 -w0)"

  if run_proxmox_remote "pct exec ${toolbox_vmid} -- bash -lc \"echo ${payload} | base64 -d | bash\"" 2>/dev/null; then
    return 0
  fi

  echo "toolbox_remote_error=direct_ssh_and_proxmox_pct_fallback_failed" >&2
  return 1
}

#!/usr/bin/env bash
set -euo pipefail

run_toolbox_remote() {
  local remote_command="$1"
  local toolbox_host="${HOMESERVER_TOOLBOX_HOST:-192.168.2.20}"
  local toolbox_user="${HOMESERVER_TOOLBOX_USER:-root}"
  local toolbox_target="${toolbox_user}@${toolbox_host}"
  local -a ssh_opts=(-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new)

  if ssh "${ssh_opts[@]}" "${toolbox_target}" "${remote_command}" 2>/dev/null; then
    return 0
  fi

  if [[ -z "${HOMESERVER_PROXMOX_ROOT_PASSWORD:-}" ]]; then
    return 1
  fi

  local proxmox_host="${HOMESERVER_PROXMOX_HOST:-192.168.2.10}"
  local toolbox_vmid="${HOMESERVER_TOOLBOX_VMID:-100}"
  local payload
  payload="$(printf '%s' "${remote_command}" | base64 -w0)"

  sshpass -p "${HOMESERVER_PROXMOX_ROOT_PASSWORD}" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@"${proxmox_host}" \
    "pct exec ${toolbox_vmid} -- bash -lc \"echo ${payload} | base64 -d | bash\"" \
    2>/dev/null
}
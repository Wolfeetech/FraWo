#!/usr/bin/env bash
set -euo pipefail

run_rpi_remote() {
  local target_host="$1"
  local remote_command="$2"
  local ssh_target="wolf@${target_host}"
  local -a ssh_opts=(-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new)

  if ssh "${ssh_opts[@]}" "${ssh_target}" "${remote_command}" 2>/dev/null; then
    return 0
  fi

  if [[ -z "${HOMESERVER_PROXMOX_ROOT_PASSWORD:-}" ]]; then
    return 1
  fi

  local proxmox_host="${HOMESERVER_PROXMOX_HOST:-192.168.2.10}"
  local toolbox_vmid="${HOMESERVER_TOOLBOX_VMID:-100}"
  local toolbox_key="${HOMESERVER_RPI_SSH_KEY:-/root/.ssh/homeserver2027_media_sync}"
  local payload
  payload="$(printf '%s' "${remote_command}" | base64 -w0)"

  sshpass -p "${HOMESERVER_PROXMOX_ROOT_PASSWORD}" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no root@"${proxmox_host}" \
    "pct exec ${toolbox_vmid} -- bash -lc 'ssh -i ${toolbox_key} -o StrictHostKeyChecking=no ${ssh_target} \"echo ${payload} | base64 -d | bash\"'" \
    2>/dev/null
}
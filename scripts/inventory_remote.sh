#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INVENTORY_FILE="${HOMESERVER_INVENTORY_FILE:-${ROOT_DIR}/ansible/inventory/hosts.yml}"
PROXMOX_KEY_CACHE_FILE="${HOMESERVER_PROXMOX_IDENTITY_CACHE_FILE:-${HOME}/.ssh/homeserver2027_proxmox_ed25519}"

inventory_host_field() {
  local host_key="$1"
  local field="$2"
  local default_value="${3:-}"

  python3 - <<'PY' "${INVENTORY_FILE}" "${host_key}" "${field}" "${default_value}"
import sys
import yaml

inventory_path, host_key, field, default_value = sys.argv[1:5]

with open(inventory_path, "r", encoding="utf-8") as handle:
    data = yaml.safe_load(handle)

def find_host(node, key):
    if isinstance(node, dict):
        hosts = node.get("hosts")
        if isinstance(hosts, dict) and key in hosts:
            return hosts[key]
        for value in node.values():
            found = find_host(value, key)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = find_host(value, key)
            if found is not None:
                return found
    return None

host_data = find_host(data, host_key) or {}
value = host_data.get(field, default_value)
if value is None:
    value = default_value
print(value)
PY
}

inventory_ssh_target() {
  local host_key="$1"
  local default_user="${2:-root}"
  local host
  local user

  host="$(inventory_host_field "${host_key}" ansible_host)"
  if [[ -z "${host}" ]]; then
    echo "inventory host ${host_key} has no ansible_host" >&2
    return 1
  fi

  user="$(inventory_host_field "${host_key}" ansible_user "${default_user}")"
  if [[ -z "${user}" ]]; then
    user="${default_user}"
  fi

  printf '%s@%s\n' "${user}" "${host}"
}

inventory_identity_file() {
  local host_key="$1"
  local configured

  configured="$(inventory_host_field "${host_key}" ansible_ssh_private_key_file)"
  if [[ -n "${configured}" ]]; then
    printf '%s\n' "${configured}"
    return 0
  fi

  configured="$(inventory_host_field "${host_key}" ansible_private_key_file)"
  if [[ -n "${configured}" ]]; then
    printf '%s\n' "${configured}"
    return 0
  fi

  if [[ "${host_key}" == "proxmox" ]]; then
    proxmox_identity_file || true
  fi
}

root_dir_windows_user() {
  if [[ "${ROOT_DIR}" =~ ^/mnt/[a-z]/Users/([^/]+)/ ]]; then
    printf '%s\n' "${BASH_REMATCH[1]}"
    return 0
  fi
  return 1
}

stage_identity_file() {
  local source_path="$1"

  if [[ ! -r "${source_path}" ]]; then
    return 1
  fi

  mkdir -p "$(dirname "${PROXMOX_KEY_CACHE_FILE}")"
  install -m 600 "${source_path}" "${PROXMOX_KEY_CACHE_FILE}"
  printf '%s\n' "${PROXMOX_KEY_CACHE_FILE}"
}

proxmox_identity_file() {
  local candidate="${HOMESERVER_PROXMOX_IDENTITY_FILE:-}"
  local windows_user

  if [[ -n "${candidate}" && -r "${candidate}" ]]; then
    if [[ "${candidate}" == /mnt/* ]]; then
      stage_identity_file "${candidate}"
    else
      printf '%s\n' "${candidate}"
    fi
    return 0
  fi

  if [[ -r "${PROXMOX_KEY_CACHE_FILE}" ]]; then
    printf '%s\n' "${PROXMOX_KEY_CACHE_FILE}"
    return 0
  fi

  if [[ -r "${HOME}/.ssh/pve_ed25519" ]]; then
    printf '%s\n' "${HOME}/.ssh/pve_ed25519"
    return 0
  fi

  if windows_user="$(root_dir_windows_user)" && [[ -r "/mnt/c/Users/${windows_user}/.ssh/pve_ed25519" ]]; then
    stage_identity_file "/mnt/c/Users/${windows_user}/.ssh/pve_ed25519"
    return 0
  fi

  return 1
}

run_proxmox_remote_via_windows_ssh() {
  local remote_command="$1"
  local payload
  local ps_script
  local status

  if ! command -v powershell.exe >/dev/null 2>&1 || ! command -v wslpath >/dev/null 2>&1; then
    return 127
  fi

  payload="$(printf '%s' "${remote_command}" | base64 -w0)"
  ps_script="$(wslpath -w "${ROOT_DIR}/scripts/proxmox_windows_ssh_exec.ps1")"
  powershell.exe -NoProfile -File "${ps_script}" -RemoteCommandBase64 "${payload}" | tr -d '\r'
  status="${PIPESTATUS[0]}"
  return "${status}"
}

inventory_guest_vmid() {
  local host_key="$1"
  local configured

  configured="$(inventory_host_field "${host_key}" proxmox_vmid)"
  if [[ -n "${configured}" ]]; then
    printf '%s\n' "${configured}"
    return 0
  fi

  case "${host_key}" in
    nextcloud_vm)
      echo "200"
      ;;
    haos_vm)
      echo "210"
      ;;
    odoo_vm)
      echo "220"
      ;;
    paperless_vm)
      echo "230"
      ;;
    pbs)
      echo "240"
      ;;
    *)
      return 1
      ;;
  esac
}

run_inventory_remote() {
  local host_key="$1"
  local remote_command="$2"
  local default_user="${3:-root}"
  local target
  local identity_file
  local -a ssh_opts=(
    -o BatchMode=yes
    -o ConnectTimeout="${HOMESERVER_SSH_CONNECT_TIMEOUT:-8}"
    -o StrictHostKeyChecking=accept-new
  )

  target="$(inventory_ssh_target "${host_key}" "${default_user}")"
  identity_file="$(inventory_identity_file "${host_key}")"
  if [[ -n "${identity_file}" ]]; then
    ssh_opts+=(-i "${identity_file}")
  fi
  ssh "${ssh_opts[@]}" "${target}" "${remote_command}"
}

run_inventory_guest_remote() {
  local host_key="$1"
  local remote_command="$2"
  local default_user="${3:-root}"
  local vmid
  local payload
  local guest_output
  local direct_output=""
  local direct_stderr=""
  local direct_status=0

  direct_stderr="$(mktemp)"
  set +e
  direct_output="$(run_inventory_remote "${host_key}" "${remote_command}" "${default_user}" 2>"${direct_stderr}")"
  direct_status=$?
  set -e

  if [[ "${direct_status}" -eq 0 ]]; then
    printf '%s' "${direct_output}"
    rm -f "${direct_stderr}"
    return 0
  fi

  # Only fall back to guest exec when SSH transport failed. Remote command
  # failures must be preserved so probe-style checks do not turn false-green.
  if [[ "${direct_status}" -ne 255 ]]; then
    if [[ -s "${direct_stderr}" ]]; then
      cat "${direct_stderr}" >&2
    fi
    printf '%s' "${direct_output}"
    rm -f "${direct_stderr}"
    return "${direct_status}"
  fi

  rm -f "${direct_stderr}"

  vmid="$(inventory_guest_vmid "${host_key}")" || {
    echo "inventory_guest_remote_error=no_vmid_mapping_for_${host_key}" >&2
    return 1
  }

  payload="$(printf '%s' "${remote_command}" | base64 -w0)"
  guest_output="$(
    run_proxmox_remote "qm guest exec ${vmid} -- bash -lc \"echo ${payload} | base64 -d | bash\""
  )" || {
    echo "inventory_guest_remote_error=guest_exec_failed_for_${host_key}" >&2
    return 1
  }

  python3 - <<'PY' <<<"${guest_output}"
import json
import sys

data = json.load(sys.stdin)
stdout = data.get("out-data", "")
stderr = data.get("err-data", "")
exitcode = int(data.get("exitcode", 0) or 0)

if stdout:
    sys.stdout.write(stdout)
if stderr:
    sys.stderr.write(stderr)

raise SystemExit(exitcode)
PY
}

run_proxmox_remote() {
  local remote_command="$1"
  local target
  local direct_output=""
  local direct_stderr=""
  local direct_status=0

  direct_stderr="$(mktemp)"
  set +e
  direct_output="$(run_proxmox_remote_via_windows_ssh "${remote_command}" 2>"${direct_stderr}")"
  direct_status=$?
  set -e
  if [[ "${direct_status}" -eq 0 ]]; then
    printf '%s' "${direct_output}"
    rm -f "${direct_stderr}"
    return 0
  fi
  if [[ "${direct_status}" -ne 127 && "${direct_status}" -ne 255 ]]; then
    if [[ -s "${direct_stderr}" ]]; then
      cat "${direct_stderr}" >&2
    fi
    printf '%s' "${direct_output}"
    rm -f "${direct_stderr}"
    return "${direct_status}"
  fi
  rm -f "${direct_stderr}"

  direct_stderr="$(mktemp)"
  set +e
  direct_output="$(run_inventory_remote "proxmox" "${remote_command}" "root" 2>"${direct_stderr}")"
  direct_status=$?
  set -e
  if [[ "${direct_status}" -eq 0 ]]; then
    printf '%s' "${direct_output}"
    rm -f "${direct_stderr}"
    return 0
  fi
  if [[ "${direct_status}" -ne 255 ]]; then
    if [[ -s "${direct_stderr}" ]]; then
      cat "${direct_stderr}" >&2
    fi
    printf '%s' "${direct_output}"
    rm -f "${direct_stderr}"
    return "${direct_status}"
  fi
  rm -f "${direct_stderr}"

  if [[ -z "${HOMESERVER_PROXMOX_ROOT_PASSWORD:-}" ]]; then
    echo "proxmox_remote_error=direct_ssh_failed_and_HOMESERVER_PROXMOX_ROOT_PASSWORD_not_set" >&2
    return 1
  fi

  target="$(inventory_ssh_target "proxmox" "root")"
  if sshpass -p "${HOMESERVER_PROXMOX_ROOT_PASSWORD}" \
    ssh \
      -o ConnectTimeout="${HOMESERVER_SSH_CONNECT_TIMEOUT:-10}" \
      -o StrictHostKeyChecking=accept-new \
      "${target}" \
      "${remote_command}"; then
    return 0
  fi

  echo "proxmox_remote_error=direct_ssh_and_password_fallback_failed" >&2
  return 1
}

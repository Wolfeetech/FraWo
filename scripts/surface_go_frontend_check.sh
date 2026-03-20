#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_IP="192.168.2.154"
TARGET_HOSTNAME="surface-go-frontend"

port_state() {
  local port="$1"
  if timeout 1 bash -lc "</dev/tcp/${TARGET_IP}/${port}" >/dev/null 2>&1; then
    echo "open"
  else
    echo "closed"
  fi
}

http_body="$(timeout 3 curl -fsSL "http://${TARGET_IP}" 2>/dev/null || true)"
http_title="$(printf '%s' "${http_body}" | tr '\n' ' ' | sed -n 's:.*<title>\\(.*\\)</title>.*:\\1:p' | head -n1 || true)"
inventory_present="no"
if rg -q '^        surface_go_frontend:$' "${ROOT_DIR}/ansible/inventory/hosts.yml"; then
  inventory_present="yes"
fi

ssh_port="$(port_state 22)"
http_port="$(port_state 80)"
https_port="$(port_state 443)"

echo "surface_go_inventory_present=${inventory_present}"
echo "surface_go_target_ip=${TARGET_IP}"
echo "surface_go_target_hostname=${TARGET_HOSTNAME}"
echo "surface_go_ssh_port=${ssh_port}"
echo "surface_go_http_port=${http_port}"
echo "surface_go_https_port=${https_port}"
echo "surface_go_http_title=${http_title:-unknown}"

default_nginx="no"
if printf '%s' "${http_body}" | grep -q 'Welcome to nginx!'; then
  default_nginx="yes"
fi
echo "surface_go_default_nginx_page=${default_nginx}"

remote_admin_ready="no"
if [[ "${ssh_port}" == "open" ]]; then
  remote_admin_ready="yes"
fi
echo "surface_go_remote_admin_ready=${remote_admin_ready}"

rebuild_required="yes"
if [[ "${ssh_port}" == "open" && "${default_nginx}" == "no" ]]; then
  rebuild_required="no"
fi
echo "surface_go_clean_rebuild_required=${rebuild_required}"

if [[ "${rebuild_required}" == "yes" ]]; then
  echo "recommendation=clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook"
else
  echo "recommendation=run_postinstall_acceptance_and_promote_to_managed_frontend"
fi

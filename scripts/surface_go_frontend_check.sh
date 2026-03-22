#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_IP="192.168.2.154"
TARGET_HOSTNAME="surface-go-frontend"
TAILSCALE_HOSTNAME="surface-go-frontend"

port_state() {
  local host="$1"
  local port="$2"
  if [[ -z "${host}" ]]; then
    echo "closed"
    return
  fi
  if timeout 1 bash -lc "</dev/tcp/${host}/${port}" >/dev/null 2>&1; then
    echo "open"
  else
    echo "closed"
  fi
}

tailscale_ip() {
  if ! command -v tailscale >/dev/null 2>&1; then
    return
  fi
  tailscale status 2>/dev/null | awk -v host="${TAILSCALE_HOSTNAME}" '$2 == host {print $1; exit}'
}

target_admin_path="none"
target_tailscale_ip="$(tailscale_ip || true)"
admin_host=""

lan_ssh_port="$(port_state "${TARGET_IP}" 22)"
tailscale_ssh_port="$(port_state "${target_tailscale_ip}" 22)"

if [[ "${lan_ssh_port}" == "open" ]]; then
  target_admin_path="lan"
  admin_host="${TARGET_IP}"
elif [[ "${tailscale_ssh_port}" == "open" ]]; then
  target_admin_path="tailscale"
  admin_host="${target_tailscale_ip}"
fi

remote_probe() {
  local command="$1"
  if [[ -z "${admin_host}" ]]; then
    return
  fi
  ssh -o BatchMode=yes -o ConnectTimeout=5 "frawo@${admin_host}" "${command}" 2>/dev/null || true
}

http_body="$(timeout 3 curl -fsSL "http://${TARGET_IP}" 2>/dev/null || true)"
http_title="$(printf '%s' "${http_body}" | tr '\n' ' ' | sed -n 's:.*<title>\\(.*\\)</title>.*:\\1:p' | head -n1 || true)"
inventory_present="no"
if rg -q '^        surface_go_frontend:$' "${ROOT_DIR}/ansible/inventory/hosts.yml"; then
  inventory_present="yes"
fi

ssh_port="closed"
case "${target_admin_path}" in
  lan) ssh_port="${lan_ssh_port}" ;;
  tailscale) ssh_port="${tailscale_ssh_port}" ;;
esac

http_port="$(port_state "${TARGET_IP}" 80)"
https_port="$(port_state "${TARGET_IP}" 443)"

echo "surface_go_inventory_present=${inventory_present}"
echo "surface_go_target_ip=${TARGET_IP}"
echo "surface_go_tailscale_ip=${target_tailscale_ip:-unknown}"
echo "surface_go_target_hostname=${TARGET_HOSTNAME}"
echo "surface_go_admin_path=${target_admin_path}"
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

portal_service_active="unknown"
portal_http_local="unknown"
control_launcher_present="unknown"
browser_binary_present="unknown"

if [[ "${remote_admin_ready}" == "yes" ]]; then
  portal_service_active="$(remote_probe "systemctl is-active homeserver2027-surface-portal.service" | head -n1)"
  portal_http_local="$(remote_probe "curl -fsSI http://127.0.0.1:17827 >/dev/null && echo ok || echo fail" | head -n1)"
  control_launcher_present="$(remote_probe "test -f /home/frawo/Desktop/FRAWO-Control.desktop && echo yes || echo no" | head -n1)"
  browser_binary_present="$(remote_probe "command -v epiphany-browser >/dev/null && echo yes || echo no" | head -n1)"
fi

echo "surface_go_portal_service_active=${portal_service_active:-unknown}"
echo "surface_go_local_portal_http=${portal_http_local:-unknown}"
echo "surface_go_control_launcher_present=${control_launcher_present:-unknown}"
echo "surface_go_browser_binary_present=${browser_binary_present:-unknown}"

rebuild_required="yes"
if [[ "${ssh_port}" == "open" && "${default_nginx}" == "no" ]]; then
  rebuild_required="no"
fi
echo "surface_go_clean_rebuild_required=${rebuild_required}"

if [[ "${rebuild_required}" == "yes" ]]; then
  echo "recommendation=clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook"
elif [[ "${portal_service_active}" == "active" && "${portal_http_local}" == "ok" && "${control_launcher_present}" == "yes" && "${browser_binary_present}" == "yes" ]]; then
  echo "recommendation=surface_frontend_ready_for_daily_use"
elif [[ "${target_admin_path}" == "tailscale" ]]; then
  echo "recommendation=perform_visual_kiosk_acceptance_over_local_session"
else
  echo "recommendation=run_postinstall_acceptance_and_promote_to_managed_frontend"
fi

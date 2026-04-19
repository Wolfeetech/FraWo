#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SURFACE_ISO="${HOME}/Downloads/Homeserver2027/install-media/surface/ubuntu-24.04.4-desktop-amd64.iso"
SURFACE_ISO_MIN_BYTES=$((5 * 1024 * 1024 * 1024))

toolbox_frontdoor_ip() {
  awk '
    /^[[:space:]]*#/ {next}
    /^[[:space:]]*Host[[:space:]]+/ {
      in_toolbox=0
      for (i=2; i<=NF; i++) {
        if ($i == "toolbox") {
          in_toolbox=1
        }
      }
      next
    }
    in_toolbox && /^[[:space:]]*HostName[[:space:]]+/ {
      print $2
      exit
    }
  ' "${ROOT_DIR}/Codex/ssh_config"
}

TOOLBOX_FRONTDOOR_IP="$(toolbox_frontdoor_ip)"
TOOLBOX_FRONTDOOR_IP="${TOOLBOX_FRONTDOOR_IP:-100.82.26.53}"

bool_from_systemd() {
  local unit="$1"
  if systemctl is-active --quiet "${unit}"; then
    echo "yes"
  else
    echo "no"
  fi
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "${data}" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

zenbook_anydesk_active="$(bool_from_systemd anydesk)"
zenbook_tailscaled_active="$(bool_from_systemd tailscaled)"

if tailscale ip -4 >/dev/null 2>&1; then
  zenbook_tailscale_joined="yes"
  zenbook_tailscale_ipv4="$(tailscale ip -4 | head -n1)"
else
  zenbook_tailscale_joined="no"
  zenbook_tailscale_ipv4=""
fi

toolbox_mobile_frontdoor_http="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 http://${TOOLBOX_FRONTDOOR_IP}:8447 || true)"
if [[ "${toolbox_mobile_frontdoor_http}" == "200" ]]; then
  toolbox_mobile_frontdoor_ready="yes"
else
  toolbox_mobile_frontdoor_ready="no"
fi

toolbox_tailscale_output="$(timeout 15 ./scripts/toolbox_tailscale_check.sh 2>/dev/null || true)"
pbs_stage_output="$(timeout 15 ./scripts/pbs_stage_gate_check.sh 2>/dev/null || true)"
gateway_gate_output="$(timeout 15 ./scripts/gateway_cutover_stage_gate_check.sh 2>/dev/null || true)"
rightsize_stage_output="$(timeout 20 ./scripts/rightsize_stage_gate_check.sh 2>/dev/null || true)"
surface_go_output="$(timeout 15 ./scripts/surface_go_frontend_check.sh 2>/dev/null || true)"
adguard_pilot_output="$(timeout 10 ./scripts/adguard_pilot_readiness_check.sh 2>/dev/null || true)"
split_dns_output="$(timeout 10 ./scripts/tailscale_split_dns_readiness_check.sh 2>/dev/null || true)"
inventory_resolution_output="$(timeout 10 ./scripts/inventory_resolution_check.sh 2>/dev/null || true)"
easybox_probe_output="$(timeout 25 ./scripts/easybox_browser_probe.sh 2>/dev/null || true)"

tailnet_route_visible="$(extract_value tailnet_route_visible "${toolbox_tailscale_output}")"
pbs_stage_gate_ready="$(extract_value pbs_stage_gate_ready "${pbs_stage_output}")"
inventory_unknown_review_count="$(extract_value inventory_unknown_review_count "${gateway_gate_output}")"
rightsize_stage_gate_ready="$(extract_value rightsize_stage_gate_ready "${rightsize_stage_output}")"
surface_go_remote_admin_ready="$(extract_value surface_go_remote_admin_ready "${surface_go_output}")"
surface_go_clean_rebuild_required="$(extract_value surface_go_clean_rebuild_required "${surface_go_output}")"
adguard_pilot_ready="$(extract_value adguard_pilot_ready "${adguard_pilot_output}")"
split_dns_prereqs_ready="$(extract_value split_dns_prereqs_ready "${split_dns_output}")"
inventory_resolution_ready="$(extract_value inventory_resolution_ready "${inventory_resolution_output}")"
unresolved_router_labels="$(extract_value unresolved_router_labels "${inventory_resolution_output}")"
easybox_remote_admin_possible="$(extract_value browser_probe_ready "${easybox_probe_output}")"

if [[ -f "${SURFACE_ISO}" ]]; then
  surface_iso_present="yes"
  surface_iso_bytes="$(stat -c '%s' "${SURFACE_ISO}")"
  surface_iso_gib="$(awk -v bytes="${surface_iso_bytes}" 'BEGIN {printf "%.2f", bytes/1024/1024/1024}')"
  if (( surface_iso_bytes >= SURFACE_ISO_MIN_BYTES )); then
    surface_iso_download_complete="yes"
  else
    surface_iso_download_complete="no"
  fi
else
  surface_iso_present="no"
  surface_iso_bytes="0"
  surface_iso_gib="0.00"
  surface_iso_download_complete="no"
fi

remote_only_window_ready="yes"
if [[ "${zenbook_anydesk_active}" != "yes" || "${zenbook_tailscale_joined}" != "yes" ]]; then
  remote_only_window_ready="no"
fi

echo "zenbook_anydesk_active=${zenbook_anydesk_active}"
echo "zenbook_tailscaled_active=${zenbook_tailscaled_active}"
echo "zenbook_tailscale_joined=${zenbook_tailscale_joined}"
echo "zenbook_tailscale_ipv4=${zenbook_tailscale_ipv4}"
echo "toolbox_mobile_frontdoor_ready=${toolbox_mobile_frontdoor_ready}"
echo "toolbox_mobile_frontdoor_http=${toolbox_mobile_frontdoor_http:-000}"
echo "easybox_remote_admin_possible=${easybox_remote_admin_possible}"
echo "tailnet_route_visible=${tailnet_route_visible:-unknown}"
echo "inventory_unknown_review_count=${inventory_unknown_review_count:-unknown}"
echo "pbs_stage_gate_ready=${pbs_stage_gate_ready:-unknown}"
echo "rightsize_stage_gate_ready=${rightsize_stage_gate_ready:-unknown}"
echo "adguard_pilot_ready=${adguard_pilot_ready:-unknown}"
echo "split_dns_prereqs_ready=${split_dns_prereqs_ready:-unknown}"
echo "inventory_resolution_ready=${inventory_resolution_ready:-unknown}"
echo "unresolved_router_labels=${unresolved_router_labels:-unknown}"
echo "surface_go_remote_admin_ready=${surface_go_remote_admin_ready:-unknown}"
echo "surface_go_clean_rebuild_required=${surface_go_clean_rebuild_required:-unknown}"
echo "surface_iso_present=${surface_iso_present}"
echo "surface_iso_gib=${surface_iso_gib}"
echo "surface_iso_download_complete=${surface_iso_download_complete}"
echo "remote_only_window_ready=${remote_only_window_ready}"

if [[ "${remote_only_window_ready}" != "yes" ]]; then
  echo "recommendation=fix_remote_admin_path_before_using_remote_only_window"
elif [[ "${tailnet_route_visible:-no}" != "yes" ]]; then
  echo "recommendation=approve_toolbox_subnet_route_then_run_phone_and_easybox_checks"
elif [[ "${split_dns_prereqs_ready:-no}" != "yes" ]]; then
  echo "recommendation=apply_hs27_internal_split_dns_in_tailscale_admin"
elif [[ "${inventory_unknown_review_count:-0}" != "0" ]]; then
  echo "recommendation=use_remote_window_for_easybox_lease_reconciliation"
elif [[ "${adguard_pilot_ready:-no}" != "yes" ]]; then
  echo "recommendation=close_adguard_pilot_readiness_before_client_dns_changes"
elif [[ "${surface_iso_download_complete}" != "yes" ]]; then
  echo "recommendation=resume_surface_iso_download_while_remote_only_window_is_open"
else
  echo "recommendation=remote_only_window_is_clear_for_documentation_or_maintenance_window_work"
fi

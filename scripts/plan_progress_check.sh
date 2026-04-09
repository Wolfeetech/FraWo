#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

clamp_percent() {
  local value="$1"
  if (( value < 0 )); then
    echo 0
  elif (( value > 100 )); then
    echo 100
  else
    echo "$value"
  fi
}

toolbox_network_output="$("${ROOT_DIR}/scripts/toolbox_network_check.sh")"
toolbox_tailscale_output="$("${ROOT_DIR}/scripts/toolbox_tailscale_check.sh")"
haos_output="$("${ROOT_DIR}/scripts/haos_stage_gate_check.sh")"
pbs_output="$("${ROOT_DIR}/scripts/pbs_stage_gate_check.sh")"
inventory_output="$("${ROOT_DIR}/scripts/inventory_resolution_check.sh")"
surface_output="$("${ROOT_DIR}/scripts/surface_go_frontend_check.sh")"
radio_output="$("${ROOT_DIR}/scripts/radio_operations_check.sh")"
media_output="$("${ROOT_DIR}/scripts/toolbox_media_server_check.sh")"
security_output="$("${ROOT_DIR}/scripts/security_baseline_check.sh")"

phase_1=100
phase_2=100

phase_3=55
[[ "$(extract_value toolbox_internal_services_ok "${toolbox_network_output}")" == "yes" ]] && phase_3=$((phase_3 + 15))
[[ "$(extract_value toolbox_tailscale_frontdoor_ok "${toolbox_network_output}")" == "yes" ]] && phase_3=$((phase_3 + 10))
[[ "$(extract_value tailnet_route_visible "${toolbox_tailscale_output}")" == "yes" ]] && phase_3=$((phase_3 + 10))
[[ "$(extract_value security_status "${security_output}")" == "ok" ]] && phase_3=$((phase_3 + 10))
phase_3="$(clamp_percent "${phase_3}")"

phase_4=40
[[ "$(extract_value haos_stage_gate_ready "${haos_output}")" == "yes" ]] && phase_4=$((phase_4 + 35))
[[ "$(extract_value haos_vm_status "${haos_output}")" == "running" ]] && phase_4=$((phase_4 + 15))
[[ "$(extract_value usb_passthrough_ready "${haos_output}")" == "yes" ]] && phase_4=$((phase_4 + 10))
phase_4="$(clamp_percent "${phase_4}")"

phase_5=35
[[ "$(extract_value backup_timer_live "${pbs_output}")" == "yes" ]] && phase_5=$((phase_5 + 15))
[[ "$(extract_value local_backup_archives_present "${pbs_output}")" == "yes" ]] && phase_5=$((phase_5 + 15))
[[ "$(extract_value pbs_stage_gate_ready "${pbs_output}")" == "yes" ]] && phase_5=$((phase_5 + 35))
phase_5="$(clamp_percent "${phase_5}")"

phase_6=35
unknown_count="$(extract_value inventory_unknown_review_count "${inventory_output}")"
if [[ -n "${unknown_count}" && "${unknown_count}" =~ ^[0-9]+$ ]]; then
  deduction=$(( unknown_count * 5 ))
  if (( deduction > 25 )); then
    deduction=25
  fi
  phase_6=$((phase_6 + 40 - deduction))
fi
[[ "$(extract_value inventory_resolution_ready "${inventory_output}")" == "yes" ]] && phase_6=100
phase_6="$(clamp_percent "${phase_6}")"

phase_6a=65
[[ "$(extract_value surface_go_inventory_present "${surface_output}")" == "yes" ]] && phase_6a=$((phase_6a + 5))
[[ "$(extract_value surface_go_clean_rebuild_required "${surface_output}")" == "no" ]] && phase_6a=$((phase_6a + 15))
[[ "$(extract_value surface_go_remote_admin_ready "${surface_output}")" == "yes" ]] && phase_6a=$((phase_6a + 10))
phase_6a="$(clamp_percent "${phase_6a}")"

phase_6b=45
[[ "$(extract_value radio_operations_ready "${radio_output}")" == "yes" ]] && phase_6b=$((phase_6b + 35))
[[ "$(extract_value radio_station_online "${radio_output}")" == "true" ]] && phase_6b=$((phase_6b + 10))
phase_6b="$(clamp_percent "${phase_6b}")"

phase_6c=40
[[ "$(extract_value toolbox_media_server_ready "${media_output}")" == "yes" ]] && phase_6c=$((phase_6c + 35))
phase_6c=$((phase_6c + 10))
phase_6c="$(clamp_percent "${phase_6c}")"

phase_7=0
phase_8=10

total_percent=$(( (phase_1 + phase_2 + phase_3 + phase_4 + phase_5 + phase_6 + phase_6a + phase_6b + phase_6c + phase_7 + phase_8) / 11 ))

echo "phase_1_foundation=${phase_1}"
echo "phase_2_business_platform=${phase_2}"
echo "phase_3_internal_network=${phase_3}"
echo "phase_4_haos=${phase_4}"
echo "phase_5_backup_dr=${phase_5}"
echo "phase_6_inventory_governance=${phase_6}"
echo "phase_6a_surface_frontend=${phase_6a}"
echo "phase_6b_radio_node=${phase_6b}"
echo "phase_6c_media_server=${phase_6c}"
echo "phase_7_gateway_cutover=${phase_7}"
echo "phase_8_public_edge=${phase_8}"
echo "masterplan_progress_percent=${total_percent}"

if (( total_percent >= 80 )); then
  echo "progress_band=late_stage"
elif (( total_percent >= 60 )); then
  echo "progress_band=mid_stage"
else
  echo "progress_band=early_stage"
fi

if [[ "$(extract_value surface_go_remote_admin_ready "${surface_output}")" != "yes" ]]; then
  echo "recommendation=wake_surface_and_finish_frontend_acceptance"
elif [[ "$(extract_value pbs_stage_gate_ready "${pbs_output}")" != "yes" ]]; then
  echo "recommendation=provide_pbs_storage_and_finish_backup_architecture"
elif [[ "$(extract_value toolbox_media_server_ready "${media_output}")" == "yes" ]]; then
  echo "recommendation=finish_jellyfin_ui_setup_and_client_rollout"
else
  echo "recommendation=continue_core_platform_rollout"
fi

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_HOST="${TARGET_HOST:-${1:-100.64.23.77}}"

extract_value() {
  local key="$1"
  local input="$2"
  printf '%s\n' "${input}" | awk -F= -v key="$key" '$1 == key {sub($1 FS, ""); print; exit}'
}

readiness_output="$(${ROOT_DIR}/scripts/rpi_radio_readiness_check.sh "${TARGET_HOST}" 2>&1 || true)"
service_output="$(${ROOT_DIR}/scripts/rpi_azuracast_service_check.sh "${TARGET_HOST}" 2>&1 || true)"
ops_output="$(${ROOT_DIR}/scripts/radio_operations_check.sh 2>&1 || true)"

readiness_gate="$(extract_value rpi_radio_ready_for_azuracast "${readiness_output}")"
service_gate="$(extract_value rpi_azuracast_service_ready "${service_output}")"
ops_gate="$(extract_value radio_operations_ready "${ops_output}")"

station_online="$(extract_value azuracast_station_online "${service_output}")"
nowplaying_ready="$(extract_value radio_nowplaying_ready "${ops_output}")"
control_ready="$(extract_value radio_control_ready "${ops_output}")"
internal_ready="$(extract_value radio_internal_ready "${ops_output}")"

readiness_gate="${readiness_gate:-no}"
service_gate="${service_gate:-no}"
ops_gate="${ops_gate:-no}"
station_online="${station_online:-unknown}"
nowplaying_ready="${nowplaying_ready:-no}"
control_ready="${control_ready:-no}"
internal_ready="${internal_ready:-no}"

echo "radio_daily_target_host=${TARGET_HOST}"
echo "radio_daily_readiness_gate=${readiness_gate}"
echo "radio_daily_service_gate=${service_gate}"
echo "radio_daily_ops_gate=${ops_gate}"
echo "radio_kpi_internal_ui_ready=${internal_ready}"
echo "radio_kpi_control_ui_ready=${control_ready}"
echo "radio_kpi_nowplaying_ready=${nowplaying_ready}"
echo "radio_kpi_station_online=${station_online}"

if [[ "${readiness_gate}" == "yes" \
   && "${service_gate}" == "yes" \
   && "${ops_gate}" == "yes" \
   && "${internal_ready}" == "yes" \
   && "${nowplaying_ready}" == "yes" \
   && "${station_online}" == "true" ]]; then
  echo "radio_daily_gate=go"
  echo "recommendation=continue_normal_operations_and_content_curation"
  exit 0
fi

echo "radio_daily_gate=no-go"
if [[ "${readiness_gate}" != "yes" ]]; then
  echo "recommendation=fix_radio_node_readiness_before_any_runtime_changes"
elif [[ "${service_gate}" != "yes" ]]; then
  echo "recommendation=repair_azuracast_service_health_before_opening_operations"
elif [[ "${ops_gate}" != "yes" ]]; then
  echo "recommendation=repair_internal_paths_or_api_before_control_surface_use"
else
  echo "recommendation=check_station_playback_and_nowplaying_pipeline"
fi

exit 1

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TARGET_HOST="${1:-100.64.23.77}"

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

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "${data}" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

http_ok() {
  local code="$1"
  [[ "${code}" == "200" || "${code}" == "302" ]]
}

readiness_output="$(timeout 60 "${ROOT_DIR}/scripts/rpi_radio_readiness_check.sh" "${TARGET_HOST}" 2>/dev/null || true)"
service_output="$(timeout 60 "${ROOT_DIR}/scripts/rpi_azuracast_service_check.sh" "${TARGET_HOST}" 2>/dev/null || true)"
resource_output="$(timeout 60 "${ROOT_DIR}/scripts/rpi_resource_budget_check.sh" "${TARGET_HOST}" 2>/dev/null || true)"
media_output="$(timeout 60 "${ROOT_DIR}/scripts/rpi_radio_media_layout_check.sh" "${TARGET_HOST}" 2>/dev/null || true)"
network_output="$(timeout 60 "${ROOT_DIR}/scripts/rpi_radio_network_music_check.sh" "${TARGET_HOST}" 2>/dev/null || true)"

radio_internal_proxy_http="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 http://radio.hs27.internal/ || true)"
radio_mobile_frontdoor_http="$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 http://${TOOLBOX_FRONTDOOR_IP}:8448/ || true)"

rpi_radio_ready="$(extract_value rpi_radio_ready_for_azuracast "${readiness_output}")"
rpi_azuracast_service_ready="$(extract_value rpi_azuracast_service_ready "${service_output}")"
rpi_resource_profile_ready="$(extract_value rpi_resource_profile_ready "${resource_output}")"
rpi_radio_media_layout_ready="$(extract_value rpi_radio_media_layout_ready "${media_output}")"
rpi_radio_network_music_ready="$(extract_value rpi_radio_network_music_ready "${network_output}")"
radio_node_http_code="$(extract_value radio_node_http_code "${service_output}")"
radio_node_http_location="$(extract_value radio_node_http_location "${service_output}")"
azuracast_initial_setup_complete="$(extract_value azuracast_initial_setup_complete "${service_output}")"
azuracast_login_ready="$(extract_value azuracast_login_ready "${service_output}")"
azuracast_station_count="$(extract_value azuracast_station_count "${service_output}")"
azuracast_first_station_present="$(extract_value azuracast_first_station_present "${service_output}")"
azuracast_station_name="$(extract_value azuracast_station_name "${service_output}")"
azuracast_station_shortcode="$(extract_value azuracast_station_shortcode "${service_output}")"
azuracast_station_online="$(extract_value azuracast_station_online "${service_output}")"
azuracast_current_song="$(extract_value azuracast_current_song "${service_output}")"

if http_ok "${radio_internal_proxy_http}"; then
  radio_internal_proxy_ready="yes"
else
  radio_internal_proxy_ready="no"
fi

if http_ok "${radio_mobile_frontdoor_http}"; then
  radio_mobile_frontdoor_ready="yes"
else
  radio_mobile_frontdoor_ready="no"
fi

echo "target_host=${TARGET_HOST}"
echo "rpi_radio_ready_for_azuracast=${rpi_radio_ready:-unknown}"
echo "rpi_azuracast_service_ready=${rpi_azuracast_service_ready:-unknown}"
echo "rpi_resource_profile_ready=${rpi_resource_profile_ready:-unknown}"
echo "rpi_radio_media_layout_ready=${rpi_radio_media_layout_ready:-unknown}"
echo "rpi_radio_network_music_ready=${rpi_radio_network_music_ready:-unknown}"
echo "rpi_radio_usb_music_ready=${rpi_radio_network_music_ready:-unknown}"
echo "radio_node_http_code=${radio_node_http_code:-unknown}"
echo "radio_node_http_location=${radio_node_http_location:-unknown}"
echo "azuracast_initial_setup_complete=${azuracast_initial_setup_complete:-unknown}"
echo "azuracast_login_ready=${azuracast_login_ready:-unknown}"
echo "azuracast_station_count=${azuracast_station_count:-unknown}"
echo "azuracast_first_station_present=${azuracast_first_station_present:-unknown}"
echo "azuracast_station_name=${azuracast_station_name:-unknown}"
echo "azuracast_station_shortcode=${azuracast_station_shortcode:-unknown}"
echo "azuracast_station_online=${azuracast_station_online:-unknown}"
echo "azuracast_current_song=${azuracast_current_song:-unknown}"
echo "radio_internal_proxy_http=${radio_internal_proxy_http:-000}"
echo "radio_internal_proxy_ready=${radio_internal_proxy_ready}"
echo "radio_mobile_frontdoor_http=${radio_mobile_frontdoor_http:-000}"
echo "radio_mobile_frontdoor_ready=${radio_mobile_frontdoor_ready}"

if [[ "${rpi_radio_ready:-no}" == "yes" \
   && "${rpi_azuracast_service_ready:-no}" == "yes" \
   && "${rpi_resource_profile_ready:-no}" == "yes" \
   && "${rpi_radio_media_layout_ready:-no}" == "yes" \
   && "${rpi_radio_network_music_ready:-no}" == "yes" \
   && "${radio_internal_proxy_ready}" == "yes" \
   && "${radio_mobile_frontdoor_ready}" == "yes" ]]; then
  echo "rpi_radio_integrated=yes"
  if [[ "${azuracast_initial_setup_complete:-unknown}" == "no" ]]; then
    echo "recommendation=complete_initial_web_setup_then_finalize_media_mounts"
  elif [[ "${azuracast_first_station_present:-unknown}" == "no" ]]; then
    echo "recommendation=create_first_station_then_finalize_media_layout"
  elif [[ "${azuracast_station_online:-unknown}" == "true" ]]; then
    echo "recommendation=radio_node_is_integrated_and_playing_from_network_music"
  else
    echo "recommendation=finish_station_playback_before_relying_on_radio_node"
  fi
else
  echo "rpi_radio_integrated=no"
  echo "recommendation=finish_proxy_mobile_resource_or_network_music_integration_before_relying_on_radio_node"
fi

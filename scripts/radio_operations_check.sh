#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
service_output="$(timeout 20 "${ROOT_DIR}/scripts/rpi_azuracast_service_check.sh" 2>/dev/null || true)"

extract_value() {
  local key="$1"
  printf '%s\n' "${service_output}" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

internal_root_http="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://radio.hs27.internal/ || true)"
control_login_http="$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://radio.hs27.internal/login || true)"
nowplaying_http="$(curl -s -o /tmp/homeserver2027_radio_nowplaying.json -w '%{http_code}' --max-time 10 http://radio.hs27.internal/api/nowplaying || true)"
station_count="$(jq 'length' /tmp/homeserver2027_radio_nowplaying.json 2>/dev/null || echo unknown)"
station_name="$(extract_value azuracast_station_name)"
station_shortcode="$(extract_value azuracast_station_shortcode)"
station_online="$(extract_value azuracast_station_online)"
current_song="$(extract_value azuracast_current_song)"

echo "radio_internal_root_http=${internal_root_http:-000}"
echo "radio_control_login_http=${control_login_http:-000}"
echo "radio_nowplaying_http=${nowplaying_http:-000}"
echo "radio_station_count=${station_count:-unknown}"
echo "radio_station_name=${station_name:-unknown}"
echo "radio_station_shortcode=${station_shortcode:-unknown}"
echo "radio_station_online=${station_online:-unknown}"
echo "radio_current_song=${current_song:-unknown}"

if [[ "${internal_root_http:-000}" =~ ^(200|302)$ ]]; then
  echo "radio_internal_ready=yes"
else
  echo "radio_internal_ready=no"
fi

if [[ "${control_login_http:-000}" =~ ^(200|302)$ ]]; then
  echo "radio_control_ready=yes"
else
  echo "radio_control_ready=no"
fi

if [[ "${nowplaying_http:-000}" == "200" && "${station_count:-unknown}" =~ ^[0-9]+$ && "${station_count}" -gt 0 ]]; then
  echo "radio_nowplaying_ready=yes"
else
  echo "radio_nowplaying_ready=no"
fi

if [[ "${internal_root_http:-000}" =~ ^(200|302)$ && "${control_login_http:-000}" =~ ^(200|302)$ && "${nowplaying_http:-000}" == "200" ]]; then
  echo "radio_operations_ready=yes"
  if [[ "${station_online:-unknown}" == "true" ]]; then
    echo "recommendation=continue_library_curation_and_build_surface_monitor_views"
  else
    echo "recommendation=inspect_station_playback_state_before_surface_radio_control_rollout"
  fi
else
  echo "radio_operations_ready=no"
  echo "recommendation=repair_internal_radio_or_control_paths_before_surface_monitor_rollout"
fi

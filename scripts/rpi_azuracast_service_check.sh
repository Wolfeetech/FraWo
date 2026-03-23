#!/usr/bin/env bash
set -euo pipefail

TARGET_HOST="${1:-100.64.23.77}"
SSH_TARGET="wolf@${TARGET_HOST}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new)

run_remote() {
  ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" "$@"
}

echo "hostname=$(run_remote "hostname" 2>/dev/null || echo unknown)"

if run_remote "test -f /var/azuracast/docker-compose.yml" 2>/dev/null; then
  echo "azuracast_compose_present=yes"
else
  echo "azuracast_compose_present=no"
fi

echo "docker_ps_start"
run_remote "docker ps --format '{{.Names}}\t{{.Status}}'" 2>/dev/null || true
echo "docker_ps_end"

headers="$(curl -s -I --max-time 10 "http://${TARGET_HOST}/" | tr -d '\r' || true)"
http_code="$(printf '%s\n' "${headers}" | awk 'NR==1 {print $2}' | head -n1)"
http_location="$(printf '%s\n' "${headers}" | awk -F': ' 'tolower($1)=="location" {print $2}' | tail -n1)"
api_status_http="$(curl -s -o /tmp/homeserver2027_rpi_azuracast_status.json -w '%{http_code}' --max-time 10 "http://${TARGET_HOST}/api/status" || true)"
api_status_online="$(jq -r '.online // "unknown"' /tmp/homeserver2027_rpi_azuracast_status.json 2>/dev/null || echo unknown)"
nowplaying_http="$(curl -s -o /tmp/homeserver2027_rpi_azuracast_nowplaying.json -w '%{http_code}' --max-time 10 "http://${TARGET_HOST}/api/nowplaying" || true)"
station_count="$(jq 'length' /tmp/homeserver2027_rpi_azuracast_nowplaying.json 2>/dev/null || echo unknown)"
station_name="$(jq -r '.[0].station.name // "unknown"' /tmp/homeserver2027_rpi_azuracast_nowplaying.json 2>/dev/null || echo unknown)"
station_shortcode="$(jq -r '.[0].station.shortcode // "unknown"' /tmp/homeserver2027_rpi_azuracast_nowplaying.json 2>/dev/null || echo unknown)"
station_online="$(jq -r '.[0].is_online // "unknown"' /tmp/homeserver2027_rpi_azuracast_nowplaying.json 2>/dev/null || echo unknown)"
station_song="$(jq -r '.[0].now_playing.song.text // "unknown"' /tmp/homeserver2027_rpi_azuracast_nowplaying.json 2>/dev/null || echo unknown)"

echo "radio_node_http_code=${http_code:-000}"
echo "radio_node_http_location=${http_location:-none}"
echo "azuracast_api_status_http=${api_status_http:-000}"
echo "azuracast_api_online=${api_status_online:-unknown}"
echo "azuracast_nowplaying_http=${nowplaying_http:-000}"
echo "azuracast_station_count=${station_count:-unknown}"
echo "azuracast_station_name=${station_name:-unknown}"
echo "azuracast_station_shortcode=${station_shortcode:-unknown}"
echo "azuracast_station_online=${station_online:-unknown}"
echo "azuracast_current_song=${station_song:-unknown}"

if [[ "${http_location:-}" == "/setup" ]]; then
  echo "azuracast_initial_setup_complete=no"
  echo "azuracast_login_ready=no"
  echo "azuracast_first_station_present=unknown"
elif [[ "${api_status_http:-000}" == "200" && "${api_status_online:-unknown}" == "true" ]]; then
  echo "azuracast_initial_setup_complete=yes"
  echo "azuracast_login_ready=yes"
  if [[ "${station_count:-unknown}" =~ ^[0-9]+$ ]] && (( station_count > 0 )); then
    echo "azuracast_first_station_present=yes"
  else
    echo "azuracast_first_station_present=no"
  fi
else
  echo "azuracast_initial_setup_complete=unknown"
  echo "azuracast_login_ready=unknown"
  echo "azuracast_first_station_present=unknown"
fi

if [[ "${http_code:-000}" =~ ^(200|302|401|403)$ && "${api_status_http:-000}" == "200" ]]; then
  echo "rpi_azuracast_service_ready=yes"
  if [[ "${http_location:-}" == "/setup" ]]; then
    echo "recommendation=complete_initial_web_setup_then_finalize_media_mounts"
  elif [[ "${station_count:-unknown}" =~ ^[0-9]+$ ]] && (( station_count == 0 )); then
    echo "recommendation=create_first_station_then_finalize_media_layout"
  elif [[ "${station_online:-unknown}" == "true" ]]; then
    echo "recommendation=station_live_verify_media_import_and_continue_library_curation"
  else
    echo "recommendation=finish_media_import_and_station_playback_before_relying_on_radio_node"
  fi
else
  echo "rpi_azuracast_service_ready=no"
  echo "recommendation=inspect_containers_before_dns_cutover"
fi

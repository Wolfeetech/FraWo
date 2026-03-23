#!/usr/bin/env bash
set -euo pipefail

TARGET_HOST="${1:-100.64.23.77}"
SSH_TARGET="wolf@${TARGET_HOST}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new)

run_remote() {
  ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" "$@"
}

mountpoint="/srv/radio-library/music-usb"
source_subdir="${mountpoint}/yourparty.radio"
container_media="/var/azuracast/stations/frawo-funk/media"

mount_state="no"
if run_remote "findmnt -T ${mountpoint@Q} >/dev/null 2>&1" 2>/dev/null; then
  mount_state="yes"
fi

mount_options="$(run_remote "findmnt -no OPTIONS -T ${mountpoint@Q}" 2>/dev/null | tr -d '\r' || true)"
mount_mode="unknown"
if [[ "${mount_options}" == *"rw"* ]]; then
  mount_mode="rw"
elif [[ "${mount_options}" == *"ro"* ]]; then
  mount_mode="ro"
fi

override_present="no"
if run_remote "test -f /var/azuracast/docker-compose.override.yml" 2>/dev/null; then
  override_present="yes"
fi

host_file_count="$(run_remote "find ${source_subdir@Q} -type f | wc -l" 2>/dev/null | tr -d ' ' || echo 0)"
container_file_count="$(run_remote "sudo docker exec azuracast sh -lc 'find ${container_media@Q} -type f | wc -l'" 2>/dev/null | tr -d ' ' || echo 0)"
station_media_count="$(run_remote "sudo docker exec azuracast azuracast_cli dbal:run-sql --force-fetch 'SELECT COUNT(*) AS media_count FROM station_media;' | awk '/^[[:space:]]+[0-9]+[[:space:]]*$/ {print \$1; exit}'" 2>/dev/null | tr -d ' ' || echo 0)"
playlist_media_count="$(run_remote "sudo docker exec azuracast azuracast_cli dbal:run-sql --force-fetch 'SELECT COUNT(*) AS spm_count FROM station_playlist_media;' | awk '/^[[:space:]]+[0-9]+[[:space:]]*$/ {print \$1; exit}'" 2>/dev/null | tr -d ' ' || echo 0)"

echo "target_host=${TARGET_HOST}"
echo "radio_usb_mount_ready=${mount_state}"
echo "radio_usb_mount_mode=${mount_mode}"
echo "radio_usb_override_present=${override_present}"
echo "radio_usb_source_subdir=${source_subdir}"
echo "radio_usb_host_file_count=${host_file_count:-0}"
echo "radio_usb_container_file_count=${container_file_count:-0}"
echo "radio_usb_station_media_count=${station_media_count:-0}"
echo "radio_usb_playlist_media_count=${playlist_media_count:-0}"

if [[ "${mount_state}" == "yes" && "${mount_mode}" == "rw" && "${override_present}" == "yes" && "${host_file_count:-0}" =~ ^[0-9]+$ && "${container_file_count:-0}" =~ ^[0-9]+$ && "${station_media_count:-0}" =~ ^[0-9]+$ && "${playlist_media_count:-0}" =~ ^[0-9]+$ && ${host_file_count:-0} -gt 0 && ${container_file_count:-0} -gt 0 && ${station_media_count:-0} -gt 0 && ${playlist_media_count:-0} -gt 0 ]]; then
  echo "rpi_radio_usb_music_ready=yes"
  echo "recommendation=usb_music_integrated_continue_media_import_and_playlist_curation"
else
  echo "rpi_radio_usb_music_ready=no"
  echo "recommendation=use_rw_usb_media_binding_and_complete_playlist_assignment_before_relying_on_station_content"
fi

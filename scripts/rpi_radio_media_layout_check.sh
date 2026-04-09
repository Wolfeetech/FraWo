#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/rpi_radio_remote.sh"

TARGET_HOST="${1:-100.64.23.77}"

run_remote() {
  run_rpi_remote "${TARGET_HOST}" "$@"
}

check_dir() {
  local path="$1"
  if run_remote "test -d ${path@Q}" 2>/dev/null; then
    echo "yes"
  else
    echo "no"
  fi
}

library_root="/srv/radio-library"
assets_root="/srv/radio-assets"

echo "target_host=${TARGET_HOST}"
echo "radio_library_root_ready=$(check_dir "${library_root}")"
echo "radio_assets_root_ready=$(check_dir "${assets_root}")"
echo "radio_library_incoming_ready=$(check_dir "${library_root}/incoming")"
echo "radio_library_music_ready=$(check_dir "${library_root}/music")"
echo "radio_library_playlists_ready=$(check_dir "${library_root}/playlists")"
echo "radio_assets_ids_ready=$(check_dir "${assets_root}/ids")"
echo "radio_assets_jingles_ready=$(check_dir "${assets_root}/jingles")"
echo "radio_assets_shows_ready=$(check_dir "${assets_root}/shows")"
echo "radio_assets_staging_ready=$(check_dir "${assets_root}/staging")"
echo "radio_assets_sweepers_ready=$(check_dir "${assets_root}/sweepers")"

if run_remote "test -f ${library_root@Q}/README.txt && test -f ${assets_root@Q}/README.txt" 2>/dev/null; then
  echo "radio_media_readmes_ready=yes"
else
  echo "radio_media_readmes_ready=no"
fi

if run_remote "test -d ${library_root@Q}/incoming && test -d ${library_root@Q}/music && test -d ${library_root@Q}/playlists && test -d ${assets_root@Q}/ids && test -d ${assets_root@Q}/jingles && test -d ${assets_root@Q}/shows && test -d ${assets_root@Q}/staging && test -d ${assets_root@Q}/sweepers && test -f ${library_root@Q}/README.txt && test -f ${assets_root@Q}/README.txt" 2>/dev/null; then
  echo "rpi_radio_media_layout_ready=yes"
  echo "recommendation=keep_station_media_curated_then_bind_final_network_source_of_truth"
else
  echo "rpi_radio_media_layout_ready=no"
  echo "recommendation=apply_media_layout_playbook_before_binding_station_media"
fi

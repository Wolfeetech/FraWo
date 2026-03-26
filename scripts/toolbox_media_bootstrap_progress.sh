#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/rpi_radio_remote.sh"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

TARGET_HOST="${1:-100.64.23.77}"
SOURCE_PATH="/srv/radio-library/music-network/yourparty_Libary"
TARGET_PATH="/srv/media-library/music-network/yourparty_Libary"

human_bytes() {
  local bytes="${1:-0}"
  if command -v numfmt >/dev/null 2>&1; then
    numfmt --to=iec --suffix=B "${bytes}" 2>/dev/null || printf '%sB\n' "${bytes}"
  else
    printf '%sB\n' "${bytes}"
  fi
}

percent_of() {
  local part="${1:-0}"
  local total="${2:-0}"
  if [[ -z "${total}" || "${total}" == "0" ]]; then
    echo "0"
    return
  fi
  awk -v part="${part}" -v total="${total}" 'BEGIN { printf "%.1f", (part / total) * 100 }'
}

source_file_count="$(run_rpi_remote "${TARGET_HOST}" "find '${SOURCE_PATH}' -type f 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
source_size_bytes="$(run_rpi_remote "${TARGET_HOST}" "du -sb '${SOURCE_PATH}' 2>/dev/null | awk '{print \$1}'" 2>/dev/null || echo 0)"
target_file_count="$(run_toolbox_remote "find '${TARGET_PATH}' -type f 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
target_size_bytes="$(run_toolbox_remote "du -sb '${TARGET_PATH}' 2>/dev/null | awk '{print \$1}'" 2>/dev/null || echo 0)"
sync_service_state="retired"
sync_timer_state="retired"
rootfs_free_bytes="$(run_toolbox_remote "df -B1 / | awk 'NR==2 {print \$4}'" 2>/dev/null || echo 0)"

file_count_percent="$(percent_of "${target_file_count}" "${source_file_count}")"
size_percent="$(percent_of "${target_size_bytes}" "${source_size_bytes}")"

echo "toolbox_media_bootstrap_source_file_count=${source_file_count:-0}"
echo "toolbox_media_bootstrap_source_size_bytes=${source_size_bytes:-0}"
echo "toolbox_media_bootstrap_source_size_human=$(human_bytes "${source_size_bytes:-0}")"
echo "toolbox_media_bootstrap_target_file_count=${target_file_count:-0}"
echo "toolbox_media_bootstrap_target_size_bytes=${target_size_bytes:-0}"
echo "toolbox_media_bootstrap_target_size_human=$(human_bytes "${target_size_bytes:-0}")"
echo "toolbox_media_bootstrap_file_progress_percent=${file_count_percent}"
echo "toolbox_media_bootstrap_size_progress_percent=${size_percent}"
echo "toolbox_media_bootstrap_sync_service_state=${sync_service_state:-unknown}"
echo "toolbox_media_bootstrap_sync_timer_state=${sync_timer_state:-unknown}"
echo "toolbox_media_bootstrap_rootfs_free_bytes=${rootfs_free_bytes:-0}"
echo "toolbox_media_bootstrap_rootfs_free_human=$(human_bytes "${rootfs_free_bytes:-0}")"

if [[ "${target_size_bytes:-0}" =~ ^[0-9]+$ ]] && [[ "${target_size_bytes:-0}" -gt 0 ]]; then
  echo "toolbox_media_bootstrap_progress_ready=yes"
else
  echo "toolbox_media_bootstrap_progress_ready=no"
fi

if [[ "${target_size_bytes:-0}" == "${source_size_bytes:-0}" && "${source_size_bytes:-0}" != "0" ]]; then
  echo "recommendation=toolbox_and_radio_point_to_the_same_central_media_path"
else
  echo "recommendation=verify_toolbox_mount_or_radio_source_against_central_media_path"
fi

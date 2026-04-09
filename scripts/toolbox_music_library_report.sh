#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

TARGET_PATH="/srv/media-library/music-network/yourparty_Libary"

echo "toolbox_music_library_path=${TARGET_PATH}"

total_files="$(run_toolbox_remote "find '${TARGET_PATH}' -type f 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
total_dirs="$(run_toolbox_remote "find '${TARGET_PATH}' -type d 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
total_size="$(run_toolbox_remote "du -sh '${TARGET_PATH}' 2>/dev/null | awk '{print \$1}'" 2>/dev/null || echo 0)"
sync_state="retired"
progress_percent="$(./scripts/toolbox_media_bootstrap_progress.sh 2>/dev/null | awk -F= '/^toolbox_media_bootstrap_size_progress_percent=/{print $2}')"

echo "toolbox_music_library_total_files=${total_files:-0}"
echo "toolbox_music_library_total_dirs=${total_dirs:-0}"
echo "toolbox_music_library_total_size=${total_size:-0}"
echo "toolbox_music_library_sync_state=${sync_state:-unknown}"
echo "toolbox_music_library_bootstrap_size_progress_percent=${progress_percent:-0}"

echo "toolbox_music_library_top_level_dirs=$(run_toolbox_remote "find '${TARGET_PATH}' -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort | paste -sd, -" 2>/dev/null || echo none)"

while IFS= read -r line; do
  echo "${line}"
done < <(
  run_toolbox_remote "
    find '${TARGET_PATH}' -type f 2>/dev/null \
      | awk '
          {
            ext=\$0
            sub(/^.*\\./, \"\", ext)
            ext=tolower(ext)
            counts[ext]++
          }
          END {
            for (ext in counts) printf \"toolbox_music_library_ext_%s=%d\\n\", ext, counts[ext]
          }
        ' \
      | sort
  " 2>/dev/null || true
)

restrictive_dirs="$(run_toolbox_remote "find '${TARGET_PATH}' -type d ! -perm -0005 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
restrictive_files="$(run_toolbox_remote "find '${TARGET_PATH}' -type f ! -perm -0004 2>/dev/null | wc -l" 2>/dev/null || echo 0)"

echo "toolbox_music_library_restrictive_dirs=${restrictive_dirs:-0}"
echo "toolbox_music_library_restrictive_files=${restrictive_files:-0}"

sample_problem_dirs="$(run_toolbox_remote "find '${TARGET_PATH}' -type d ! -perm -0005 -printf '%P\n' 2>/dev/null | head -n 10 | paste -sd'|' -" 2>/dev/null || true)"
sample_problem_files="$(run_toolbox_remote "find '${TARGET_PATH}' -type f ! -perm -0004 -printf '%P\n' 2>/dev/null | head -n 10 | paste -sd'|' -" 2>/dev/null || true)"

echo "toolbox_music_library_problem_dir_samples=${sample_problem_dirs:-none}"
echo "toolbox_music_library_problem_file_samples=${sample_problem_files:-none}"

audio_like_count="$(run_toolbox_remote "find '${TARGET_PATH}' -type f \\( -iname '*.mp3' -o -iname '*.wav' -o -iname '*.flac' -o -iname '*.aif' -o -iname '*.aiff' -o -iname '*.m4a' -o -iname '*.ogg' \\) 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
non_audio_count=$(( ${total_files:-0} - ${audio_like_count:-0} ))

echo "toolbox_music_library_audio_like_files=${audio_like_count:-0}"
echo "toolbox_music_library_non_audio_files=${non_audio_count:-0}"

if [[ "${total_files:-0}" =~ ^[0-9]+$ ]] && (( total_files > 0 )); then
  echo "toolbox_music_library_report_ready=yes"
  if [[ "${restrictive_dirs:-0}" =~ ^[0-9]+$ ]] && (( restrictive_dirs > 0 )); then
    echo "recommendation=normalize_permissions_on_the_central_media_path_for_jellyfin"
  else
    echo "recommendation=central_smb_media_path_is_ready_for_jellyfin"
  fi
else
  echo "toolbox_music_library_report_ready=no"
  echo "recommendation=verify_toolbox_mount_or_radio_source_against_central_media_path"
fi

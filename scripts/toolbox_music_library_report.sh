#!/usr/bin/env bash
set -euo pipefail

TARGET_HOST="root@toolbox"
TARGET_PATH="/srv/media-library/music/bootstrap-radio-usb"

remote() {
  ssh -o BatchMode=yes "${TARGET_HOST}" "$@"
}

echo "toolbox_music_library_path=${TARGET_PATH}"

total_files="$(remote "find '${TARGET_PATH}' -type f 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
total_dirs="$(remote "find '${TARGET_PATH}' -type d 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
total_size="$(remote "du -sh '${TARGET_PATH}' 2>/dev/null | awk '{print \$1}'" 2>/dev/null || echo 0)"
sync_state="$(remote "systemctl is-active homeserver2027-media-sync.service 2>/dev/null || true" 2>/dev/null || echo unknown)"
progress_percent="$(./scripts/toolbox_media_bootstrap_progress.sh 2>/dev/null | awk -F= '/^toolbox_media_bootstrap_size_progress_percent=/{print $2}')"

echo "toolbox_music_library_total_files=${total_files:-0}"
echo "toolbox_music_library_total_dirs=${total_dirs:-0}"
echo "toolbox_music_library_total_size=${total_size:-0}"
echo "toolbox_music_library_sync_state=${sync_state:-unknown}"
echo "toolbox_music_library_bootstrap_size_progress_percent=${progress_percent:-0}"

echo "toolbox_music_library_top_level_dirs=$(remote "find '${TARGET_PATH}' -mindepth 1 -maxdepth 1 -type d -printf '%f\n' 2>/dev/null | sort | paste -sd, -" 2>/dev/null || echo none)"

while IFS= read -r line; do
  echo "${line}"
done < <(
  remote "
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

restrictive_dirs="$(remote "find '${TARGET_PATH}' -type d ! -perm -0005 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
restrictive_files="$(remote "find '${TARGET_PATH}' -type f ! -perm -0004 2>/dev/null | wc -l" 2>/dev/null || echo 0)"

echo "toolbox_music_library_restrictive_dirs=${restrictive_dirs:-0}"
echo "toolbox_music_library_restrictive_files=${restrictive_files:-0}"

sample_problem_dirs="$(remote "find '${TARGET_PATH}' -type d ! -perm -0005 -printf '%P\n' 2>/dev/null | head -n 10 | paste -sd'|' -" 2>/dev/null || true)"
sample_problem_files="$(remote "find '${TARGET_PATH}' -type f ! -perm -0004 -printf '%P\n' 2>/dev/null | head -n 10 | paste -sd'|' -" 2>/dev/null || true)"

echo "toolbox_music_library_problem_dir_samples=${sample_problem_dirs:-none}"
echo "toolbox_music_library_problem_file_samples=${sample_problem_files:-none}"

audio_like_count="$(remote "find '${TARGET_PATH}' -type f \\( -iname '*.mp3' -o -iname '*.wav' -o -iname '*.flac' -o -iname '*.aif' -o -iname '*.aiff' -o -iname '*.m4a' -o -iname '*.ogg' \\) 2>/dev/null | wc -l" 2>/dev/null || echo 0)"
non_audio_count=$(( ${total_files:-0} - ${audio_like_count:-0} ))

echo "toolbox_music_library_audio_like_files=${audio_like_count:-0}"
echo "toolbox_music_library_non_audio_files=${non_audio_count:-0}"

if [[ "${total_files:-0}" =~ ^[0-9]+$ ]] && (( total_files > 0 )); then
  echo "toolbox_music_library_report_ready=yes"
  if [[ "${restrictive_dirs:-0}" =~ ^[0-9]+$ ]] && (( restrictive_dirs > 0 )); then
    echo "recommendation=continue_bootstrap_sync_then_normalize_permissions_for_curated_jellyfin_use"
  else
    echo "recommendation=continue_bootstrap_sync_then_finish_jellyfin_music_library_setup"
  fi
else
  echo "toolbox_music_library_report_ready=no"
  echo "recommendation=wait_for_bootstrap_media_sync_to_seed_music_library"
fi

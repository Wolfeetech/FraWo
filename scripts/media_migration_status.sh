#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/rpi_radio_remote.sh"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

TARGET_HOST="${1:-100.64.23.77}"
SOURCE_PATH="/srv/radio-library/music-usb/yourparty.radio"
TARGET_PATH="/srv/radio-library/music-network/yourparty_Libary"
TOOLBOX_PATH="/srv/media-library/music-network/yourparty_Libary"

human_bytes() {
  local bytes="${1:-0}"
  if command -v numfmt >/dev/null 2>&1; then
    numfmt --to=iec --suffix=B "${bytes}" 2>/dev/null || printf '%sB\n' "${bytes}"
  else
    printf '%sB\n' "${bytes}"
  fi
}

emit_transport_error() {
  echo "error=remote_access_unavailable"
  echo "detail=set_HOMESERVER_PROXMOX_ROOT_PASSWORD_or_restore_direct_ssh_access"
  exit 1
}

source_target_stats="$(
  run_rpi_remote "${TARGET_HOST}" "python3 - <<'PY'
import os
src = '${SOURCE_PATH}'
dst = '${TARGET_PATH}'

source_count = 0
source_size = 0
missing_count = 0
mismatch_count = 0
matched_size = 0

for root, _, files in os.walk(src):
    rel = os.path.relpath(root, src)
    droot = os.path.join(dst, rel) if rel != '.' else dst
    for name in files:
        sp = os.path.join(root, name)
        dp = os.path.join(droot, name)
        source_count += 1
        ssize = os.path.getsize(sp)
        source_size += ssize
        if not os.path.exists(dp):
            missing_count += 1
            continue
        dsize = os.path.getsize(dp)
        if dsize != ssize:
            mismatch_count += 1
            continue
        matched_size += ssize

target_total_count = 0
target_total_size = 0
for root, _, files in os.walk(dst):
    for name in files:
        path = os.path.join(root, name)
        target_total_count += 1
        target_total_size += os.path.getsize(path)

print(f'source_count={source_count}')
print(f'source_size={source_size}')
print(f'missing_count={missing_count}')
print(f'mismatch_count={mismatch_count}')
print(f'matched_count={source_count - missing_count - mismatch_count}')
print(f'matched_size={matched_size}')
print(f'target_total_count={target_total_count}')
print(f'target_total_size={target_total_size}')
PY" 2>/dev/null
)" || emit_transport_error

toolbox_stats="$(
  run_toolbox_remote "python3 - <<'PY'
import os
target = '${TOOLBOX_PATH}'

count = 0
size = 0
for root, _, files in os.walk(target):
    for name in files:
        path = os.path.join(root, name)
        count += 1
        size += os.path.getsize(path)

print(f'toolbox_total_count={count}')
print(f'toolbox_total_size={size}')
PY" 2>/dev/null
)" || emit_transport_error

radio_df_line="$(
  run_rpi_remote "${TARGET_HOST}" "df -B1 '${TARGET_PATH}' | awk 'NR==2 {print \$2\" \"\$3\" \"\$4}'" 2>/dev/null
)" || emit_transport_error

declare -A stats=()
while IFS='=' read -r key value; do
  [[ -n "${key}" ]] || continue
  stats["${key}"]="${value}"
done <<<"${source_target_stats}"

while IFS='=' read -r key value; do
  [[ -n "${key}" ]] || continue
  stats["${key}"]="${value}"
done <<<"${toolbox_stats}"

read -r radio_fs_total radio_fs_used radio_fs_free <<<"${radio_df_line}"

toolbox_match="no"
if [[ "${stats[target_total_count]:-0}" == "${stats[toolbox_total_count]:-0}" && "${stats[target_total_size]:-0}" == "${stats[toolbox_total_size]:-0}" ]]; then
  toolbox_match="yes"
fi

echo "media_migration_source_file_count=${stats[source_count]:-0}"
echo "media_migration_source_size_bytes=${stats[source_size]:-0}"
echo "media_migration_source_size_human=$(human_bytes "${stats[source_size]:-0}")"
echo "media_migration_matched_file_count=${stats[matched_count]:-0}"
echo "media_migration_matched_size_bytes=${stats[matched_size]:-0}"
echo "media_migration_matched_size_human=$(human_bytes "${stats[matched_size]:-0}")"
echo "media_migration_missing_file_count=${stats[missing_count]:-0}"
echo "media_migration_size_mismatch_count=${stats[mismatch_count]:-0}"
echo "media_migration_target_total_file_count=${stats[target_total_count]:-0}"
echo "media_migration_target_total_size_bytes=${stats[target_total_size]:-0}"
echo "media_migration_target_total_size_human=$(human_bytes "${stats[target_total_size]:-0}")"
echo "media_migration_toolbox_total_file_count=${stats[toolbox_total_count]:-0}"
echo "media_migration_toolbox_total_size_bytes=${stats[toolbox_total_size]:-0}"
echo "media_migration_toolbox_total_size_human=$(human_bytes "${stats[toolbox_total_size]:-0}")"
echo "media_migration_target_fs_free_bytes=${radio_fs_free:-0}"
echo "media_migration_target_fs_free_human=$(human_bytes "${radio_fs_free:-0}")"
echo "media_migration_toolbox_matches_target=${toolbox_match}"

if [[ "${stats[missing_count]:-0}" == "0" && "${stats[mismatch_count]:-0}" == "0" && "${stats[source_count]:-0}" != "0" ]]; then
  echo "media_migration_complete=yes"
  echo "recommendation=validate_azuracast_and_jellyfin_against_the_completed_smb_library_then_retire_usb_source"
else
  echo "media_migration_complete=no"
  echo "recommendation=continue_sync_until_missing_and_mismatched_counts_reach_zero"
fi

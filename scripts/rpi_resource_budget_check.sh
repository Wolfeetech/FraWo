#!/usr/bin/env bash
set -euo pipefail

TARGET_HOST="${1:-100.64.23.77}"
SSH_TARGET="wolf@${TARGET_HOST}"
SSH_OPTS=(-o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=accept-new)

run_remote() {
  ssh "${SSH_OPTS[@]}" "${SSH_TARGET}" "$@"
}

mem_total_kib="$(run_remote "awk '/MemTotal:/ {print \$2}' /proc/meminfo" 2>/dev/null || echo 0)"
mem_avail_kib="$(run_remote "awk '/MemAvailable:/ {print \$2}' /proc/meminfo" 2>/dev/null || echo 0)"
swap_total_kib="$(run_remote "awk '/SwapTotal:/ {print \$2}' /proc/meminfo" 2>/dev/null || echo 0)"
swap_free_kib="$(run_remote "awk '/SwapFree:/ {print \$2}' /proc/meminfo" 2>/dev/null || echo 0)"
cpu_cores="$(run_remote "nproc" 2>/dev/null || echo 0)"
root_free_gib="$(run_remote "df -BG / | awk 'NR==2 {gsub(/G/,\"\",\$4); print \$4}'" 2>/dev/null || echo 0)"
azuracast_mem_usage="$(run_remote "docker stats --no-stream --format '{{.Name}}|{{.MemUsage}}|{{.MemPerc}}' | awk -F'|' '\$1==\"azuracast\" {print \$2\"|\"\$3}'" 2>/dev/null || true)"

compose_timeout="$(run_remote "awk -F= '/^COMPOSE_HTTP_TIMEOUT=/{print \$2}' /var/azuracast/.env 2>/dev/null || true" || true)"
php_fpm_children="$(run_remote "awk -F= '/^PHP_FPM_MAX_CHILDREN=/{print \$2}' /var/azuracast/azuracast.env 2>/dev/null || true" || true)"
now_playing_delay="$(run_remote "awk -F= '/^NOW_PLAYING_DELAY_TIME=/{print \$2}' /var/azuracast/azuracast.env 2>/dev/null || true" || true)"
now_playing_concurrency="$(run_remote "awk -F= '/^NOW_PLAYING_MAX_CONCURRENT_PROCESSES=/{print \$2}' /var/azuracast/azuracast.env 2>/dev/null || true" || true)"
web_updater="$(run_remote "awk -F= '/^ENABLE_WEB_UPDATER=/{print \$2}' /var/azuracast/azuracast.env 2>/dev/null || true" || true)"
docker_userland_proxy="$(run_remote "jq -r 'if has(\"userland-proxy\") then .[\"userland-proxy\"] else \"unset\" end' /etc/docker/daemon.json 2>/dev/null || true" || true)"

mem_total_mib=$((mem_total_kib / 1024))
mem_avail_mib=$((mem_avail_kib / 1024))
swap_total_mib=$((swap_total_kib / 1024))
swap_used_mib=$(((swap_total_kib - swap_free_kib) / 1024))

resource_profile="unsupported"
if [[ "${mem_total_mib}" -ge 1700 && "${mem_total_mib}" -lt 2500 ]]; then
  resource_profile="pi4_2gb_single_station_low_resource"
fi

echo "target_host=${TARGET_HOST}"
echo "cpu_cores=${cpu_cores}"
echo "mem_total_mib=${mem_total_mib}"
echo "mem_available_mib=${mem_avail_mib}"
echo "swap_total_mib=${swap_total_mib}"
echo "swap_used_mib=${swap_used_mib}"
echo "root_free_gib=${root_free_gib}"
echo "azuracast_mem_usage=${azuracast_mem_usage:-unknown}"
echo "compose_http_timeout=${compose_timeout:-unset}"
echo "php_fpm_max_children=${php_fpm_children:-unset}"
echo "now_playing_delay_time=${now_playing_delay:-unset}"
echo "now_playing_max_concurrent_processes=${now_playing_concurrency:-unset}"
echo "enable_web_updater=${web_updater:-unset}"
echo "docker_userland_proxy=${docker_userland_proxy:-unset}"
echo "resource_profile=${resource_profile}"
echo "recommended_station_count=1"
echo "recommended_docker_hard_memory_limit=avoid_on_2gb_pi"
echo "recommended_replaygain_mode=precompute_or_disable"
echo "recommended_audio_post_processing=disabled_initially"
echo "recommended_autocue=disabled_initially"

if [[ "${resource_profile}" == "pi4_2gb_single_station_low_resource" \
   && "${swap_total_mib}" -ge 2000 \
   && "${root_free_gib}" -ge 15 \
   && "${compose_timeout:-}" == "900" \
   && "${php_fpm_children:-}" == "2" \
   && "${now_playing_delay:-}" == "15" \
   && "${now_playing_concurrency:-}" == "1" \
   && "${web_updater:-}" == "false" \
   && "${docker_userland_proxy:-}" == "false" ]]; then
  echo "rpi_resource_profile_ready=yes"
  echo "recommendation=keep_single_station_profile_and_finish_azuracast_web_setup"
else
  echo "rpi_resource_profile_ready=no"
  echo "recommendation=apply_low_resource_tuning_profile_before_real_media_load"
fi

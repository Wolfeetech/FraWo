#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/rpi_radio_remote.sh"

TARGET_HOST="${1:-100.64.23.77}"

run_remote() {
  run_rpi_remote "${TARGET_HOST}" "$@"
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "${data}" | awk -F= -v key="$key" '$1 == key {sub($1 FS, ""); print; exit}'
}

remote_snapshot="$(
  run_remote '
    hostname_value="$(hostname 2>/dev/null || echo unknown)"
    ssh_state="$(systemctl is-active ssh 2>/dev/null || echo unknown)"
    docker_state="$(systemctl is-active docker 2>/dev/null || echo unknown)"
    tailscaled_state="$(systemctl is-active tailscaled 2>/dev/null || echo unknown)"
    swap_total_mib="$(awk "/SwapTotal:/ {print int(\$2/1024)}" /proc/meminfo 2>/dev/null || echo 0)"
    root_free_gib="$(df -BG / 2>/dev/null | awk "NR==2 {gsub(/G/,\"\",\$4); print \$4}" || echo 0)"

    if docker compose version >/dev/null 2>&1; then
      docker_compose_ready=yes
    else
      docker_compose_ready=no
    fi

    if test -x /var/azuracast/docker.sh; then
      azuracast_script_present=yes
    else
      azuracast_script_present=no
    fi

    if test -d /srv/radio-library && test -d /srv/radio-assets; then
      radio_dirs_ready=yes
    else
      radio_dirs_ready=no
    fi

    tailscale_json="$(sudo tailscale status --json 2>/dev/null || true)"
    if [ -n "${tailscale_json}" ]; then
      backend_state="$(printf "%s" "${tailscale_json}" | jq -r ".BackendState // \"unknown\"")"
      dns_name="$(printf "%s" "${tailscale_json}" | jq -r ".Self.DNSName // \"unknown\"")"
      tailscale_ipv4="$(sudo tailscale ip -4 2>/dev/null | paste -sd, - || true)"
      [ -n "${tailscale_ipv4}" ] || tailscale_ipv4=unknown
    else
      backend_state=unknown
      dns_name=unknown
      tailscale_ipv4=unknown
    fi

    printf "hostname=%s\n" "${hostname_value}"
    printf "ssh_service=%s\n" "${ssh_state}"
    printf "docker_service=%s\n" "${docker_state}"
    printf "tailscaled_service=%s\n" "${tailscaled_state}"
    printf "tailscale_backend_state=%s\n" "${backend_state}"
    printf "tailscale_dns_name=%s\n" "${dns_name}"
    printf "tailscale_ipv4=%s\n" "${tailscale_ipv4}"
    printf "swap_total_mib=%s\n" "${swap_total_mib}"
    printf "root_free_gib=%s\n" "${root_free_gib}"
    printf "docker_compose_ready=%s\n" "${docker_compose_ready}"
    printf "azuracast_script_present=%s\n" "${azuracast_script_present}"
    printf "radio_dirs_ready=%s\n" "${radio_dirs_ready}"
  ' 2>/dev/null || true
)"

hostname_value="$(extract_value hostname "${remote_snapshot}")"
ssh_state="$(extract_value ssh_service "${remote_snapshot}")"
docker_state="$(extract_value docker_service "${remote_snapshot}")"
tailscaled_state="$(extract_value tailscaled_service "${remote_snapshot}")"
backend_state="$(extract_value tailscale_backend_state "${remote_snapshot}")"
dns_name="$(extract_value tailscale_dns_name "${remote_snapshot}")"
tailscale_ipv4="$(extract_value tailscale_ipv4 "${remote_snapshot}")"
swap_total_mib="$(extract_value swap_total_mib "${remote_snapshot}")"
root_free_gib="$(extract_value root_free_gib "${remote_snapshot}")"
docker_compose_ready="$(extract_value docker_compose_ready "${remote_snapshot}")"
azuracast_script_present="$(extract_value azuracast_script_present "${remote_snapshot}")"
radio_dirs_ready="$(extract_value radio_dirs_ready "${remote_snapshot}")"

hostname_value="${hostname_value:-unknown}"
ssh_state="${ssh_state:-unknown}"
docker_state="${docker_state:-unknown}"
tailscaled_state="${tailscaled_state:-unknown}"
backend_state="${backend_state:-unknown}"
dns_name="${dns_name:-unknown}"
tailscale_ipv4="${tailscale_ipv4:-unknown}"
swap_total_mib="${swap_total_mib:-0}"
root_free_gib="${root_free_gib:-0}"
docker_compose_ready="${docker_compose_ready:-no}"
azuracast_script_present="${azuracast_script_present:-no}"
radio_dirs_ready="${radio_dirs_ready:-no}"

echo "hostname=${hostname_value:-unknown}"
echo "ssh_service=${ssh_state}"
echo "docker_service=${docker_state}"
echo "tailscaled_service=${tailscaled_state}"
echo "tailscale_backend_state=${backend_state}"
echo "tailscale_dns_name=${dns_name}"
echo "tailscale_ipv4=${tailscale_ipv4}"
echo "swap_total_mib=${swap_total_mib}"
echo "root_free_gib=${root_free_gib}"
echo "docker_compose_ready=${docker_compose_ready}"
echo "azuracast_script_present=${azuracast_script_present}"
echo "radio_dirs_ready=${radio_dirs_ready}"

if [[ "${hostname_value}" == "radio-node" \
   && "${ssh_state}" == "active" \
   && "${docker_state}" == "active" \
   && "${tailscaled_state}" == "active" \
   && "${backend_state}" == "Running" \
   && "${docker_compose_ready}" == "yes" \
   && "${azuracast_script_present}" == "yes" \
   && "${radio_dirs_ready}" == "yes" \
   && "${swap_total_mib}" -ge 1024 \
   && "${root_free_gib}" -ge 10 ]]; then
  echo "rpi_radio_ready_for_azuracast=yes"
  echo "recommendation=radio_node_host_ready_keep_low_resource_profile_and_continue_service_checks"
else
  echo "rpi_radio_ready_for_azuracast=no"
  echo "recommendation=finish_host_prep_before_installing_azuracast"
fi

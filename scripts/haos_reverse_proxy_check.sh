#!/usr/bin/env bash
set -euo pipefail

HAOS_IP="192.168.2.24"
TOOLBOX_IP="192.168.2.20"
HAOS_HOSTNAME="ha.hs27.internal"

log() {
  printf '[haos-reverse-proxy-check] %s\n' "$*"
}

check_http_code() {
  local label="$1"
  local url="$2"
  local expected="$3"
  local actual

  actual="$(curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}' "$url")"
  if [[ "$actual" != "$expected" ]]; then
    echo "Expected HTTP ${expected} for ${label}, got ${actual}" >&2
    return 1
  fi

  printf '%s_http=%s\n' "$label" "$actual"
}

check_resolved_http() {
  local label="$1"
  local hostname="$2"
  local target_ip="$3"
  local expected="$4"
  local actual

  actual="$(
    curl \
      --silent \
      --show-error \
      --max-time 10 \
      --noproxy '*' \
      --resolve "${hostname}:80:${target_ip}" \
      --output /dev/null \
      --write-out '%{http_code}' \
      "http://${hostname}/"
  )"

  if [[ "$actual" != "$expected" ]]; then
    echo "Expected HTTP ${expected} for ${hostname} via ${target_ip}, got ${actual}" >&2
    return 1
  fi

  printf '%s_http=%s\n' "$label" "$actual"
}

log "Checking direct Home Assistant endpoint"
check_http_code "haos_direct" "http://${HAOS_IP}:8123/" "200"

log "Checking HA internal frontdoor via toolbox"
check_resolved_http "haos_frontdoor" "${HAOS_HOSTNAME}" "${TOOLBOX_IP}" "200"

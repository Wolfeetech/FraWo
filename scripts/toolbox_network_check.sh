#!/usr/bin/env bash
set -euo pipefail

TOOLBOX_IP="192.168.2.20"

log() {
  printf '[toolbox-check] %s\n' "$*"
}

check_http() {
  local url="$1"
  local expected="$2"
  local actual

  actual="$(curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}' "$url")"
  if [[ ",${expected}," != *",${actual},"* ]]; then
    echo "Expected HTTP ${expected} from ${url}, got ${actual}" >&2
    return 1
  fi

  printf 'http_status=%s\n' "$actual"
}

check_remote_http() {
  local host="$1"
  local url="$2"
  local expected="$3"
  local actual

  actual="$(
    ssh "$host" "curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}' ${url@Q}"
  )"

  if [[ ",${expected}," != *",${actual},"* ]]; then
    echo "Expected HTTP ${expected} from ${host}:${url}, got ${actual}" >&2
    return 1
  fi

  printf 'http_status=%s\n' "$actual"
}

check_resolved_http() {
  local hostname="$1"
  local path="$2"
  local expected="$3"
  local actual

  actual="$(
    curl \
      --silent \
      --show-error \
      --max-time 10 \
      --noproxy '*' \
      --resolve "${hostname}:80:${TOOLBOX_IP}" \
      --output /dev/null \
      --write-out '%{http_code}' \
      "http://${hostname}${path}"
  )"

  if [[ ",${expected}," != *",${actual},"* ]]; then
    echo "Expected HTTP ${expected} from ${hostname}${path}, got ${actual}" >&2
    return 1
  fi

  printf 'http_status=%s\n' "$actual"
}

check_dns() {
  local hostname="$1"
  local expected="$2"
  local actual

  actual="$(dig @"${TOOLBOX_IP}" +short "${hostname}" | tail -n 1)"
  if [[ "$actual" != "$expected" ]]; then
    echo "Expected DNS ${hostname} -> ${expected}, got ${actual:-<empty>}" >&2
    return 1
  fi

  printf 'dns_answer=%s\n' "$actual"
}

log "Checking toolbox base endpoints"
check_http "http://${TOOLBOX_IP}/" "200"
check_remote_http "root@toolbox" "http://127.0.0.1:3000/" "302"

log "Checking toolbox systemd and containers"
ssh root@toolbox "systemctl is-enabled homeserver-compose-toolbox-network.service"
ssh root@toolbox "systemctl is-active homeserver-compose-toolbox-network.service"
ssh root@toolbox "docker ps --format '{{.Names}}|{{.Status}}' | grep '^toolbox-network_'"

HOSTS=(
  "portal.hs27.internal|/|200"
  "cloud.hs27.internal|/|200"
  "odoo.hs27.internal|/web/login|200,303"
  "paperless.hs27.internal|/accounts/login/|200"
  "ha.hs27.internal|/|200"
  "radio.hs27.internal|/|302"
)

for entry in "${HOSTS[@]}"; do
  IFS='|' read -r hostname path expected_http <<<"${entry}"
  log "Checking DNS and proxy path for ${hostname}"
  check_dns "${hostname}" "${TOOLBOX_IP}"
  check_resolved_http "${hostname}" "${path}" "${expected_http}"
done

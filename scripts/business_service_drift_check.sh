#!/usr/bin/env bash
set -euo pipefail

SSH_OPTS=(
  -o BatchMode=yes
  -o StrictHostKeyChecking=accept-new
)

log() {
  printf '[drift-check] %s\n' "$*"
}

remote() {
  local target="$1"
  shift
  ssh "${SSH_OPTS[@]}" "$target" "$@"
}

check_http() {
  local url="$1"
  local expected="$2"
  local actual

  actual="$(curl --silent --show-error --location --max-time 10 --output /dev/null --write-out '%{http_code}' "$url")"
  if [[ "$actual" != "$expected" ]]; then
    echo "Expected HTTP ${expected} from ${url}, got ${actual}" >&2
    return 1
  fi

  printf 'http_status=%s\n' "$actual"
}

CHECKS=(
  "nextcloud|wolf@192.168.2.21|homeserver-compose-nextcloud.service|/opt/homeserver2027/stacks/nextcloud/docker-compose.yml|nextcloud_|http://192.168.2.21/|200"
  "odoo|wolf@192.168.2.22|homeserver-compose-odoo.service|/opt/homeserver2027/stacks/odoo/docker-compose.yml|odoo_|http://192.168.2.22:8069/web/login|200"
  "paperless|wolf@192.168.2.23|homeserver-compose-paperless.service|/opt/homeserver2027/stacks/paperless/docker-compose.yml|paperless_|http://192.168.2.23:8000/accounts/login/|200"
)

for entry in "${CHECKS[@]}"; do
  IFS='|' read -r label target service compose_path container_prefix url expected_http <<<"${entry}"

  log "Checking ${label}"
  remote "${target}" "hostname"
  remote "${target}" "systemctl is-enabled '${service}'"
  remote "${target}" "systemctl is-active '${service}'"
  remote "${target}" "test -f '${compose_path}' && echo compose_present"
  remote "${target}" "docker ps --format '{{.Names}}|{{.Status}}' | grep '^${container_prefix}'"
  check_http "${url}" "${expected_http}"
done

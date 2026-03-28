#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

SSH_OPTS=(
  -o BatchMode=yes
  -o StrictHostKeyChecking=accept-new
)

log() {
  printf '[drift-check] %s\n' "$*"
}

remote() {
  local host_key="$1"
  shift
  run_inventory_guest_remote "${host_key}" "$*" "wolf"
}

check_http() {
  local url="$1"
  local expected="$2"
  local actual

  actual="$(curl --silent --show-error --location --max-time 15 --output /dev/null --write-out '%{http_code}' "$url")"
  if [[ ",${expected}," != *",${actual},"* ]]; then
    echo "Expected HTTP ${expected} from ${url}, got ${actual}" >&2
    return 1
  fi

  printf 'http_status=%s\n' "$actual"
}

CHECKS=(
  "nextcloud|nextcloud_vm|homeserver-compose-nextcloud.service|/opt/homeserver2027/stacks/nextcloud/docker-compose.yml|nextcloud_|http://192.168.2.21/|200"
  "odoo|odoo_vm|homeserver-compose-odoo.service|/opt/homeserver2027/stacks/odoo/docker-compose.yml|odoo_|http://192.168.2.22:8069/web/login|200,303"
  "paperless|paperless_vm|homeserver-compose-paperless.service|/opt/homeserver2027/stacks/paperless/docker-compose.yml|paperless_|http://192.168.2.23:8000/accounts/login/|200"
)

for entry in "${CHECKS[@]}"; do
  IFS='|' read -r label host_key service compose_path container_prefix url expected_http <<<"${entry}"

  log "Checking ${label}"
  remote "${host_key}" "hostname"
  remote "${host_key}" "systemctl is-enabled '${service}'"
  remote "${host_key}" "systemctl is-active '${service}'"
  remote "${host_key}" "test -f '${compose_path}' && echo compose_present"
  remote "${host_key}" "docker ps --format '{{.Names}}|{{.Status}}' | grep '^${container_prefix}'"
  check_http "${url}" "${expected_http}"
done

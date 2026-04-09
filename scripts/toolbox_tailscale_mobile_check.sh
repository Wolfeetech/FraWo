#!/usr/bin/env bash
set -euo pipefail

check_http() {
  local host="$1"
  local url="$2"
  local expected="$3"
  local actual

  actual="$(ssh "$host" "curl --silent --show-error --max-time 15 --output /dev/null --write-out '%{http_code}' ${url@Q}")"
  if [[ ",${expected}," != *",${actual},"* ]]; then
    echo "Expected HTTP ${expected} from ${host}:${url}, got ${actual}" >&2
    return 1
  fi

  printf 'http_status=%s\n' "$actual"
}

echo "[tailscale-mobile-check] verifying toolbox mobile proxy ports"
check_http "root@toolbox" "http://127.0.0.1:8443/" "200"
check_http "root@toolbox" "http://127.0.0.1:8444/web/login" "200"
check_http "root@toolbox" "http://127.0.0.1:8445/" "200"
check_http "root@toolbox" "http://127.0.0.1:8446/accounts/login/" "200"
check_http "root@toolbox" "http://127.0.0.1:8447/" "200"
check_http "root@toolbox" "http://127.0.0.1:8448/" "200,302"

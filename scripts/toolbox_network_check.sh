#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

TOOLBOX_IP="10.1.0.20"

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
  local url="$1"
  local expected="$2"
  local actual

  actual="$(
    run_toolbox_remote "curl --silent --show-error --max-time 10 --output /dev/null --write-out '%{http_code}' ${url@Q}"
  )"

  if [[ ",${expected}," != *",${actual},"* ]]; then
    echo "Expected HTTP ${expected} from toolbox:${url}, got ${actual}" >&2
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

  if command -v dig >/dev/null 2>&1; then
    actual="$(dig @"${TOOLBOX_IP}" +short "${hostname}" | tail -n 1)"
  elif command -v nslookup >/dev/null 2>&1; then
    actual="$(nslookup "${hostname}" "${TOOLBOX_IP}" 2>/dev/null | awk '/^Address: / {print $2}' | tail -n 1)"
  else
    actual="$(
      python3 - <<'PY' "${TOOLBOX_IP}" "${hostname}"
import socket
import struct
import sys

server = sys.argv[1]
hostname = sys.argv[2].rstrip(".")

transaction_id = 0x1234
flags = 0x0100
qdcount = 1
header = struct.pack("!HHHHHH", transaction_id, flags, qdcount, 0, 0, 0)
question = b"".join(len(label).to_bytes(1, "big") + label.encode("ascii") for label in hostname.split(".")) + b"\x00"
question += struct.pack("!HH", 1, 1)
packet = header + question

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)
sock.sendto(packet, (server, 53))
data, _ = sock.recvfrom(512)
sock.close()

answer_count = struct.unpack("!H", data[6:8])[0]
offset = 12
while data[offset] != 0:
    offset += data[offset] + 1
offset += 5

for _ in range(answer_count):
    if data[offset] & 0xC0 == 0xC0:
        offset += 2
    else:
        while data[offset] != 0:
            offset += data[offset] + 1
        offset += 1
    rtype, rclass, _ttl, rdlength = struct.unpack("!HHIH", data[offset:offset + 10])
    offset += 10
    rdata = data[offset:offset + rdlength]
    offset += rdlength
    if rtype == 1 and rclass == 1 and rdlength == 4:
        print(socket.inet_ntoa(rdata))
        raise SystemExit(0)

raise SystemExit(1)
PY
    )"
  fi
  if [[ "$actual" != "$expected" ]]; then
    echo "Expected DNS ${hostname} -> ${expected}, got ${actual:-<empty>}" >&2
    return 1
  fi

  printf 'dns_answer=%s\n' "$actual"
}

log "Checking toolbox base endpoints"
check_http "http://${TOOLBOX_IP}/" "200"
check_remote_http "http://127.0.0.1:3000/" "302"

log "Checking toolbox systemd and containers"
run_toolbox_remote "systemctl is-enabled homeserver-compose-toolbox-network.service"
run_toolbox_remote "systemctl is-active homeserver-compose-toolbox-network.service"
run_toolbox_remote "docker ps --format '{{.Names}}|{{.Status}}' | grep '^toolbox-network_'"

HOSTS=(
  "portal.hs27.internal|/|200"
  "cloud.hs27.internal|/|200,302"
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

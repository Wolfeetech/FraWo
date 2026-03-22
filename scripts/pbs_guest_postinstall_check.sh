#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

read_hostvar() {
  local key="$1"
  python3 - <<'PY' "$ROOT_DIR/ansible/inventory/host_vars/pbs.yml" "$key"
import sys
import yaml

path = sys.argv[1]
key = sys.argv[2]
with open(path, 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data[key])
PY
}

PBS_HOST="$(python3 - <<'PY' "$ROOT_DIR/ansible/inventory/hosts.yml"
import sys, yaml
with open(sys.argv[1], 'r', encoding='utf-8') as handle:
    data = yaml.safe_load(handle)
print(data["all"]["children"]["management"]["hosts"]["pbs"]["ansible_host"])
PY
)"

PBS_ADMIN_URL="$(read_hostvar pbs_admin_url)"

icmp="no"
tcp22="closed"
tcp8007="closed"

if ping -c 1 -W 1 "$PBS_HOST" >/dev/null 2>&1; then
  icmp="yes"
fi

python3 - <<'PY' "$PBS_HOST" 22 >/dev/null 2>&1 && tcp22="open" || true
import socket, sys
host = sys.argv[1]
port = int(sys.argv[2])
s = socket.socket()
s.settimeout(1.5)
try:
    s.connect((host, port))
except Exception:
    raise SystemExit(1)
else:
    s.close()
    raise SystemExit(0)
PY

python3 - <<'PY' "$PBS_HOST" 8007 >/dev/null 2>&1 && tcp8007="open" || true
import socket, sys
host = sys.argv[1]
port = int(sys.argv[2])
s = socket.socket()
s.settimeout(1.5)
try:
    s.connect((host, port))
except Exception:
    raise SystemExit(1)
else:
    s.close()
    raise SystemExit(0)
PY

echo "pbs_target_ip=${PBS_HOST}"
echo "pbs_admin_url=${PBS_ADMIN_URL}"
echo "pbs_ping_reachable=${icmp}"
echo "pbs_ssh_port=${tcp22}"
echo "pbs_web_port=${tcp8007}"

if [[ "${tcp22}" == "open" && "${tcp8007}" == "open" ]]; then
  echo "pbs_guest_postinstall_ready=yes"
  echo "recommendation=configure_datastore_and_add_pbs_storage_target"
elif [[ "${icmp}" == "yes" || "${tcp22}" == "open" || "${tcp8007}" == "open" ]]; then
  echo "pbs_guest_postinstall_ready=partial"
  echo "recommendation=finish_pbs_installer_and_wait_for_ssh_and_web"
else
  echo "pbs_guest_postinstall_ready=no"
  echo "recommendation=complete_pbs_installer_in_vm240_console"
fi

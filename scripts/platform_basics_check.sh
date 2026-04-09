#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

read_pbs_hostvar() {
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

run_check() {
  local script="$1"
if output="$(timeout 25 "${ROOT_DIR}/scripts/${script}" 2>/dev/null)"; then
    printf '%s\n' "$output"
    return 0
  fi
  return 1
}

tcp_open() {
  local host="$1"
  local port="$2"
  python3 - <<'PY' "$host" "$port"
import socket, sys
host = sys.argv[1]
port = int(sys.argv[2])
s = socket.socket()
s.settimeout(2)
try:
    s.connect((host, port))
except Exception:
    raise SystemExit(1)
else:
    s.close()
    raise SystemExit(0)
PY
}

http_code() {
  local url="$1"
  curl --silent --show-error --max-time 8 --output /dev/null --write-out '%{http_code}' "$url"
}

security_output="$(run_check security_baseline_check.sh)"
surface_output="$(run_check surface_go_frontend_check.sh)"
radio_output="$(run_check radio_operations_check.sh)"
media_output="$(run_check toolbox_media_server_check.sh)"
inventory_output="$(run_check inventory_resolution_check.sh)"
pbs_guest_output="$(run_check pbs_guest_postinstall_check.sh)"

business_core_ok="no"
nextcloud_ok="no"
odoo_ok="no"
paperless_ok="no"

if run_inventory_guest_remote nextcloud_vm "systemctl is-active --quiet homeserver-compose-nextcloud.service" "wolf" >/dev/null 2>&1 && tcp_open 10.1.0.21 80 >/dev/null 2>&1; then
  nextcloud_ok="yes"
fi
if run_inventory_guest_remote odoo_vm "systemctl is-active --quiet homeserver-compose-odoo.service" "wolf" >/dev/null 2>&1 && tcp_open 10.1.0.22 8069 >/dev/null 2>&1; then
  odoo_ok="yes"
fi
if run_inventory_guest_remote paperless_vm "systemctl is-active --quiet homeserver-compose-paperless.service" "wolf" >/dev/null 2>&1 && tcp_open 10.1.0.23 8000 >/dev/null 2>&1; then
  paperless_ok="yes"
fi
if [[ "${nextcloud_ok}" == "yes" && "${odoo_ok}" == "yes" && "${paperless_ok}" == "yes" ]]; then
  business_core_ok="yes"
fi

toolbox_network_ok="no"
toolbox_ip="10.1.0.20"
portal_http="$(curl --silent --show-error --max-time 8 --noproxy '*' --resolve "portal.hs27.internal:80:${toolbox_ip}" --output /dev/null --write-out '%{http_code}' "http://portal.hs27.internal/" 2>/dev/null || true)"
ha_http="$(curl --silent --show-error --max-time 8 --noproxy '*' --resolve "ha.hs27.internal:80:${toolbox_ip}" --output /dev/null --write-out '%{http_code}' "http://ha.hs27.internal/" 2>/dev/null || true)"
if [[ "${portal_http}" == "200" && "${ha_http}" == "200" ]]; then
  toolbox_network_ok="yes"
fi

PBS_PROXMOX_STORAGE_ID="$(read_pbs_hostvar pbs_proxmox_storage_id)"

pbs_storage_active="no"
if run_proxmox_remote "pvesm status | awk '\$1 == \"${PBS_PROXMOX_STORAGE_ID}\" && \$2 == \"pbs\" && \$3 == \"active\" {found=1} END {exit(found ? 0 : 1)}'" >/dev/null 2>&1; then
  pbs_storage_active="yes"
fi

security_ok="no"
[[ "$(extract_value security_status "${security_output}")" == "ok" ]] && security_ok="yes"

surface_ready="no"
[[ "$(extract_value surface_go_remote_admin_ready "${surface_output}")" == "yes" && "$(extract_value surface_go_portal_service_active "${surface_output}")" == "active" ]] && surface_ready="yes"

radio_ready="no"
[[ "$(extract_value radio_operations_ready "${radio_output}")" == "yes" ]] && radio_ready="yes"

media_ready="no"
[[ "$(extract_value toolbox_media_server_ready "${media_output}")" == "yes" ]] && media_ready="yes"

pbs_guest_ready="no"
[[ "$(extract_value pbs_guest_postinstall_ready "${pbs_guest_output}")" == "yes" ]] && pbs_guest_ready="yes"

inventory_finalized="no"
[[ "$(extract_value inventory_resolution_ready "${inventory_output}")" == "yes" ]] && inventory_finalized="yes"

basics_final="no"
if [[ "${security_ok}" == "yes" && "${toolbox_network_ok}" == "yes" && "${business_core_ok}" == "yes" && "${surface_ready}" == "yes" && "${radio_ready}" == "yes" && "${media_ready}" == "yes" && "${pbs_guest_ready}" == "yes" && "${pbs_storage_active}" == "yes" ]]; then
  basics_final="yes"
fi

echo "security_ok=${security_ok}"
echo "toolbox_network_ok=${toolbox_network_ok}"
echo "portal_proxy_http=${portal_http:-unknown}"
echo "ha_proxy_http=${ha_http:-unknown}"
echo "business_core_ok=${business_core_ok}"
echo "nextcloud_baseline_ok=${nextcloud_ok}"
echo "odoo_baseline_ok=${odoo_ok}"
echo "paperless_baseline_ok=${paperless_ok}"
echo "surface_ready=${surface_ready}"
echo "radio_ready=${radio_ready}"
echo "media_ready=${media_ready}"
echo "pbs_guest_ready=${pbs_guest_ready}"
echo "pbs_storage_active=${pbs_storage_active}"
echo "inventory_finalized=${inventory_finalized}"
echo "basics_final=${basics_final}"

if [[ "${basics_final}" == "yes" && "${inventory_finalized}" == "yes" ]]; then
  echo "recommendation=core_platform_basics_are_finalized"
elif [[ "${pbs_guest_ready}" != "yes" || "${pbs_storage_active}" != "yes" ]]; then
  echo "recommendation=stabilize_pbs_before_calling_basics_final"
elif [[ "${inventory_finalized}" != "yes" ]]; then
  echo "recommendation=finish_inventory_and_router_mapping"
else
  echo "recommendation=finish_remaining_proof_and_polish_items"
fi

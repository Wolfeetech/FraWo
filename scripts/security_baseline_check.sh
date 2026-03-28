#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

log() {
  printf '[security-check] %s\n' "$*"
}

search_workspace() {
  local pattern="$1"

  if command -v rg >/dev/null 2>&1; then
    rg -l --hidden --glob '*.yml' --glob '*.yaml' --glob '*.md' --glob '*.env' --glob '!ansible/inventory/group_vars/all/vault.yml' "${pattern}" "${ROOT_DIR}" || true
  else
    grep -R -l -E --include='*.yml' --include='*.yaml' --include='*.md' --include='*.env' --exclude='vault.yml' "${pattern}" "${ROOT_DIR}" 2>/dev/null || true
  fi
}

workspace_has_pattern() {
  local pattern="$1"
  local path="${2:-${ROOT_DIR}}"

  if command -v rg >/dev/null 2>&1; then
    rg -q "${pattern}" "${path}"
  else
    grep -q -E "${pattern}" "${path}" 2>/dev/null
  fi
}

run_host_remote() {
  local host_key="$1"
  local remote_command="$2"

  case "${host_key}" in
    toolbox)
      run_toolbox_remote "${remote_command}"
      ;;
    nextcloud_vm|odoo_vm|paperless_vm)
      run_inventory_guest_remote "${host_key}" "${remote_command}" "wolf"
      ;;
    *)
      run_inventory_remote "${host_key}" "${remote_command}"
      ;;
  esac
}

remote_tcp_ports_by_scope() {
  local host_key="$1"
  local scope="$2"
  run_host_remote "${host_key}" "python3 - <<'PY'
import ipaddress
import re
import subprocess

scope = ${scope@Q}
ports = set()
for line in subprocess.check_output(['ss', '-tlnH'], text=True).splitlines():
    cols = line.split()
    if len(cols) < 4:
        continue
    local = cols[3]
    if local.startswith('127.') or local.startswith('[::1]'):
        continue
    match = re.search(r':(\d+)$', local)
    if match:
        port = int(match.group(1))
    else:
        continue

    addr = local.rsplit(':', 1)[0]
    if addr.startswith('[') and addr.endswith(']'):
        addr = addr[1:-1]

    is_tailscale = False
    if addr not in {'0.0.0.0', '::', '*'}:
        try:
            ip = ipaddress.ip_address(addr)
            if ip.version == 4:
                is_tailscale = ip in ipaddress.ip_network('100.64.0.0/10')
            else:
                is_tailscale = ip in ipaddress.ip_network('fd7a:115c:a1e0::/48')
        except ValueError:
            is_tailscale = False

    if scope == 'lan' and not is_tailscale:
        ports.add(port)
    elif scope == 'tailscale' and is_tailscale:
        ports.add(port)

print(','.join(str(port) for port in sorted(ports)))
PY"
}

remote_tcp_ports() {
  local host_key="$1"
  remote_tcp_ports_by_scope "${host_key}" lan
}

remote_unexpected_data_ports() {
  local host_key="$1"
  run_host_remote "${host_key}" "python3 - <<'PY'
import re
import subprocess

unexpected = []
for line in subprocess.check_output(['ss', '-tlnH'], text=True).splitlines():
    cols = line.split()
    if len(cols) < 4:
        continue
    local = cols[3]
    if local.startswith('127.') or local.startswith('[::1]'):
        continue
    match = re.search(r':(\d+)$', local)
    if not match:
        continue
    port = int(match.group(1))
    if port in {3306, 5432, 6379, 6380, 5672, 9200, 9300}:
        unexpected.append(str(port))

print(','.join(unexpected))
PY"
}

remote_port_surface() {
  local host_key="$1"
  local port="$2"
  run_host_remote "${host_key}" "python3 - <<'PY'
import re
import subprocess

port = int(${port})
lan = False
loopback = False
for line in subprocess.check_output(['ss', '-tlnH'], text=True).splitlines():
    cols = line.split()
    if len(cols) < 4:
        continue
    local = cols[3]
    match = re.search(r':(\d+)$', local)
    if not match or int(match.group(1)) != port:
        continue
    if local.startswith('127.') or local.startswith('[::1]'):
        loopback = True
    else:
        lan = True

if lan and loopback:
    print('lan_and_loopback')
elif lan:
    print('lan')
elif loopback:
    print('loopback')
else:
    print('none')
PY"
}

filter_toolbox_effective_lan_ports() {
  local ports_csv="$1"
  python3 - "${ports_csv}" <<'PY'
import sys

ports = [p for p in sys.argv[1].split(',') if p]
excluded = {"8443", "8444", "8445", "8446", "8447", "8448", "8449"}
filtered = [p for p in ports if p not in excluded]
print(','.join(filtered))
PY
}

log "Checking workspace for plaintext secret leaks outside Vault"
easybox_secret_hits="$(search_workspace 'homeserver_vault_easybox_password:[[:space:]]+[^[:space:]]')"
tailscale_secret_hits="$(search_workspace 'homeserver_vault_tailscale_authkey:[[:space:]]+[^[:space:]]')"
secret_hits="$(printf '%s\n%s\n' "${easybox_secret_hits}" "${tailscale_secret_hits}" | sed '/^$/d' | sort -u)"
if [[ -n "${secret_hits}" ]]; then
  echo "plaintext_secret_leak=yes"
  printf '%s\n' "${secret_hits}"
else
  echo "plaintext_secret_leak=no"
fi

log "Checking declared public exposure policy"
if workspace_has_pattern '^  public_exposure_enabled: false$' "${ROOT_DIR}/ansible/inventory/group_vars/all/main.yml"; then
  echo "public_exposure_enabled=false"
else
  echo "public_exposure_enabled=true_or_unknown"
fi

log "Checking Tailscale backend state"
tailscale_backend_state="$(
  run_toolbox_remote "tailscale status --json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get(\"BackendState\", \"unknown\"))'" 2>/dev/null \
  || echo "unknown"
)"
echo "tailscale_backend_state=${tailscale_backend_state}"

log "Checking externally reachable TCP ports"
toolbox_lan_ports_raw="$(remote_tcp_ports_by_scope toolbox lan)"
toolbox_lan_ports="$(filter_toolbox_effective_lan_ports "${toolbox_lan_ports_raw}")"
toolbox_tailscale_only_ports="$(remote_tcp_ports_by_scope toolbox tailscale)"
nextcloud_ports="$(remote_tcp_ports nextcloud_vm)"
odoo_ports="$(remote_tcp_ports odoo_vm)"
paperless_ports="$(remote_tcp_ports paperless_vm)"
echo "toolbox_lan_tcp_ports=${toolbox_lan_ports}"
echo "toolbox_tailscale_only_tcp_ports=${toolbox_tailscale_only_ports:-none}"
echo "nextcloud_tcp_ports=${nextcloud_ports}"
echo "odoo_tcp_ports=${odoo_ports}"
echo "paperless_tcp_ports=${paperless_ports}"

log "Checking for unexpected database or broker ports on business VMs"
nextcloud_unexpected="$(remote_unexpected_data_ports nextcloud_vm)"
odoo_unexpected="$(remote_unexpected_data_ports odoo_vm)"
paperless_unexpected="$(remote_unexpected_data_ports paperless_vm)"
echo "nextcloud_unexpected_data_ports=${nextcloud_unexpected:-none}"
echo "odoo_unexpected_data_ports=${odoo_unexpected:-none}"
echo "paperless_unexpected_data_ports=${paperless_unexpected:-none}"

log "Checking whether LLMNR is still exposed on business VMs"
llmnr_open="no"
for host in nextcloud_vm odoo_vm paperless_vm; do
  if run_host_remote "$host" "ss -tlnH | grep -q ':5355'"; then
    printf 'llmnr_open_on=%s\n' "$host"
    llmnr_open="yes"
  fi
done
echo "llmnr_open=${llmnr_open}"

log "Checking AdGuard admin surface on toolbox"
adguard_admin_surface="$(remote_port_surface toolbox 3000)"
case "${adguard_admin_surface}" in
  lan|lan_and_loopback)
  echo "adguard_admin_lan_surface=yes"
  ;;
  *)
  echo "adguard_admin_lan_surface=no"
  ;;
esac
case "${adguard_admin_surface}" in
  loopback|lan_and_loopback)
  echo "adguard_admin_local_surface=yes"
  ;;
  *)
  echo "adguard_admin_local_surface=no"
  ;;
esac

log "Checking whether mobile frontdoor ports are still reachable from the LAN"
toolbox_mobile_lan_surface="no"
toolbox_mobile_lan_probe_host="nextcloud_vm"
for port in 8443 8444 8445 8446 8447 8448 8449; do
  if run_host_remote "${toolbox_mobile_lan_probe_host}" "curl --silent --max-time 5 --output /dev/null http://192.168.2.20:${port}/ 2>/dev/null"; then
    toolbox_mobile_lan_surface="yes"
    break
  fi
done
echo "toolbox_mobile_lan_surface=${toolbox_mobile_lan_surface}"
echo "toolbox_mobile_lan_probe_host=${toolbox_mobile_lan_probe_host}"

log "Checking toolbox mobile firewall service"
toolbox_mobile_firewall_service="$(run_toolbox_remote 'systemctl is-active homeserver2027-toolbox-mobile-firewall.service 2>/dev/null || true')"
echo "toolbox_mobile_firewall_service=${toolbox_mobile_firewall_service:-missing}"

security_status="ok"
if [[ -n "${secret_hits}" || "${nextcloud_unexpected}" != "" || "${odoo_unexpected}" != "" || "${paperless_unexpected}" != "" || "${llmnr_open}" == "yes" || "${adguard_admin_surface}" == "lan" || "${adguard_admin_surface}" == "lan_and_loopback" || "${toolbox_mobile_lan_surface}" == "yes" || "${toolbox_mobile_firewall_service}" != "active" ]]; then
  security_status="attention_required"
fi
echo "security_status=${security_status}"

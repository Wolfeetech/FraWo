#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source "${ROOT_DIR}/scripts/inventory_remote.sh"
source "${ROOT_DIR}/scripts/toolbox_remote.sh"

log() {
  printf '[haos-stage-gate] %s\n' "$*"
}

extract_value() {
  local key="$1"
  local data="$2"
  printf '%s\n' "$data" | awk -F= -v key="$key" '$1 == key {print $2; exit}'
}

get_vm210_status() {
  run_proxmox_remote "qm status 210 2>/dev/null | awk '/^status:/ {print \$2}'" 2>/dev/null || echo "unknown"
}

get_vm210_ipv4() {
  run_proxmox_remote "qm guest cmd 210 network-get-interfaces 2>/dev/null | python3 -c '
import json, sys
data = json.load(sys.stdin)
for iface in data:
    if iface.get(\"name\") == \"lo\":
        continue
    for addr in iface.get(\"ip-addresses\", []):
        ip = addr.get(\"ip-address\", \"\")
        if addr.get(\"ip-address-type\") == \"ipv4\" and ip and not ip.startswith(\"127.\") and not ip.startswith(\"172.30.\"):
            print(ip)
            raise SystemExit(0)
print(\"unknown\")
' " 2>/dev/null || echo "unknown"
}

toolbox_network_foundation="no"
if "${ROOT_DIR}/scripts/toolbox_network_check.sh" >/dev/null 2>&1; then
  toolbox_network_foundation="yes"
fi

log "Reading Tailscale backend state from toolbox"
tailscale_backend_state="$(
  run_toolbox_remote "tailscale status --json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get(\"BackendState\", \"unknown\"))'" 2>/dev/null \
  || echo "unknown"
)"

tailscale_ready="no"
if [[ -n "$tailscale_backend_state" && "$tailscale_backend_state" != "NeedsLogin" && "$tailscale_backend_state" != "NoState" && "$tailscale_backend_state" != "unknown" ]]; then
  tailscale_ready="yes"
fi

backup_timer_live="no"
if run_proxmox_remote "systemctl is-enabled --quiet homeserver2027-local-business-backup.timer && systemctl is-active --quiet homeserver2027-local-business-backup.timer" >/dev/null 2>&1; then
  backup_timer_live="yes"
fi

log "Reading HAOS preflight output"
preflight_output="$("${ROOT_DIR}/scripts/haos_preflight_check.sh")"
printf '%s\n' "$preflight_output"

vm210_exists="$(extract_value vm210_exists "$preflight_output")"
haos_4gb_fit="$(extract_value haos_4gb_fit "$preflight_output")"
haos_32g_disk_fit="$(extract_value haos_32g_disk_fit "$preflight_output")"
usb_passthrough_ready="$(extract_value usb_passthrough_ready "$preflight_output")"
haos_vm_status="absent"
haos_current_ipv4="absent"
if [[ "$vm210_exists" == "yes" ]]; then
  haos_vm_status="$(get_vm210_status)"
  haos_current_ipv4="$(get_vm210_ipv4)"
fi

haos_stage_gate_ready="no"
if [[ "$toolbox_network_foundation" == "yes" && "$tailscale_ready" == "yes" && "$backup_timer_live" == "yes" && "$vm210_exists" == "no" && "$haos_4gb_fit" == "yes" && "$haos_32g_disk_fit" == "yes" ]]; then
  haos_stage_gate_ready="yes"
elif [[ "$toolbox_network_foundation" == "yes" && "$tailscale_ready" == "yes" && "$backup_timer_live" == "yes" && "$vm210_exists" == "yes" ]]; then
  haos_stage_gate_ready="yes"
fi

echo "toolbox_network_foundation=${toolbox_network_foundation}"
echo "tailscale_backend_state=${tailscale_backend_state}"
echo "tailscale_stage_gate_ready=${tailscale_ready}"
echo "backup_timer_live=${backup_timer_live}"
echo "haos_stage_gate_ready=${haos_stage_gate_ready}"
echo "haos_vm_status=${haos_vm_status}"
echo "haos_current_ipv4=${haos_current_ipv4}"

if [[ "$vm210_exists" == "yes" && "$haos_vm_status" != "running" ]]; then
  echo "recommendation=start_vm210_and_finish_post_build_validation"
elif [[ "$vm210_exists" == "yes" && "$haos_current_ipv4" == "unknown" ]]; then
  echo "recommendation=vm210_running_confirm_network_identity_and_then_stabilize_addressing"
elif [[ "$vm210_exists" == "yes" && "$haos_current_ipv4" != "10.1.0.24" ]]; then
  echo "recommendation=stabilize_vm210_address_then_switch_ha_internal_dns"
elif [[ "$vm210_exists" == "yes" && "$usb_passthrough_ready" == "no" ]]; then
  echo "recommendation=vm210_online_stable_wait_for_real_usb_dongles_not_storage_only_usb"
elif [[ "$vm210_exists" == "yes" ]]; then
  echo "recommendation=vm210_stable_continue_with_snapshot_addons_and_usb_passthrough"
elif [[ "$haos_stage_gate_ready" == "yes" && "$usb_passthrough_ready" == "no" ]]; then
  echo "recommendation=build_baseline_haos_vm_now_and_add_usb_passthrough_later"
elif [[ "$haos_stage_gate_ready" == "yes" ]]; then
  echo "recommendation=build_haos_vm_and_continue_with_usb_passthrough"
else
  echo "recommendation=clear_remaining_network_backup_or_capacity_gates_before_building_vm210"
fi

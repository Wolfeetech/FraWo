#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_NAME="Homeserver 2027 Ops Workspace"
WORKSPACE_ALIAS="/home/wolf/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace"
DESKTOP_SHORTCUT="/home/wolf/Desktop/Homeserver 2027 Workspace"
OUTPUT_FILE="${ROOT_DIR}/LIVE_CONTEXT.md"

section_body() {
  local file="$1"
  local heading="$2"
  awk -v heading="$heading" '
    $0 == heading {in_section=1; next}
    in_section && /^## / {exit}
    in_section {print}
  ' "$file"
}

mtime() {
  stat -c '%y' "$1" | cut -d'.' -f1
}

inventory_count="$(awk '/ansible_host:/{count++} END {print count+0}' "${ROOT_DIR}/ansible/inventory/hosts.yml")"
git_branch="$(git -C "${ROOT_DIR}" branch --show-current 2>/dev/null || true)"
git_dirty_count="$(git -C "${ROOT_DIR}" status --short 2>/dev/null | wc -l | awk '{print $1}')"
generated_at="$(date '+%Y-%m-%d %H:%M:%S %Z')"

cat > "${OUTPUT_FILE}" <<EOF
# Live Context

## Workspace

- Name: \`${WORKSPACE_NAME}\`
- Alias: \`${WORKSPACE_ALIAS}\`
- Desktop shortcut: \`${DESKTOP_SHORTCUT}\`
- Generated at: \`${generated_at}\`
- Git branch: \`${git_branch:-main}\`
- Pending git changes: \`${git_dirty_count}\`

## Shared Read Order

1. \`LIVE_CONTEXT.md\`
2. \`MASTERPLAN.md\`
3. \`MORNING_ROUTINE.md\`
4. \`SECURITY_BASELINE.md\`
5. \`SESSION_CLOSEOUT.md\`
6. \`GEMINI.md\`
7. \`MEMORY.md\`
8. \`NETWORK_INVENTORY.md\`
9. \`VM_AUDIT.md\`
10. \`BACKUP_RESTORE_PROOF.md\`
11. \`CAPACITY_REVIEW.md\`
12. \`RIGHTSIZING_MAINTENANCE_PLAN.md\`
13. \`SURFACE_GO_FRONTEND_SETUP_PLAN.md\`
14. \`MEDIA_AND_REMOTE_PREP.md\`
15. \`REMOTE_ACCESS_STANDARD.md\`
16. \`REMOTE_ONLY_WORK_WINDOW.md\`
17. \`ADGUARD_PILOT_ROLLOUT_PLAN.md\`
18. \`TAILSCALE_SPLIT_DNS_PLAN.md\`
19. \`ROUTER_LEASE_RECONCILIATION_RUNBOOK.md\`
20. \`PUBLIC_EDGE_ARCHITECTURE_PLAN.md\`
21. \`RASPBERRY_PI_RADIO_NODE_PLAN.md\`
22. \`AZURACAST_FIRST_STATION_BASELINE.md\`
23. \`RADIO_OPERATIONS_STANDARD.md\`
24. \`MEDIA_SERVER_PLAN.md\`
25. \`MEDIA_SERVER_CLIENT_SETUP.md\`
26. \`OPERATOR_TODO_QUEUE.md\`
27. \`PBS_VM_240_SETUP_PLAN.md\`
28. \`HAOS_VM_210_SETUP_PLAN.md\`
29. \`PORTABLE_BACKUP_USB_PLAN.md\`

## Canonical Sources

- \`README.md\` updated: \`$(mtime "${ROOT_DIR}/README.md")\`
- \`MASTERPLAN.md\` updated: \`$(mtime "${ROOT_DIR}/MASTERPLAN.md")\`
- \`MORNING_ROUTINE.md\` updated: \`$(mtime "${ROOT_DIR}/MORNING_ROUTINE.md")\`
- \`SECURITY_BASELINE.md\` updated: \`$(mtime "${ROOT_DIR}/SECURITY_BASELINE.md")\`
- \`SESSION_CLOSEOUT.md\` updated: \`$(mtime "${ROOT_DIR}/SESSION_CLOSEOUT.md")\`
- \`EVENING_ROUTINE.md\` updated: \`$(mtime "${ROOT_DIR}/EVENING_ROUTINE.md")\`
- \`GEMINI.md\` updated: \`$(mtime "${ROOT_DIR}/GEMINI.md")\`
- \`MEMORY.md\` updated: \`$(mtime "${ROOT_DIR}/MEMORY.md")\`
- \`NETWORK_INVENTORY.md\` updated: \`$(mtime "${ROOT_DIR}/NETWORK_INVENTORY.md")\`
- \`VM_AUDIT.md\` updated: \`$(mtime "${ROOT_DIR}/VM_AUDIT.md")\`
- \`BACKUP_RESTORE_PROOF.md\` updated: \`$(mtime "${ROOT_DIR}/BACKUP_RESTORE_PROOF.md")\`
- \`CAPACITY_REVIEW.md\` updated: \`$(mtime "${ROOT_DIR}/CAPACITY_REVIEW.md")\`
- \`RIGHTSIZING_MAINTENANCE_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/RIGHTSIZING_MAINTENANCE_PLAN.md")\`
- \`SURFACE_GO_FRONTEND_SETUP_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/SURFACE_GO_FRONTEND_SETUP_PLAN.md")\`
- \`MEDIA_AND_REMOTE_PREP.md\` updated: \`$(mtime "${ROOT_DIR}/MEDIA_AND_REMOTE_PREP.md")\`
- \`REMOTE_ACCESS_STANDARD.md\` updated: \`$(mtime "${ROOT_DIR}/REMOTE_ACCESS_STANDARD.md")\`
- \`REMOTE_ONLY_WORK_WINDOW.md\` updated: \`$(mtime "${ROOT_DIR}/REMOTE_ONLY_WORK_WINDOW.md")\`
- \`ADGUARD_PILOT_ROLLOUT_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/ADGUARD_PILOT_ROLLOUT_PLAN.md")\`
- \`TAILSCALE_SPLIT_DNS_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/TAILSCALE_SPLIT_DNS_PLAN.md")\`
- \`ROUTER_LEASE_RECONCILIATION_RUNBOOK.md\` updated: \`$(mtime "${ROOT_DIR}/ROUTER_LEASE_RECONCILIATION_RUNBOOK.md")\`
- \`PUBLIC_EDGE_ARCHITECTURE_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/PUBLIC_EDGE_ARCHITECTURE_PLAN.md")\`
- \`RASPBERRY_PI_RADIO_NODE_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/RASPBERRY_PI_RADIO_NODE_PLAN.md")\`
- \`AZURACAST_FIRST_STATION_BASELINE.md\` updated: \`$(mtime "${ROOT_DIR}/AZURACAST_FIRST_STATION_BASELINE.md")\`
- \`RADIO_OPERATIONS_STANDARD.md\` updated: \`$(mtime "${ROOT_DIR}/RADIO_OPERATIONS_STANDARD.md")\`
- \`MEDIA_SERVER_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/MEDIA_SERVER_PLAN.md")\`
- \`MEDIA_SERVER_CLIENT_SETUP.md\` updated: \`$(mtime "${ROOT_DIR}/MEDIA_SERVER_CLIENT_SETUP.md")\`
- \`OPERATOR_TODO_QUEUE.md\` updated: \`$(mtime "${ROOT_DIR}/OPERATOR_TODO_QUEUE.md")\`
- \`PBS_VM_240_SETUP_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/PBS_VM_240_SETUP_PLAN.md")\`
- \`HAOS_VM_210_SETUP_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/HAOS_VM_210_SETUP_PLAN.md")\`
- \`PORTABLE_BACKUP_USB_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/PORTABLE_BACKUP_USB_PLAN.md")\`
- \`ansible/inventory/hosts.yml\` updated: \`$(mtime "${ROOT_DIR}/ansible/inventory/hosts.yml")\`
- \`ansible/inventory/group_vars/all/vault.yml\` updated: \`$(mtime "${ROOT_DIR}/ansible/inventory/group_vars/all/vault.yml")\`

## Current Estate Snapshot

- Managed hosts in Ansible inventory: \`${inventory_count}\`
- Router baseline: \`192.168.2.1\` Vodafone Easy Box
- Planned future gateway: \`UniFi Cloud Gateway Ultra (UCG-Ultra)\`, not yet active
- Core business nodes: \`192.168.2.20\` toolbox, \`192.168.2.21\` nextcloud, \`192.168.2.22\` odoo, \`192.168.2.23\` paperless, \`192.168.2.24\` haos
- Toolbox network base: Caddy on \`192.168.2.20:80\`, AdGuard Home on \`192.168.2.20:53\` and localhost-only admin on \`127.0.0.1:3000\`, \`hs27.internal\` rewrites verified in opt-in mode
- Toolbox mobile Tailscale frontdoor: \`100.99.206.128:8443\` HA, \`:8444\` Odoo, \`:8445\` Nextcloud, \`:8446\` Paperless, \`:8447\` Portal, \`:8448\` Radio, \`:8449\` Media
- Toolbox Tailscale state: \`/dev/net/tun\` mapped, \`tailscaled\` active, backend \`Running\`, subnet route \`192.168.2.0/24\` is active in the Tailnet and Split-DNS for \`hs27.internal\` is operational
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from \`/opt/homeserver2027/stacks\` under systemd-managed local IaC
- Home Assistant OS is stable on \`192.168.2.24:8123\` and \`ha.hs27.internal\` now returns \`HTTP 200\` through Caddy
- Local Proxmox backup proof completed on \`2026-03-18\` for \`VM 200\`, \`VM 220\` and \`VM 230\`; daily local backup coverage now includes \`VM 210\`
- PBS runner path is live, the official installer ISO is staged, interim USB-backed storage is mounted on Proxmox at \`/srv/pbs-datastore\`, \`VM 240 pbs\` is installed on \`192.168.2.25\`, datastore \`hs27-interim\` is active, Proxmox storage \`pbs-interim\` is active, and the first green proof-backup plus restore drill are already verified for \`VM 220\`
- Capacity review says the host is memory-overcommitted on paper; immediate right-sizing candidates are \`VM 200\` and \`VM 220\`, while \`VM 210\` should not be reduced
- Right-sizing stage gate is green; the actual memory reduction remains a maintenance-window change and is not yet applied
- Shared frontend node on \`192.168.2.154\` is now rebuilt as \`surface-go-frontend\`; SSH, Tailnet admin on \`100.106.67.127\`, root sleep hardening, and the robust local portal path \`http://127.0.0.1:17827\` are live via the visible \`FRAWO Control\` launcher
- Local media prep is staged on the ZenBook: \`/dev/mmcblk0\` for Raspberry Pi, \`/dev/sdd\` is now the ready blue Ventoy install-/image-stick, and \`/dev/sdc1\` is the ready exFAT Favorites-stick \`FRAWO_FAVS\`
- Portable backup USB path has been repurposed: the dedicated \`64GB\` stick is attached directly to Proxmox as \`HS27_PORTABLEBK\`, mounted on \`/srv/portable-backup-usb\`, bind-mounted to \`/srv/pbs-datastore\`, and now backs the interim PBS-v1 path instead of continuing as a portable archive shuttle
- Raspberry-Pi radio node is live: \`radio-node\` on \`192.168.2.155\` / \`100.64.23.77\`, AzuraCast containers are running, \`radio.hs27.internal\` currently returns \`HTTP 302\` to \`/login\`, and the status API is reachable
- Raspberry-Pi radio node uses the conservative pi4_2gb_single_station_low_resource profile with about 1.8 GiB RAM, 2 GiB swap, about 21 GiB free rootfs, COMPOSE_HTTP_TIMEOUT=900, PHP_FPM_MAX_CHILDREN=2, NOW_PLAYING_DELAY_TIME=15, NOW_PLAYING_MAX_CONCURRENT_PROCESSES=1, and ENABLE_WEB_UPDATER=false
- Media server V1 is now live on \`CT 100 toolbox\`: Jellyfin is reachable internally on \`http://media.hs27.internal\`, directly on \`http://192.168.2.20:8096\`, and through the mobile Tailscale frontdoor on \`:8449\`; the startup wizard is complete and the music library is attached while the bootstrap import continues
- ZenBook remote posture is now stronger: Tailscale joined on \`100.76.249.126\` and AnyDesk is installed and active as a GUI fallback
- Remote-only work windows are now codified through \`REMOTE_ONLY_WORK_WINDOW.md\` and \`make remote-only-check\`

## Active Work Queue
$(section_body "${ROOT_DIR}/MEMORY.md" "## Aktuelle Arbeitsauftraege")

## Operator Actions Needed
$(section_body "${ROOT_DIR}/MEMORY.md" "## Aktive Operator-Aktionen")

## Tonight's Review Findings
$(section_body "${ROOT_DIR}/SESSION_CLOSEOUT.md" "## Review Findings")

## Best-Practice Actions
$(section_body "${ROOT_DIR}/NETWORK_INVENTORY.md" "## Current Best-Practice Actions")

## Collaboration Contract

- Update canonical source files instead of creating duplicate notes.
- Gemini and Codex should use the same shared files listed above.
- The user systemd path unit should refresh this file automatically after source-file changes.
- Manual fallback: \`make refresh-context\`
EOF

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

latest_artifact_file() {
  local root_dir="$1"
  local file_name="$2"
  local latest_dir
  latest_dir="$(
    find "${root_dir}" -mindepth 1 -maxdepth 1 -type d 2>/dev/null \
      | while IFS= read -r dir; do
          base="$(basename "${dir}")"
          [[ "${base}" =~ ^[0-9]{8}_[0-9]{6}$ ]] || continue
          printf '%s\n' "${dir}"
        done \
      | sort \
      | tail -n 1
  )"
  if [[ -z "${latest_dir}" ]]; then
    return 1
  fi
  printf '%s/%s\n' "${latest_dir}" "${file_name}"
}

summary_status() {
  local summary_path="$1"
  local check_id="$2"
  python3 - <<'PY' "${summary_path}" "${check_id}"
import csv
import sys

summary_path, check_id = sys.argv[1:3]

with open(summary_path, "r", encoding="utf-8") as handle:
    rows = list(csv.DictReader(handle, delimiter="\t"))

for row in rows:
    if row["id"] == check_id:
        print(row["status"])
        raise SystemExit(0)

print("unknown")
PY
}

production_gate_decision() {
  local gate_path="$1"
  python3 - <<'PY' "${gate_path}"
import sys

path = sys.argv[1]
decision = "unknown"
with open(path, "r", encoding="utf-8") as handle:
    for line in handle:
        if line.startswith("Decision: `") and line.rstrip().endswith("`"):
            decision = line.split("`", 2)[1]
            break

print(decision)
PY
}

inventory_count="$(awk '/ansible_host:/{count++} END {print count+0}' "${ROOT_DIR}/ansible/inventory/hosts.yml")"
git_branch="$(git -C "${ROOT_DIR}" branch --show-current 2>/dev/null || true)"
git_dirty_count="$(git -C "${ROOT_DIR}" status --short 2>/dev/null | wc -l | awk '{print $1}')"
generated_at="$(date '+%Y-%m-%d %H:%M:%S %Z')"
latest_stress_summary="$(latest_artifact_file "${ROOT_DIR}/artifacts/stress_tests" "summary.tsv")"
latest_release_mvp_gate="$(latest_artifact_file "${ROOT_DIR}/artifacts/release_mvp_gate" "release_mvp_gate.md")"
latest_production_gate="$(latest_artifact_file "${ROOT_DIR}/artifacts/production_gate" "production_gate.md")"
ansible_ping_status="unknown"
backup_list_status="unknown"
proxmox_backup_status="unknown"
pbs_stage_gate_status="unknown"
pbs_proof_status="unknown"
security_status="unknown"
release_mvp_decision="unknown"
production_decision="unknown"
readiness_findings_md=$(
  cat <<'EOF'
1. Die Plattform folgt jetzt zwei echten Freigabespuren:
   - Business-MVP fuer `Portal`, `Vaultwarden`, `Nextcloud`, `Paperless`, `Odoo`, STRATO-Mail und lokale Backups
   - Vollzertifizierung spaeter fuer `PBS`, `surface-go-frontend`, `Radio/AzuraCast` und Shared Frontend
2. Der Business-Kern ist technisch weitgehend gruen:
   - Inventory, Ansible, QGA, Toolbox, Vaultwarden-SMTP, lokale Backups und Security-Baseline sind im letzten Stresslauf bestanden.
3. Die Vollzertifizierung bleibt technisch blockiert:
   - `PBS` ist nicht gruen
   - `surface-go-frontend` ist aktuell nicht erreichbar
   - `Radio/AzuraCast` ist intern adressierbar, aber nicht als integrierter Produktionspfad verifiziert
4. Freigaben duerfen nur ueber Gate-Artefakte behauptet werden:
   - `release_mvp_gate` fuer den Arbeits-MVP
   - `production_gate` fuer das volle interne Produktionssiegel
EOF
)

if [[ -n "${latest_stress_summary}" ]]; then
  ansible_ping_status="$(summary_status "${latest_stress_summary}" "ansible-ping")"
  backup_list_status="$(summary_status "${latest_stress_summary}" "backup-list")"
  proxmox_backup_status="$(summary_status "${latest_stress_summary}" "proxmox-local-backup-check")"
  pbs_stage_gate_status="$(summary_status "${latest_stress_summary}" "pbs-stage-gate")"
  pbs_proof_status="$(summary_status "${latest_stress_summary}" "pbs-proof-check")"
  security_status="$(summary_status "${latest_stress_summary}" "security-baseline-check")"
fi

if [[ -n "${latest_production_gate}" ]]; then
  production_decision="$(production_gate_decision "${latest_production_gate}")"
fi
if [[ -n "${latest_release_mvp_gate}" ]]; then
  release_mvp_decision="$(production_gate_decision "${latest_release_mvp_gate}")"
fi

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

1. \`INTRODUCTION_PROMPT.md\`
2. \`BUSINESS_MVP_PROMPT.md\` oder \`WEBSITE_RELEASE_PROMPT.md\` oder \`FULL_CERTIFICATION_PROMPT.md\`
3. \`AI_BOOTSTRAP_CONTEXT.md\`
4. \`LIVE_CONTEXT.md\`
5. \`MASTERPLAN.md\`
6. \`OPERATIONS/OPERATOR_ROUTINES.md\`
7. \`SECURITY_BASELINE.md\`
8. \`SESSION_CLOSEOUT.md\`
9. \`GEMINI.md\`
10. \`MEMORY.md\`
11. \`NETWORK_INVENTORY.md\`
12. \`VM_AUDIT.md\`
13. \`BACKUP_RESTORE_PROOF.md\`
14. \`CAPACITY_REVIEW.md\`
15. \`RIGHTSIZING_MAINTENANCE_PLAN.md\`
16. \`SURFACE_GO_FRONTEND_SETUP_PLAN.md\`
17. \`MEDIA_AND_REMOTE_PREP.md\`
18. \`REMOTE_ACCESS_STANDARD.md\`
19. \`REMOTE_ONLY_WORK_WINDOW.md\`
20. \`ADGUARD_PILOT_ROLLOUT_PLAN.md\`
21. \`TAILSCALE_SPLIT_DNS_PLAN.md\`
22. \`ROUTER_LEASE_RECONCILIATION_RUNBOOK.md\`
23. \`PUBLIC_EDGE_ARCHITECTURE_PLAN.md\`
24. \`RASPBERRY_PI_RADIO_NODE_PLAN.md\`
25. \`RPI_RESOURCE_ALLOCATION_PLAN.md\`
26. \`AZURACAST_FIRST_STATION_BASELINE.md\`
27. \`RADIO_OPERATIONS_STANDARD.md\`
28. \`MEDIA_SERVER_PLAN.md\`
29. \`MEDIA_SERVER_CLIENT_SETUP.md\`
30. \`OPERATOR_TODO_QUEUE.md\`
31. \`PBS_VM_240_SETUP_PLAN.md\`
32. \`HAOS_VM_210_SETUP_PLAN.md\`
33. \`PORTABLE_BACKUP_USB_PLAN.md\`

## Canonical Sources

- \`INTRODUCTION_PROMPT.md\` updated: \`$(mtime "${ROOT_DIR}/INTRODUCTION_PROMPT.md")\`
- \`BUSINESS_MVP_PROMPT.md\` updated: \`$(mtime "${ROOT_DIR}/BUSINESS_MVP_PROMPT.md")\`
- \`WEBSITE_RELEASE_PROMPT.md\` updated: \`$(mtime "${ROOT_DIR}/WEBSITE_RELEASE_PROMPT.md")\`
- \`FULL_CERTIFICATION_PROMPT.md\` updated: \`$(mtime "${ROOT_DIR}/FULL_CERTIFICATION_PROMPT.md")\`
- \`AI_BOOTSTRAP_CONTEXT.md\` updated: \`$(mtime "${ROOT_DIR}/AI_BOOTSTRAP_CONTEXT.md")\`
- \`README.md\` updated: \`$(mtime "${ROOT_DIR}/README.md")\`
- \`MASTERPLAN.md\` updated: \`$(mtime "${ROOT_DIR}/MASTERPLAN.md")\`
- \`OPERATIONS/OPERATOR_ROUTINES.md\` updated: \`$(mtime "${ROOT_DIR}/OPERATIONS/OPERATOR_ROUTINES.md")\`
- \`SECURITY_BASELINE.md\` updated: \`$(mtime "${ROOT_DIR}/SECURITY_BASELINE.md")\`
- \`SESSION_CLOSEOUT.md\` updated: \`$(mtime "${ROOT_DIR}/SESSION_CLOSEOUT.md")\`
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
- \`RPI_RESOURCE_ALLOCATION_PLAN.md\` updated: \`$(mtime "${ROOT_DIR}/RPI_RESOURCE_ALLOCATION_PLAN.md")\`
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
- UCG transition gateway: \`UniFi Cloud Gateway Ultra (UCG-Ultra)\` active for \`proxmox-anker\` on VLAN 101 (\`10.1.0.92/24\`), with legacy aliases \`192.168.2.10/24\` + temporary \`192.168.2.1/24\`
- UCG static route \`Anker-Legacy-Bridge\` set: \`192.168.2.0/24 -> 10.1.0.92\`; WAN overlap keeps it shadowed and it now serves only as an emergency fallback
- Core business nodes: \`10.1.0.20\` toolbox, \`10.1.0.21\` nextcloud, \`10.1.0.22\` odoo, \`10.1.0.23\` paperless, \`10.1.0.24\` haos, \`10.1.0.26\` vaultwarden, \`10.1.0.30\` storage-node
- Latest stress summary: \`${latest_stress_summary:-missing}\`
- Latest release-MVP gate: \`${latest_release_mvp_gate:-missing}\` -> \`${release_mvp_decision}\`
- Latest production gate: \`${latest_production_gate:-missing}\` -> \`${production_decision}\`
- Toolbox network base: Caddy on \`10.1.0.20:80\`, AdGuard Home on \`10.1.0.20:53\` and localhost-only admin on \`127.0.0.1:3000\`, \`hs27.internal\` rewrites verified in opt-in mode
- Toolbox mobile Tailscale frontdoor: \`100.99.206.128:8443\` HA, \`:8444\` Odoo, \`:8445\` Nextcloud, \`:8446\` Paperless, \`:8447\` Portal, \`:8448\` Radio (502: node \`100.64.23.77\` offline), \`:8449\` Media
- Toolbox Tailscale state: \`/dev/net/tun\` mapped, \`tailscaled\` active, backend \`Running\`, subnet route \`10.1.0.0/24\` is advertised (Tailnet approval pending), Split-DNS still needs to be updated to \`10.1.0.20\`
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from \`/opt/homeserver2027/stacks\` under systemd-managed local IaC
- Home Assistant OS is stable on \`10.1.0.24:8123\` and \`ha.hs27.internal\` now returns \`HTTP 200\` through Caddy
- Direct Ansible management status: \`ansible-ping=${ansible_ping_status}\`
- Local Proxmox backup status: \`backup-list=${backup_list_status}\`, \`proxmox-local-backup-check=${proxmox_backup_status}\`; the latest stress run is the deciding source for whether real archives under \`/var/lib/vz/dump\` are currently proven
- PBS status from latest gate: \`pbs-stage-gate=${pbs_stage_gate_status}\`, \`pbs-proof-check=${pbs_proof_status}\`; \`VM 240\` existiert, ist aber gestoppt und der verifizierte Datastore-/Proof-Pfad ist aktuell nicht gruen
- Security baseline from latest gate: \`security-baseline-check=${security_status}\`
- Capacity review says the host is memory-overcommitted on paper; immediate right-sizing candidates are \`VM 200\` and \`VM 220\`, while \`VM 210\` should not be reduced
- Right-sizing stage gate is green; the actual memory reduction remains a maintenance-window change and is not yet applied
- Shared frontend node \`surface-go-frontend\` on \`192.168.2.154\` remains blocked in the live audit; SSH, HTTP and HTTPS are currently closed and the active recommendation is \`clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook\`
- Local media prep is staged on the ZenBook: \`/dev/mmcblk0\` for Raspberry Pi, \`/dev/sdd\` is now the ready blue Ventoy install-/image-stick, and \`/dev/sdc1\` is the ready exFAT Favorites-stick \`FRAWO_FAVS\`
- Portable backup / PBS datastore path is currently not verified green in the latest PBS checks; der sichtbare USB-Stick meldet derzeit \`No medium found\`, und die datentragende USB-SSD bleibt bis zu einer expliziten Freigabe unangetastet
- Raspberry-Pi radio node remains only partially green: \`radio.hs27.internal\` and the mobile radio frontdoor answer through the toolbox, but the live audit still shows \`rpi_radio_integrated=no\` und \`rpi_radio_usb_music_ready=no\`
- Radio/AzuraCast is therefore not part of the current business-MVP release decision
- Media server V1 is now live on \`CT 100 toolbox\`: Jellyfin is reachable internally on \`http://media.hs27.internal\`, directly on \`http://10.1.0.20:8096\`, and through the mobile Tailscale frontdoor on \`:8449\`; the obsolete local bootstrap sync is retired and Jellyfin reads from the central SMB-backed media path
- ZenBook remote posture is now stronger: Tailscale joined on \`100.76.249.126\` and AnyDesk is installed and active as a GUI fallback
- Remote-only work windows are now codified through \`REMOTE_ONLY_WORK_WINDOW.md\` and \`make remote-only-check\`

## Active Work Queue
$(section_body "${ROOT_DIR}/MEMORY.md" "## Aktuelle Arbeitsauftraege")

## Operator Actions Needed
$(section_body "${ROOT_DIR}/MEMORY.md" "## Aktive Operator-Aktionen")

## Current Readiness Findings
${readiness_findings_md}

## Best-Practice Actions
$(section_body "${ROOT_DIR}/NETWORK_INVENTORY.md" "## Current Best-Practice Actions")

## Collaboration Contract

- Update canonical source files instead of creating duplicate notes.
- Gemini and Codex should use the same shared files listed above.
- The user systemd path unit should refresh this file automatically after source-file changes.
- Manual fallback: \`make refresh-context\`
EOF

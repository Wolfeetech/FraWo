# Homeserver 2027 Ops Workspace

This is the shared operational workspace for Homeserver 2027.

## Workspace Identity

- Human-facing name: `Homeserver 2027 Ops Workspace`
- Stable alias: `~/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop shortcut target: `~/Desktop/Homeserver 2027 Workspace`
- Backing store: the Antigravity-managed workspace directory remains in place to avoid breaking internal tooling

## Read Order

1. `LIVE_CONTEXT.md`
2. `MASTERPLAN.md`
3. `MORNING_ROUTINE.md`
4. `SECURITY_BASELINE.md`
5. `SESSION_CLOSEOUT.md`
6. `GEMINI.md`
7. `MEMORY.md`
8. `NETWORK_INVENTORY.md`
9. `VM_AUDIT.md`
10. `BACKUP_RESTORE_PROOF.md`
11. `CAPACITY_REVIEW.md`
12. `RIGHTSIZING_MAINTENANCE_PLAN.md`
13. `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
14. `MEDIA_AND_REMOTE_PREP.md`
15. `REMOTE_ACCESS_STANDARD.md`
16. `REMOTE_ONLY_WORK_WINDOW.md`
17. `ADGUARD_PILOT_ROLLOUT_PLAN.md`
18. `TAILSCALE_SPLIT_DNS_PLAN.md`
19. `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md`
20. `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
21. `RASPBERRY_PI_RADIO_NODE_PLAN.md`
22. `RPI_RESOURCE_ALLOCATION_PLAN.md`
23. `PBS_VM_240_SETUP_PLAN.md`
24. `HAOS_VM_210_SETUP_PLAN.md`

## Canonical Files

- `LIVE_CONTEXT.md`
  - always-open handoff summary for Codex and Gemini
- `MASTERPLAN.md`
  - single-file strategic roadmap from current state to professionally finished target state
- `GEMINI.md`
  - Gemini-specific operating rules and shared collaboration contract
- `AGENTS.md`
  - generic agent rules for any AI collaborator
- `MEMORY.md`
  - long-lived project knowledge base
- `NETWORK_INVENTORY.md`
  - canonical LAN inventory
- `VM_AUDIT.md`
  - verified runtime state and remediation notes
- `BACKUP_RESTORE_PROOF.md`
  - latest verified local backup and restore proof until PBS is live
- `CAPACITY_REVIEW.md`
  - current sizing decision for host, toolbox and VMs based on live runtime data
- `RIGHTSIZING_MAINTENANCE_PLAN.md`
  - staged maintenance path for reducing Nextcloud and Odoo RAM safely
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
  - clean-rebuild and post-install baseline path for the shared Surface Go frontend node
- `MEDIA_AND_REMOTE_PREP.md`
  - canonical prep path for Raspberry Pi install media, Surface install USB and AnyDesk on the ZenBook
- `REMOTE_ACCESS_STANDARD.md`
  - canonical remote-access posture for Tailscale-first and AnyDesk-fallback operation
- `REMOTE_ONLY_WORK_WINDOW.md`
  - exact remote-only work order for AnyDesk/Tailscale sessions without physical access
- `ADGUARD_PILOT_ROLLOUT_PLAN.md`
  - controlled DNS pilot and rollback path before any LAN-wide AdGuard promotion
- `TAILSCALE_SPLIT_DNS_PLAN.md`
  - exact split-DNS rollout path for `hs27.internal` over Tailscale after route approval
- `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md`
  - exact browser-first work path for resolving the remaining Easy-Box labels and unknown hosts
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
  - professional target architecture for the later public website and radio exposure
- `RASPBERRY_PI_RADIO_NODE_PLAN.md`
  - target architecture for the future dedicated Raspberry Pi 4 radio node
- `AZURACAST_FIRST_STATION_BASELINE.md`
  - exact first-station settings and low-resource operating baseline for the Pi radio node
- `RPI_RESOURCE_ALLOCATION_PLAN.md`
  - verified live resource budget and low-resource tuning profile for the Pi radio node
- `TAILSCALE_PHONE_ACCESS.md`
  - practical mobile-access runbook for subnet routing, DNS and phone testing
- `PBS_VM_240_SETUP_PLAN.md`
  - controlled rollout path and stage gates for the planned PBS VM
- `MORNING_ROUTINE.md`
  - canonical start-of-day checklist and execution order
- `SECURITY_BASELINE.md`
  - current repeatable security posture and daily security checks
- `ansible/inventory/hosts.yml`
  - machine-readable infrastructure inventory
- `ansible/inventory/group_vars/all/vault.yml`
  - encrypted secrets only
- `ansible/playbooks/deploy_business_stacks.yml`
  - canonical deployment path for Nextcloud, Odoo and Paperless compose stacks
- `ansible/playbooks/deploy_haos_vm_runner.yml`
  - controlled deployment path for the HAOS runner script on Proxmox
- `ansible/playbooks/deploy_pbs_vm_runner.yml`
  - controlled deployment path for the PBS runner script on Proxmox
- `ansible/playbooks/bootstrap_surface_go_frontend.yml`
  - post-rebuild baseline path for the shared Surface Go frontend node
- `ansible/inventory/host_vars/*.yml`
  - per-VM stack metadata for the business services

## Workspace Presets

- `.editorconfig`
  - consistent whitespace, UTF-8 and LF endings
- `.gitattributes`
  - normalized text handling
- `.gitignore`
  - editor, cache and local noise excluded
- `Makefile`
  - common validation and sync shortcuts

## Shared Agent Workflow

1. Read `LIVE_CONTEXT.md` before making changes.
2. Update the canonical source file for the thing you changed.
3. Do not create side notes in random scratch files.
4. Let the auto-sync service refresh `LIVE_CONTEXT.md`, or run `make refresh-context`.

## Operator Handoff Standard

- If Codex or Gemini is blocked by a manual, physical or account-bound dependency, they must say it explicitly using the prefix `AKTION VON DIR ERFORDERLICH:`.
- Every such handoff must contain:
  - the exact action needed from the operator
  - why that action is required
  - what will resume automatically afterwards
- Open operator dependencies must be reflected in `MEMORY.md` under `## Aktive Operator-Aktionen` and therefore appear in `LIVE_CONTEXT.md`.

## Quick Commands

```bash
./scripts/start_day.sh
./scripts/close_day.sh
make refresh-context
make inventory-check
make ansible-ping
make qga-check
make backup-list
make backup-proof
make backup-prune-dry-run
make backup-prune
make capacity-review
make surface-go-check
make ansible-syntax-check-surface-go
make surface-go-bootstrap
make ansible-syntax-check-rpi-radio
make ansible-syntax-check-rpi-azuracast-host
make ansible-syntax-check-rpi-azuracast-tuning
make rpi-firstboot-seed
make rpi-radio-bootstrap
make rpi-azuracast-host-prepare
make rpi-azuracast-deploy
make rpi-azuracast-tune
make rpi-radio-check
make rpi-radio-integration-check
make rpi-azuracast-check
make rpi-resource-check
make business-drift-check
make ansible-syntax-check-toolbox
make ansible-syntax-check-toolbox-tailscale
make ansible-syntax-check-toolbox-mobile-firewall
make toolbox-deploy
make toolbox-network-check
make toolbox-tun-prep
make toolbox-tailscale-prep
make toolbox-tailscale-check
make toolbox-tailscale-login-url
make toolbox-tailscale-join-assist
make toolbox-tailscale-mobile-check
make toolbox-mobile-firewall-deploy
make rightsize-stage-gate
make rightsize-plan
make rightsize-apply
make easybox-browser-probe
make pbs-preflight
make pbs-stage-gate
make pbs-iso-stage
make ansible-syntax-check-pbs
make pbs-runner-deploy
make pbs-vm-check
make haos-preflight
make haos-stage-gate
make ansible-syntax-check-haos
make haos-runner-deploy
make haos-vm-check
make security-baseline-check
make ansible-syntax-check-business-hardening
make business-hardening-deploy
make easybox-browser-probe
make easybox-authenticated-overview
make media-devices
make media-fetch
make surface-iso-fetch
make surface-usb-prepare
make rpi-sd-flash
make anydesk-zenbook-install
make zenbook-remote-check
make remote-only-check
make adguard-pilot-check
make tailscale-split-dns-check
make inventory-resolution-check
make ansible-syntax-check-proxmox-backups
make proxmox-local-backup-deploy
make proxmox-local-backup-check
make ansible-syntax-check
make ansible-list-business
make proxmox-storage-check
```

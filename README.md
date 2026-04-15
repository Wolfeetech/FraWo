# MASTER SINGLE SOURCE OF TRUTH (SSOT)

> [!IMPORTANT]
> **Dies ist das einzige und massgebliche Projektverzeichnis für Homeserver 2027.**
> Alle technischen Fakten, Automatisierungen und Dokumentationen in diesem Repository sind die absolute Wahrheit für das FraWo-Estate.
>
> **Canonical Upstream**: [https://github.com/Wolfeetech/FraWo](https://github.com/Wolfeetech/FraWo)

---

> **Solo Operator? Start here.** This workspace runs a hybrid Proxmox home-lab for the GbR "FraWo".
> If you feel lost, read the three lines under [Start Here](#start-here) and pick your objective.
>
> 📱 **On your phone or don't know where to start?**
> → Open **[`OPS_CONTROL_CENTER.md`](OPS_CONTROL_CENTER.md)** – your single entry point with status, categories, phone-safe links, and exactly one next action.

## Workspace Identity

- Name: `Homeserver 2027 Ops Workspace`
- Stabiler Alias: `~/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop-Shortcut: `Homeserver 2027 Workspace`
- Backing Store: Das Antigravity-Arbeitsverzeichnis bleibt technisch unverändert.
- Windows-Bootstrap:
  - `scripts\bootstrap_windows_workspace.cmd` führt die initiale Einrichtung des Alias und des Shortcuts durch.

## Read Order

Read only this short boot path first:

1. `INTRODUCTION_PROMPT.md`
2. `AI_BOOTSTRAP_CONTEXT.md`
3. `LIVE_CONTEXT.md`
4. `OPS_HOME.md`
5. `OPERATOR_TODO_QUEUE.md`
6. `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
7. `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`
8. `MASTERPLAN.md`

Only then open the service- or topic-specific canonical file you actually need.
Do not treat the rest of the workspace as mandatory boot reading.
After `INTRODUCTION_PROMPT.md`, choose the narrowest specialized prompt that fits the task:

- `BUSINESS_MVP_PROMPT.md`
- `WEBSITE_RELEASE_PROMPT.md`
- `FULL_CERTIFICATION_PROMPT.md`

## Canonical Files

- `INTRODUCTION_PROMPT.md`
  - hard-facts-only research bootstrap based on the latest live audit and runtime checks
- `BUSINESS_MVP_PROMPT.md`
  - specialized research prompt for the current internal business MVP only
- `WEBSITE_RELEASE_PROMPT.md`
  - specialized research prompt for the first public website release only
- `FULL_CERTIFICATION_PROMPT.md`
  - specialized research prompt for the strict full internal certification track
- `GEMINI_BROWSER_MVP_ACCEPTANCE_PROMPT.md`
  - ready-to-run browser prompt for Gemini to execute the open MVP UI acceptance checks
- `GEMINI_BROWSER_WEBSITE_RELEASE_PROMPT.md`
  - ready-to-run browser prompt for Gemini to execute the public website browser acceptance
- `AI_BOOTSTRAP_CONTEXT.md`
  - read-first AI bootstrap for server, page, user and rollout context
- `LIVE_CONTEXT.md`
  - always-open handoff summary for Codex and Gemini
- `OPS_HOME.md`
  - canonical operator start page and navigation hub
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
- `MEDIA_SERVER_PLAN.md`
  - canonical rollout and target state for Jellyfin V1 on toolbox
- `MEDIA_SERVER_CLIENT_SETUP.md`
  - operator runbook for TV, browser and mobile client connection paths
- `OPERATIONS/MAIL_OPERATIONS.md`
  - canonical operator path for mailbox rollout and app SMTP
- `OPERATIONS/OPERATOR_ROUTINES.md`
  - canonical start-of-day, close-day and handoff control path
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
  - canonical operator path for Wolf, Franz and device onboarding
- `OPERATOR_TODO_QUEUE.md`
  - short operator-facing queue for the next manual unblock steps
- `PBS_VM_240_SETUP_PLAN.md`
  - controlled rollout path and stage gates for the planned PBS VM
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

## Consolidated Repositories

This repository is the Single Source of Truth (SSOT). Key projects have been integrated via Git Subtrees:

### Active Apps
- **[`apps/yourparty/`](apps/yourparty/)** - Community radio application with mood-based playlists.
  - Synced from: `wolfeetech/yourparty-tech`
- **[`apps/fayanet/`](apps/fayanet/)** - Network security manager (Vaultwarden + Nginx).
  - Synced from: `wolfeetech/FaYa-Net`

### Automation
Run [`./scripts/sync-subtrees.sh`](scripts/sync-subtrees.sh) to pull latest subtree updates.

### Consolidation Documentation
See **[`CONSOLIDATION.md`](CONSOLIDATION.md)** and **[`CONSOLIDATION_CHANGELOG.txt`](CONSOLIDATION_CHANGELOG.txt)** for migration details and timeline.

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

1. Read `INTRODUCTION_PROMPT.md`, `AI_BOOTSTRAP_CONTEXT.md`, and `LIVE_CONTEXT.md` before making changes.
2. Update the canonical source file for the thing you changed.
3. Do not create side notes in random scratch files.
4. Let the auto-sync service refresh `LIVE_CONTEXT.md`, or run `make refresh-context`.
5. Keep the root portal and Franz portal at MVP scope until the current business core is visibly stable.

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
make release-mvp-audit
make release-mvp-gate
make website-release-audit
make website-release-gate
make stockenweiler-inventory-check
make stockenweiler-inventory-report
make stockenweiler-support-brief
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
make basics-check
make ansible-syntax-check-toolbox
make ansible-syntax-check-toolbox-tailscale
make ansible-syntax-check-toolbox-mobile-firewall
make toolbox-deploy
make toolbox-network-check
make toolbox-portal-status-check
make toolbox-tun-prep
make toolbox-tailscale-prep
make toolbox-tailscale-check
make toolbox-tailscale-login-url
make toolbox-tailscale-join-assist
make toolbox-tailscale-mobile-check
make toolbox-mobile-firewall-deploy
make toolbox-media-check
make toolbox-media-sync-check
make toolbox-media-bootstrap-progress
make toolbox-music-library-report
make toolbox-music-scan-issues
make toolbox-music-curation-candidates
make toolbox-music-curated-layout
make toolbox-music-quarantine-candidates
make toolbox-music-selection-seed-report
make toolbox-music-selection-sync
make ops-brief
make operator-todos
make surface-go-root-sleep-harden
make rightsize-stage-gate
make rightsize-plan
make rightsize-apply
make easybox-browser-probe
make pbs-preflight
make pbs-stage-gate
make pbs-proof-check
make app-smtp-check
make pbs-restore-proof
make inventory-unknown-report
make pbs-iso-stage
make pbs-rebuild-storage-audit
make pbs-rebuild-contract-check
make pbs-device-inventory
make pbs-contract-prefill BOOT_SERIAL=... DATASTORE_SERIAL=... APPROVED_BY=...
make ansible-syntax-check-pbs
make pbs-runner-deploy
make pbs-vm-check
make pbs-guest-check
make pbs-datastore-prepare DEV=/dev/sdX
make pbs-vm240-reconcile
make pbs-guarded-rebuild
make ansible-syntax-check-app-smtp
make app-smtp-deploy
make portable-backup-usb-prepare DEV=/dev/sdX
make portable-backup-usb-autoprepare
make portable-backup-usb-fill
make portable-backup-usb-check
make portable-backup-usb-run
make haos-preflight
make haos-usb-audit
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

## Local Runtime Overrides

- keep live SMTP credentials out of committed repo files
- use `ansible/inventory/group_vars/all/mail_runtime.local.yml.example` as the local template
- real local file:
  - `ansible/inventory/group_vars/all/mail_runtime.local.yml`
- preferred password path:
  - PowerShell: `$env:HOMESERVER_MAIL_SMTP_PASSWORD='...'`
- Windows helper:
  - `.\scripts\run_app_smtp_deploy.ps1`
- productive app SMTP rollout:
  1. create the local runtime file with `homeserver_mail_app_smtp_enabled: true`
  2. set the SMTP username locally
  3. export `HOMESERVER_MAIL_SMTP_PASSWORD`
  4. run `make app-smtp-deploy`
  5. run `make app-smtp-check`

# Live Context

## Workspace

- Name: `Homeserver 2027 Ops Workspace`
- Alias: `/home/wolf/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop shortcut: `/home/wolf/Desktop/Homeserver 2027 Workspace`
- Generated at: `2026-03-30 07:42:58 CEST`
- Git branch: `main`
- Pending git changes: `500`

## Shared Read Order

1. `INTRODUCTION_PROMPT.md`
2. `BUSINESS_MVP_PROMPT.md` oder `WEBSITE_RELEASE_PROMPT.md` oder `FULL_CERTIFICATION_PROMPT.md`
3. `AI_BOOTSTRAP_CONTEXT.md`
4. `LIVE_CONTEXT.md`
5. `MASTERPLAN.md`
6. `OPERATIONS/OPERATOR_ROUTINES.md`
7. `SECURITY_BASELINE.md`
8. `SESSION_CLOSEOUT.md`
9. `GEMINI.md`
10. `MEMORY.md`
11. `NETWORK_INVENTORY.md`
12. `VM_AUDIT.md`
13. `BACKUP_RESTORE_PROOF.md`
14. `CAPACITY_REVIEW.md`
15. `RIGHTSIZING_MAINTENANCE_PLAN.md`
16. `SURFACE_GO_FRONTEND_SETUP_PLAN.md`
17. `MEDIA_AND_REMOTE_PREP.md`
18. `REMOTE_ACCESS_STANDARD.md`
19. `REMOTE_ONLY_WORK_WINDOW.md`
20. `ADGUARD_PILOT_ROLLOUT_PLAN.md`
21. `TAILSCALE_SPLIT_DNS_PLAN.md`
22. `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md`
23. `PUBLIC_EDGE_ARCHITECTURE_PLAN.md`
24. `RASPBERRY_PI_RADIO_NODE_PLAN.md`
25. `RPI_RESOURCE_ALLOCATION_PLAN.md`
26. `AZURACAST_FIRST_STATION_BASELINE.md`
27. `RADIO_OPERATIONS_STANDARD.md`
28. `MEDIA_SERVER_PLAN.md`
29. `MEDIA_SERVER_CLIENT_SETUP.md`
30. `OPERATOR_TODO_QUEUE.md`
31. `PBS_VM_240_SETUP_PLAN.md`
32. `HAOS_VM_210_SETUP_PLAN.md`
33. `PORTABLE_BACKUP_USB_PLAN.md`

## Canonical Sources

- `INTRODUCTION_PROMPT.md` updated: `2026-03-28 07:18:20`
- `BUSINESS_MVP_PROMPT.md` updated: `2026-03-28 07:18:15`
- `WEBSITE_RELEASE_PROMPT.md` updated: `2026-03-28 07:18:15`
- `FULL_CERTIFICATION_PROMPT.md` updated: `2026-03-28 07:18:15`
- `AI_BOOTSTRAP_CONTEXT.md` updated: `2026-03-30 07:32:46`
- `README.md` updated: `2026-03-30 07:42:21`
- `MASTERPLAN.md` updated: `2026-03-30 07:31:50`
- `OPERATIONS/OPERATOR_ROUTINES.md` updated: `2026-03-26 23:23:08`
- `SECURITY_BASELINE.md` updated: `2026-03-24 11:50:08`
- `SESSION_CLOSEOUT.md` updated: `2026-03-24 19:23:44`
- `GEMINI.md` updated: `2026-03-30 06:19:37`
- `MEMORY.md` updated: `2026-03-28 10:09:33`
- `NETWORK_INVENTORY.md` updated: `2026-03-25 18:09:01`
- `VM_AUDIT.md` updated: `2026-03-24 12:03:50`
- `BACKUP_RESTORE_PROOF.md` updated: `2026-03-25 18:07:10`
- `CAPACITY_REVIEW.md` updated: `2026-03-24 11:50:08`
- `RIGHTSIZING_MAINTENANCE_PLAN.md` updated: `2026-03-24 11:50:08`
- `SURFACE_GO_FRONTEND_SETUP_PLAN.md` updated: `2026-03-24 11:50:08`
- `MEDIA_AND_REMOTE_PREP.md` updated: `2026-03-24 11:50:08`
- `REMOTE_ACCESS_STANDARD.md` updated: `2026-03-24 11:50:08`
- `REMOTE_ONLY_WORK_WINDOW.md` updated: `2026-03-24 11:50:08`
- `ADGUARD_PILOT_ROLLOUT_PLAN.md` updated: `2026-03-24 11:50:08`
- `TAILSCALE_SPLIT_DNS_PLAN.md` updated: `2026-03-24 11:50:08`
- `ROUTER_LEASE_RECONCILIATION_RUNBOOK.md` updated: `2026-03-24 11:50:08`
- `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` updated: `2026-03-30 06:33:46`
- `RASPBERRY_PI_RADIO_NODE_PLAN.md` updated: `2026-03-24 11:50:08`
- `RPI_RESOURCE_ALLOCATION_PLAN.md` updated: `2026-03-24 11:50:08`
- `AZURACAST_FIRST_STATION_BASELINE.md` updated: `2026-03-26 08:51:37`
- `RADIO_OPERATIONS_STANDARD.md` updated: `2026-03-24 11:50:08`
- `MEDIA_SERVER_PLAN.md` updated: `2026-03-26 22:26:25`
- `MEDIA_SERVER_CLIENT_SETUP.md` updated: `2026-03-25 13:44:07`
- `OPERATOR_TODO_QUEUE.md` updated: `2026-03-30 07:32:46`
- `PBS_VM_240_SETUP_PLAN.md` updated: `2026-03-27 08:57:47`
- `HAOS_VM_210_SETUP_PLAN.md` updated: `2026-03-24 11:50:08`
- `PORTABLE_BACKUP_USB_PLAN.md` updated: `2026-03-24 11:50:08`
- `ansible/inventory/hosts.yml` updated: `2026-03-27 17:28:29`
- `ansible/inventory/group_vars/all/vault.yml` updated: `2026-03-26 23:10:18`

## Current Estate Snapshot

- Managed hosts in Ansible inventory: `29`
- Router baseline: `192.168.2.1` Vodafone Easy Box
- Planned future gateway: `UniFi Cloud Gateway Ultra (UCG-Ultra)` is now active in a test segment; `proxmox-anker` moved to `10.1.0.92/24` (GW `10.1.0.1`)
- Core business nodes are still on `192.168.2.0/24` (toolbox/nextcloud/odoo/paperless/haos), but are currently unreachable from `wolfstudiopc` while the UCG segment is active
- Proxmox network config is staged back to static `192.168.2.10/24` on `vmbr0`, pending physical port move + network reload
- Latest stress summary: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_234807/summary.tsv`
- Latest release-MVP gate: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_gate/20260328_072307/release_mvp_gate.md` -> `BLOCKED`
- Latest production gate: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/production_gate/20260328_072130/production_gate.md` -> `BLOCKED`
- Toolbox network base: Caddy on `192.168.2.20:80`, AdGuard Home on `192.168.2.20:53` and localhost-only admin on `127.0.0.1:3000`, `hs27.internal` rewrites verified in opt-in mode (currently unreachable from `wolfstudiopc`)
- Toolbox mobile Tailscale frontdoor: `100.99.206.128:8443` HA, `:8444` Odoo, `:8445` Nextcloud, `:8446` Paperless, `:8447` Portal, `:8448` Radio, `:8449` Media (currently unreachable from `wolfstudiopc`)
- Toolbox Tailscale state: `/dev/net/tun` mapped, `tailscaled` active, backend `Running`, subnet route `192.168.2.0/24` is active in the Tailnet and Split-DNS for `hs27.internal` is operational
- VM 200, VM 210, VM 220 and VM 230: QEMU Guest Agent verified from Proxmox during latest audit
- Business stacks are running from `/opt/homeserver2027/stacks` under systemd-managed local IaC
- Home Assistant OS is stable on `192.168.2.24:8123` and `ha.hs27.internal` now returns `HTTP 200` through Caddy
- Direct Ansible management status: `ansible-ping=passed`
- Local Proxmox backup status: `backup-list=passed`, `proxmox-local-backup-check=passed`; the latest stress run is the deciding source for whether real archives under `/var/lib/vz/dump` are currently proven
- PBS status from latest gate: `pbs-stage-gate=failed`, `pbs-proof-check=failed`; `VM 240` existiert, ist aber gestoppt und der verifizierte Datastore-/Proof-Pfad ist aktuell nicht gruen
- Security baseline from latest gate: `security-baseline-check=passed`
- Capacity review says the host is memory-overcommitted on paper; immediate right-sizing candidates are `VM 200` and `VM 220`, while `VM 210` should not be reduced
- Right-sizing stage gate is green; the actual memory reduction remains a maintenance-window change and is not yet applied
- Shared frontend node `surface-go-frontend` on `192.168.2.154` remains blocked in the live audit; SSH, HTTP and HTTPS are currently closed and the active recommendation is `clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook`
- Local media prep is staged on the ZenBook: `/dev/mmcblk0` for Raspberry Pi, `/dev/sdd` is now the ready blue Ventoy install-/image-stick, and `/dev/sdc1` is the ready exFAT Favorites-stick `FRAWO_FAVS`
- Portable backup / PBS datastore path is currently not verified green in the latest PBS checks; der sichtbare USB-Stick meldet derzeit `No medium found`, und die datentragende USB-SSD bleibt bis zu einer expliziten Freigabe unangetastet
- Raspberry-Pi radio node remains only partially green: `radio.hs27.internal` and the mobile radio frontdoor answer through the toolbox, but the live audit still shows `rpi_radio_integrated=no` und `rpi_radio_usb_music_ready=no`
- Radio/AzuraCast is therefore not part of the current business-MVP release decision
- Media server V1 is now live on `CT 100 toolbox`: Jellyfin is reachable internally on `http://media.hs27.internal`, directly on `http://192.168.2.20:8096`, and through the mobile Tailscale frontdoor on `:8449`; the obsolete local bootstrap sync is retired and Jellyfin reads from the central SMB-backed media path
- ZenBook remote posture is now stronger: Tailscale joined on `100.76.249.126` and AnyDesk is installed and active as a GUI fallback
- Remote-only work windows are now codified through `REMOTE_ONLY_WORK_WINDOW.md` and `make remote-only-check`

## Active Work Queue


## Operator Actions Needed


## Current Readiness Findings
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

## Best-Practice Actions

1. Freeze a canonical device register now and update it only from scan plus router-lease reconciliation.
2. Reserve or document fixed addresses for all infrastructure and business nodes on the Easy Box.
3. Keep unmanaged household and IoT devices explicitly separated in inventory even before VLAN-capable hardware exists.
4. Treat `unknown-review` devices as temporary exceptions and close them out before exposing any services over Tailscale.
5. Only promote devices into `trusted-clients` after owner and management posture are known.
6. Treat the UCG-Ultra as a dedicated later-phase network cutover, not as a side-task during current LXC/VM rollout work.
7. Keep router-only names that are not yet tied to a live IP explicit in the notes instead of guessing their mapping.
8. Introduce AdGuard Home first as an opt-in internal DNS service, not as immediate default DNS for the whole LAN.
9. Treat public exposure as its own hardening phase with edge separation, not as an extension of the current flat-LAN toolbox phase.
10. Treat shared frontend devices as kiosk-first endpoints, not as ad hoc desktop-server hybrids.

## Collaboration Contract

- Update canonical source files instead of creating duplicate notes.
- Gemini and Codex should use the same shared files listed above.
- The user systemd path unit should refresh this file automatically after source-file changes.
- Manual fallback: `make refresh-context`

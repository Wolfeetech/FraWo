# Stockenweiler Inventory Report

Inventory source: `C:/Users/StudioPC/Documents/Homeserver 2027 Workspace/manifests/stockenweiler/site_inventory.json`

## Canonical Domain

- canonical: `online-prinz.de`
- legacy: `prinz-stockenweiler.de`

## Access Model

- primary remote access: `tailscale`
- fallback remote access: `anydesk`
- WAN admin exposure allowed: `False`
- site-to-site VPN allowed: `False`

## Current Known Facts

- `router`: `FRITZ!Box 5690 Pro` @ `192.168.178.1`
- `proxmox`: `proxmox Host` @ `192.168.178.25`
- `home_assistant`: `homeassistant` @ `192.168.178.67`
- `printer_scanner`: `Brother - Drucker` @ `192.168.178.153`
- `magenta_tv`: `MagentaTV` @ `192.168.178.120`

## Endpoint Status Counts

- `legacy_fact_needs_revalidation`: `5`
- `pending_inventory`: `2`

## Current Blockers

- No first live remote onboarding has happened yet.
- Current on-site main PC identity is still unresolved; operator stated on 2026-03-31 that the former main PC anchor was this StudioPC.
- Phone identity is still unresolved.
- Current StudioPC is not on the 192.168.178.0/24 LAN right now; direct SSH to 192.168.178.25 timed out during recovery on 2026-03-31.
- UCG and broader gateway work stay deferred while the operator 2FA path remains blocked.

## Issues

- none

## Legacy Conflicts To Revalidate

- `proxmox_host_ip`: best guess `192.168.178.25`, conflicting legacy `192.168.178.172`
- `home_assistant_ip`: best guess `192.168.178.67`, conflicting legacy `192.168.178.68`
- `ip_192.168.178.120_role`: best guess `MagentaTV`, conflicting legacy `\\192.168.178.120\scans\Familie Prinz`

## Legacy Access Probe Summary

- source: `Local StudioPC probe on 2026-03-31`
- `home_assistant_public`: host `home.prinz-stockenweiler.de` resolved to `91.14.44.20` with HTTPS status `200` and title `Home Assistant`
- `proxmox_public`: host `pve.prinz-stockenweiler.de` unresolved (`getaddrinfo failed`)
- `nextcloud_legacy_public`: host `files.alopri` unresolved (`getaddrinfo failed`)
- `paperless_legacy_public`: host `paperless.alopri` unresolved (`getaddrinfo failed`)
- `vaultwarden_legacy_public`: host `vault.alopri` unresolved (`getaddrinfo failed`)
- `wireguard_legacy_public`: host `vpn.prinz-stockenweiler.de` unresolved (`getaddrinfo failed`)
- `paperless_public_bookmark`: host `papierkram.prinz-stockenweiler.de` resolved to `80.134.168.100` (`Recovered from Edge bookmarks; HTTPS timed out during StudioPC probe on 2026-03-31.`)
- `nextcloud_public_bookmark`: host `cloud.prinz-stockenweiler.de` resolved to `91.14.44.20` (`Recovered from Edge bookmarks; HTTPS currently fails with TLSV1_UNRECOGNIZED_NAME during StudioPC probe on 2026-03-31.`)

## Recovered Browser Bookmarks

- `home_assistant_public` via `chrome`: `Home Assistant` -> `https://home.prinz-stockenweiler.de/dashboard-bereiche`
- `paperless_public` via `edge`: `Startseite - Paperless-ngx` -> `https://papierkram.prinz-stockenweiler.de/dashboard`
- `paperless_documents` via `edge`: `Dokumente - Paperless-ngx` -> `https://papierkram.prinz-stockenweiler.de/documents?correspondent__isnull=1&sort=added&reverse=1&page=1`
- `nextcloud_public` via `edge`: `Dashboard - Nextcloud` -> `https://cloud.prinz-stockenweiler.de/apps/dashboard/`
- `adguard_public` via `edge`: `AdGuard Home` -> `http://adguard.alopri/`

## Recovered Local Access Hints

- `proxmox_host` via `ssh_alias`: `pve -> root@192.168.178.25` using `~/.ssh/id_ed25519`
- `scan_share_or_main_pc_hint` via `windows_recent_shortcut`: `\\192.168.178.120\scans\Familie Prinz` using `SMB share target only; no credentials recovered`

## Legacy Host Key Evidence

- `proxmox_host_ip_continuity`: hosts `192.168.178.172`, `192.168.178.25`, same_host_key=`True`

## Phase 2 Backlog

- management_plane_bridge_candidate: status `deferred_until_lane_a_closed`, preferred path `tailscale_subnet_router_candidate`, fallback `wireguard_recovery_only`
  - not before: Lane A is closed.
  - not before: Stockenweiler is explicitly promoted from watch to active.
  - not before: Main PC and phone are verified.
  - not before: At least one real remote support case has been completed cleanly.
  - must not do: Do not build a Proxmox cluster over WAN.
  - must not do: Do not stretch Layer 2, VLANs or broadcasts between sites.
  - must not do: Do not centralize services just because routed management access exists.
- service_consolidation_candidates:
  - `home_assistant`: phase_2=`management_only`, phase_3=`migrate_later`
  - `radio`: phase_2=`keep_local`, phase_3=`migrate_later`
  - `website_wordpress`: phase_2=`management_only`, phase_3=`migrate_later`
  - `paperless_nextcloud`: phase_2=`management_only`, phase_3=`migrate_later`
  - `smb_scan`: phase_2=`keep_local`, phase_3=`undecided`
- migration_blockers:
  - Lane A remains active and Stockenweiler is still watch-only.
  - Main PC identity is still unresolved.
  - Phone identity is still unresolved.
  - Primary remote path is not yet proven on a live support case.
  - Role of 192.168.178.120 is unresolved between MagentaTV and SMB scan path.
  - FRITZ!Box/Tailscale NAT capability is not yet visibly verified.
  - Upload and latency profile for cross-site operations are not documented.
- rollback_requirements:
  - Any future bridge must be reversible from the StudioPC without same-day physical rework at the site.
  - Keep local Stockenweiler services reachable locally while phase 2 is being tested.
  - Document exact disable/remove steps for any routed bridge before enabling it.
  - Do not decommission any local service before a visible post-check and rollback path exist.

## First Live Onboarding

- collect: `main_pc friendly name`
- collect: `main_pc OS and local login model`
- collect: `main_pc tailscale name or AnyDesk ID`
- collect: `phone model and OS`
- collect: `phone tailscale name`
- collect: `router management contact path`
- collect: `printer/scanner exact model`
- collect: `MagentaTV box model and room context`
- done when: Main PC is identified as a managed support endpoint.
- done when: Phone is identified as a managed support endpoint.
- done when: Primary remote path is Tailscale or the fallback is documented as AnyDesk.
- done when: First support target can be routed without WAN admin exposure.

## First Support Playbooks

- `tv_magenta_triage`: Restore basic TV or receiver usability without changing WAN exposure.
- `father_desktop_remote_help`: Reach the main PC safely and help with the actual user problem.
- `printer_scanner_help`: Unblock printing or scanning with the least invasive path.

# Stockenweiler Inventory Report

Inventory source: `manifests/stockenweiler/site_inventory.json`

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

- `legacy_fact_needs_revalidation`: `6`
- `pending_inventory`: `2`

## Current Blockers

- No first live remote onboarding has happened yet.
- Current on-site main PC identity is still unresolved; operator stated on 2026-03-31 that the former main PC anchor was this StudioPC.
- Phone identity is still unresolved.
- The Stockenweiler Tailscale bridge on stockenweiler-pve is prepared but still pending login approval; StudioPC still sees only 192.168.2.0/24 via toolbox and no visible 192.168.178.0/24 tailnet route yet.
- Scan and media share lineage is unresolved across \\192.168.178.25\music, \\192.168.178.120\music, \\192.168.178.120\scans\Familie Prinz and \\192.168.178.187\ScansDrucker.
- AnyDesk fallback is present locally, but recovered remote IDs are not yet mapped to live Stockenweiler device names.
- Public DNS / DynDNS is only partially coherent: home and cloud resolve via yourparty.tech to 91.14.44.20, Paperless points separately to 80.134.168.100, and pve.prinz-stockenweiler.de has no DNS record.
- Visible legacy host health is degraded: Home Assistant frontend loads but backend is unavailable, Paperless times out, Nextcloud fails TLS/SNI, and pve.prinz-stockenweiler.de does not resolve.
- UCG and broader gateway work stay deferred while the operator 2FA path remains blocked.
- StudioPC already has a local Windows WireGuard route for 192.168.178.0/24 via 10.0.0.2, but direct TCP/22 to 192.168.178.25 still times out; treat that local tunnel as stale until it is re-applied with elevation.
- Stockenweiler PVE storage baseline is now documented: /mnt/data_family on sdb1 (932G) and /mnt/music_hdd on sda2 (1.9T) are both at 100% usage, so any future PBS reuse needs cleanup or reallocation first.
- Local WireGuard Tunnel VPN is still running on StudioPC and cannot be stopped or uninstalled without an elevated admin token.
- Windows hosts file still pins yourparty.tech and www.yourparty.tech to 192.168.178.175; removing those stale lines needs an elevated admin token.

## Issues

- none

## Legacy Conflicts To Revalidate

- `proxmox_host_ip`: best guess `192.168.178.25`, conflicting legacy `192.168.178.172`
- `home_assistant_ip`: best guess `192.168.178.67`, conflicting legacy `192.168.178.68`
- `ip_192.168.178.120_role`: best guess `MagentaTV`, conflicting legacy `\\192.168.178.120\scans\Familie Prinz and \\192.168.178.120\music`
- `music_share_host_ip`: best guess `\\192.168.178.25\music`, conflicting legacy `\\192.168.178.120\music`
- `scanner_share_host_ip`: best guess `\\192.168.178.187\ScansDrucker`, conflicting legacy `\\192.168.178.120\scans\Familie Prinz`

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

## Browser Visible Host Check

- source: `Gemini visible host check on 2026-03-31`
- currently_reachable: `1` / currently_broken: `3`
- observation: Home Assistant is the only legacy host that still presents a frontend at HTTPS level.
- observation: Paperless currently times out on port 443.
- observation: Nextcloud currently fails with ERR_SSL_UNRECOGNIZED_NAME_ALERT, which points to a reverse-proxy or certificate SNI mismatch.
- observation: pve.prinz-stockenweiler.de currently fails DNS resolution.
- `https://home.prinz-stockenweiler.de` -> state `home_assistant`, title `Home Assistant`, login_required `unknown`
  - note: The Home Assistant frontend loads, but it immediately shows 'Unable to connect to Home Assistant. Retrying in ... seconds...', which means the web frontend answers while the backend service appears unavailable.
- `https://papierkram.prinz-stockenweiler.de/dashboard` -> state `timeout`, title `N/A`, login_required `unknown`
  - note: Browser-visible state is ERR_CONNECTION_TIMED_OUT. The host does not currently answer on port 443.
- `https://cloud.prinz-stockenweiler.de/apps/dashboard/` -> state `tls_error`, title `N/A`, login_required `unknown`
  - note: Browser-visible state is ERR_SSL_UNRECOGNIZED_NAME_ALERT, which indicates a missing or wrong certificate/SNI mapping at the reverse proxy.
- `https://pve.prinz-stockenweiler.de` -> state `dns_fail`, title `N/A`, login_required `unknown`
  - note: Browser-visible state is ERR_NAME_NOT_RESOLVED. The hostname does not currently resolve.

## Public Truth Check

- source: `Local public truth check on 2026-03-31`
- dyn_dns_like_count: `2`
- observation: home.prinz-stockenweiler.de resolves via the canonical name yourparty.tech to 91.14.44.20 and returns HTTPS 200.
- observation: cloud.prinz-stockenweiler.de resolves via the canonical name yourparty.tech to 91.14.44.20 but currently fails TLS/SNI.
- observation: papierkram.prinz-stockenweiler.de resolves directly to 80.134.168.100 and currently times out on HTTPS.
- observation: pve.prinz-stockenweiler.de currently has no DNS record.
- `home.prinz-stockenweiler.de` -> canonical `yourparty.tech` / addresses `91.14.44.20` / error `none`
- `pve.prinz-stockenweiler.de` -> canonical `-` / addresses `-` / error `dns_fail`
- `papierkram.prinz-stockenweiler.de` -> canonical `papierkram.prinz-stockenweiler.de` / addresses `80.134.168.100` / error `timeout`
- `cloud.prinz-stockenweiler.de` -> canonical `yourparty.tech` / addresses `91.14.44.20` / error `tls_error`

## Remote Path Probe

- source: `-`
- tailscale_backend_state: `Running`
- tailscale_route_all: `False`
- stockenweiler_subnet_route_present: `False`
- ssh_pve_status: `reachable`
- anydesk_candidate_count: `7`
- observation: Tailscale backend is `Running` on StudioPC.
- observation: StudioPC currently has `RouteAll=false`, so advertised subnet routes are not automatically accepted.
- observation: Visible Tailscale primary routes are currently limited to: 192.168.2.0/24 via toolbox.tail150400.ts.net.
- observation: No Stockenweiler subnet route `192.168.178.0/24` is currently visible in local Tailscale status.
- observation: SSH to `stock-pve` is currently reachable from StudioPC.
- observation: AnyDesk is installed locally and exposes `7` recovered remote-ID candidates, but they are not yet mapped to live Stockenweiler device names.

## Management Bridge

- state: `prepared_pending_login`
- target: `Tailscale subnet-router on stockenweiler-pve for 192.168.178.0/24`
- fallback: `StudioPC -> toolbox -> userspace WireGuard wgstkw -> 192.168.178.25`
- local_direct_wireguard_route_present: `True` / reachable `False`
- route strategy: Do not enable blind RouteAll on StudioPC while it is directly attached to 192.168.2.0/24 and toolbox advertises the same subnet.
- next_operator_action: Open the current login URL from artifacts/stockenweiler_inventory/latest_tailscale_bridge_check.md and authorize stockenweiler-pve into the active tail150400 tailnet.
- next_codex_action: After Tailscale login approval, re-run python scripts/check_stockenweiler_tailscale_bridge.py and then refresh the Stockenweiler reports and AI handoff.

## Recovered Browser Bookmarks

- `home_assistant_public` via `chrome`: `Home Assistant` -> `https://home.prinz-stockenweiler.de/dashboard-bereiche`
- `paperless_public` via `edge`: `Startseite - Paperless-ngx` -> `https://papierkram.prinz-stockenweiler.de/dashboard`
- `paperless_documents` via `edge`: `Dokumente - Paperless-ngx` -> `https://papierkram.prinz-stockenweiler.de/documents?correspondent__isnull=1&sort=added&reverse=1&page=1`
- `nextcloud_public` via `edge`: `Dashboard - Nextcloud` -> `https://cloud.prinz-stockenweiler.de/apps/dashboard/`
- `adguard_public` via `edge`: `AdGuard Home` -> `http://adguard.alopri/`

## Recovered Local Access Hints

- `proxmox_host` via `ssh_alias`: `pve -> root@192.168.178.25` using `~/.ssh/id_ed25519`
- `scan_share_or_main_pc_hint` via `windows_recent_shortcut`: `\\192.168.178.120\scans\Familie Prinz` using `SMB share target only; no credentials recovered`
- `music_share_current_hint` via `mapped_network_drive`: `\\192.168.178.25\music` using `persisted Z: mapping for user wolf`
- `music_share_legacy_hint` via `mountpoints2`: `\\192.168.178.120\music` using `historic Explorer mount only; no current credential recovered`
- `scanner_share_hint` via `windows_credential_manager`: `\\192.168.178.187\ScansDrucker` using `stored domain credential target 192.168.178.187 as user Scanner`
- `stockenweiler_remote_path_truth` via `tailscale_status`: `BackendState=Running; RouteAll=false; visible primary routes currently only 192.168.2.0/24 via toolbox.tail150400.ts.net` using `StudioPC is logged into Tailscale but no 192.168.178.0/24 subnet route is currently visible`
- `anydesk_fallback_candidates` via `anydesk_local_history`: `roster IDs 1580356160 and 1971554928; additional candidate remote IDs 1174136922, 1342642678, 1468499678, 859293713 and 1129124189` using `AnyDesk is installed locally; IDs were recovered from user.conf and connection traces but are not yet mapped to live device names`

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
  - `radio`: phase_2=`management_only`, phase_3=`migrate_to_best_host_later`
  - `website_wordpress`: phase_2=`management_only`, phase_3=`migrate_later`
  - `paperless_nextcloud`: phase_2=`keep_local`, phase_3=`separate_db_later`
  - `smb_scan`: phase_2=`keep_local`, phase_3=`undecided`
  - `pbs_storage`: phase_2=`management_only`, phase_3=`enable_as_pbs_target_later`
- migration_blockers:
  - Lane A remains active and Stockenweiler is still watch-only.
  - Main PC identity is still unresolved.
  - Phone identity is still unresolved.
  - Primary remote path is not yet proven on a live support case.
  - Role of 192.168.178.120 is unresolved between MagentaTV and SMB scan path.
  - FRITZ!Box/Tailscale NAT capability is not yet visibly verified.
  - Upload and latency profile for cross-site operations are not documented.
  - PVE disk inventory and PBS fitness on 192.168.178.25 are not documented.
- rollback_requirements:
  - Any future bridge must be reversible from the StudioPC without same-day physical rework at the site.
  - Keep local Stockenweiler services reachable locally while phase 2 is being tested.
  - Document exact disable/remove steps for any routed bridge before enabling it.
  - Do not decommission any local service before a visible post-check and rollback path exist.

## First Live Onboarding

- collect: `main_pc friendly name`
- collect: `main_pc OS and local login model`
- collect: `main_pc tailscale name or AnyDesk ID`
- collect: `AnyDesk ID to current device-name mapping`
- collect: `phone model and OS`
- collect: `phone tailscale name`
- collect: `router management contact path`
- collect: `printer/scanner exact model`
- collect: `MagentaTV box model and room context`
- collect: `music share host identity`
- collect: `scan share host identity`
- collect: `current local scan folder path used by the parents`
- collect: `PVE local HDD inventory for future PBS use`
- done when: Main PC is identified as a managed support endpoint.
- done when: Phone is identified as a managed support endpoint.
- done when: Primary remote path is Tailscale or the fallback is documented as AnyDesk.
- done when: First support target can be routed without WAN admin exposure.

## First Support Playbooks

- `tv_magenta_triage`: Restore basic TV or receiver usability without changing WAN exposure.
- `father_desktop_remote_help`: Reach the main PC safely and help with the actual user problem.
- `printer_scanner_help`: Unblock printing or scanning with the least invasive path.

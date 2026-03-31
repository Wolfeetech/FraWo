# Stockenweiler Support Brief

- site: `Stockenweiler`
- support label: `Rentner OS`
- canonical external name: `online-prinz.de`
- primary remote access: `tailscale`
- fallback remote access: `anydesk`
- WAN admin exposure allowed: `False`

## First Support Targets

- MagentaTV / TV path
- Father desktop remote help
- Printer / scanner help
- Existing local Home Assistant support

## Current Known Local Facts

- Router: `FRITZ!Box 5690 Pro` @ `192.168.178.1`
- Proxmox: `proxmox Host` @ `192.168.178.25`
- Home Assistant: `homeassistant` @ `192.168.178.67`
- Printer: `Brother - Drucker` @ `192.168.178.153`
- MagentaTV: `MagentaTV` @ `192.168.178.120`

## Current Blockers

- No first live remote onboarding has happened yet.
- Current on-site main PC identity is still unresolved; operator stated on 2026-03-31 that the former main PC anchor was this StudioPC.
- Phone identity is still unresolved.
- Current StudioPC is not on the 192.168.178.0/24 LAN right now; direct SSH to 192.168.178.25 timed out during recovery on 2026-03-31.
- UCG and broader gateway work stay deferred while the operator 2FA path remains blocked.

## Legacy Access Probe

- source: `Local StudioPC probe on 2026-03-31`
- `home_assistant_public`: `home.prinz-stockenweiler.de` -> `91.14.44.20` / HTTPS `200` / `Home Assistant`
- `proxmox_public`: `pve.prinz-stockenweiler.de` unresolved (`getaddrinfo failed`)
- `nextcloud_legacy_public`: `files.alopri` unresolved (`getaddrinfo failed`)
- `paperless_legacy_public`: `paperless.alopri` unresolved (`getaddrinfo failed`)
- `vaultwarden_legacy_public`: `vault.alopri` unresolved (`getaddrinfo failed`)
- `wireguard_legacy_public`: `vpn.prinz-stockenweiler.de` unresolved (`getaddrinfo failed`)
- `paperless_public_bookmark`: `papierkram.prinz-stockenweiler.de` -> `80.134.168.100` (`Recovered from Edge bookmarks; HTTPS timed out during StudioPC probe on 2026-03-31.`)
- `nextcloud_public_bookmark`: `cloud.prinz-stockenweiler.de` -> `91.14.44.20` (`Recovered from Edge bookmarks; HTTPS currently fails with TLSV1_UNRECOGNIZED_NAME during StudioPC probe on 2026-03-31.`)

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

- `proxmox_host_ip_continuity`: `192.168.178.172, 192.168.178.25` / same_host_key `True`

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

## Do Not Do

- do not expose admin paths to the internet
- do not build site-to-site VPN in V1
- do not mix the Stockenweiler LAN into the FraWo production LAN

## Legacy Conflicts To Revalidate

- `proxmox_host_ip`: best guess `192.168.178.25`, conflicting legacy `192.168.178.172`
- `home_assistant_ip`: best guess `192.168.178.67`, conflicting legacy `192.168.178.68`
- `ip_192.168.178.120_role`: best guess `MagentaTV`, conflicting legacy `\\192.168.178.120\scans\Familie Prinz`

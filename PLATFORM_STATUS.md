# Platform Status

## Current State

| Area | Status | Why it is here now | Next move |
| --- | --- | --- | --- |
| Core LAN frontdoor | green | AdGuard, Caddy, portal and internal domains are live | keep stable and document UCG cutover |
| Nextcloud | green | app works, login works, internal domain works, named users exist | move final values into Vaultwarden and standardize system mail |
| Paperless | green | app works, bridge works, login works, named users exist | move final values into Vaultwarden and refine filing model |
| Odoo | green | app works, login works, DB name clarified, named users exist | move final values into Vaultwarden and keep Studio out of the critical path |
| Home Assistant | green | internal path works | keep stable |
| Jellyfin | green | service is live, named users exist, and the active library is now the canonical SMB path | add first TV clients and optional PINs |
| AzuraCast / Radio integration | yellow | internal proxy path answers, but the live audit still reports `rpi_radio_integrated=no` and media/layout readiness is not green | repair Pi integration and keep it out of the current MVP |
| Shared media storage | yellow | `CT110` is live, SMB is canonical, Jellyfin is SMB-only, and the old local bootstrap copy is gone | keep stable and decide whether the 2-TB SSD should become the next storage tier |
| Backups | yellow | local Proxmox backups are real and current, but `PBS` is not green and no restore-proof path is currently active there | keep local backups stable and rebuild `PBS` as a separate certification track |
| Surface Go frontend | red | the live audit sees `SSH`, `HTTP`, and `HTTPS` closed on `192.168.2.154` | treat it as offline, then clean-rebuild and reaccept it later |
| UCG Ultra | yellow | hardware is attached in test mode only | inventory, isolate, then controlled cutover |
| Public edge | red | intentionally not exposed yet; `2026-04-01` is website-first only | hold the line until DNS, TLS, auth, monitoring and rollback are ready |
| Identity and mail model | yellow | `Franz` is in `FraWo`, Vaultwarden invite flow works, and `webmaster`/`franz` auth are technically verified, but visible send/receive and final `STRATO` verification are still open | finish visible send/receive for `webmaster`, `franz`, `noreply` and close the remaining app mail tests |
| Secrets | yellow | Vaultwarden is live, Franz is in `FraWo`, but the visible spot-check and markdown cleanup are still open | verify the imported set visibly and then reduce markdown secrets to references |
| Business MVP readiness | green | `release-mvp-gate` = `MVP_READY` (2026-04-09); alle manuellen Nachweise passed; Lane A geschlossen | Lane B (Website/Public) ist der aktive Nachfolgetrack |
| Full internal certification | red | `production-gate` ist korrekt `BLOCKED` durch `PBS`, `surface-go`, `Radio/AzuraCast` und fehlende manuelle Evidenz | getrennt vom Website-Release weiter verfolgen |
| Stockenweiler / Rentner OS | yellow | SSL-Zertifikat `home.prinz-stockenweiler.de` seit April 2026 abgelaufen; Inventar klar, aber kein operativer Remote-Support-Onboarding | SSL sofort erneuern (NPM LXC 103), dann Tailscale-only Support-Pfad |
| Website release readiness | yellow | HTTP auf `www.frawo-tech.de` gruen; DS-Lite blockiert IPv4-Portforward fuer HTTPS | Cloudflare-Proxy oder Dual-Stack-ISP-Upgrade fuer TLS |

## Why Work Felt Slow

- Media moved from an old USB/legacy path to a new SMB canonical path while services had to stay online.
- Identity, credentials, and final ownership standards were not defined early enough.
- `local-lvm` ran into a real thinpool saturation incident and caused follow-on storage errors on `CT110`.
- There was no real secret-management home yet; the old plaintext access register became an interim crutch instead of a final operating standard.

## Canonical Paths

- Music library: `\\192.168.2.30\Media\yourparty_Libary`
- Linux view of the same library: `//192.168.2.30/Media`
- Documents share: `\\192.168.2.30\Documents`

## Immediate Priorities

1. **Cloudflare oder ISP-Upgrade** für HTTPS auf `www.frawo-tech.de`: EasyBox 805 DS-Lite blockiert IPv4-Portforwards → Cloudflare-Proxy oder Dual-Stack-Tarif.
2. **Stockenweiler SSL erneuern** für `home.prinz-stockenweiler.de` (abgelaufen seit April 2026) via NPM LXC 103 oder Certbot CLI.
3. **PBS monatlicher Restore-Drill** via `make pbs-restore-proof` (VM 240 gestoppt, muss wieder aktiviert werden).
4. **yourparty-Payload sichern** bevor Stockenweiler ausgedünnt wird: AzuraCast Station Config, WordPress-Content, MariaDB-Data, Radio-API-Config.
5. **AzuraCast Pi-Integration** schließen (`rpi_radio_integrated=no`) und Jellyfin `TV Wohnzimmer`-Passwort hinterlegen.

## Current Operator Note

- On March 25, 2026, `wolfstudiopc` had a live routing conflict: Tailscale was accepting the subnet route `192.168.2.0/24` from `toolbox`, which overrode the directly attached LAN for this workstation.
- The workstation-side fix is applied: `tailscale set --accept-routes=false`.
- Result: the local route to `192.168.2.0/24` is preferred again on this PC and the current live admin path to Proxmox, Toolbox, Storage and the Radio Pi is working again.

## Incident Note 2026-03-25

- The apparent VM failure was a Proxmox thin-pool saturation incident on `local-lvm`.
- Root cause:
  - stale Codex-created rollback snapshots on `VM 200`, `VM 220`, and `CT 100`
  - `VM 320 odoo-restore-test` still present with `onboot=1`
  - `VM 320` also carried the same `192.168.2.22` cloud-init address as productive `VM 220 odoo`
- Resolution:
  - removed stale rollback snapshots
  - destroyed `VM 320 odoo-restore-test`
  - restarted affected guests `210`, `220`, `230`, `240`
  - trimmed reclaimable space inside active guests and containers
  - moved `VM 240 pbs` system disk from `local-lvm` to `pbs-usb`
  - enabled VM image support on `local` and moved `VM 220`, `VM 230`, `VM 200`, and `VM 210` system disks from `local-lvm` to `local` as `qcow2`
  - reran `e2fsck` on `CT110` after headroom returned, which removed the ext4 emergency read-only state
  - migrated `CT 100 toolbox` rootfs from `local-lvm` to `local`
  - removed the obsolete local Jellyfin bootstrap library `bootstrap-radio-usb` from `CT 100`
  - switched Jellyfin to the active SMB-backed library `Musik Netzwerk`
- Result:
  - all production VMs respond again on `192.168.2.21` to `192.168.2.25`
  - `pbs-interim` is active again
  - the canonical media share on `CT110` is writable again and the USB library is fully mirrored into SMB
  - `HAOS` recovered from `io-error`, its UI answers again on `192.168.2.24:8123` and `ha.hs27.internal`
  - `local-lvm` dropped from `100%` to about `40.4%`, so the acute thinpool failure is gone
  - `local` (`/var/lib/vz`) was temporarily pushed high by the `CT100` move, then relieved again by moving old local dump archives onto the 2-TB NTFS SSD
  - current host root usage is back around `78%` and `local` is around `73%`

## Incident Note 2026-03-26

- Symptom:
  - Jellyfin loaded in the browser, but selecting a preconfigured user produced a connection error.
- Root cause:
  - `CT 100 toolbox` rootfs was mounted as `ext4 (rw,relatime,emergency_ro)`.
  - That left the Jellyfin host partially functional but unstable for auth and write-dependent flows.
- Resolution:
  - stopped `CT 100`
  - ran `e2fsck -f -y /var/lib/vz/images/100/vm-100-disk-0.raw`
  - restarted `CT 100`
  - verified `/` inside the container is back to plain `rw`
  - verified `portal.hs27.internal` and `media.hs27.internal` answer again
  - verified `POST /Users/AuthenticateByName` for Jellyfin user `Wolf` returns `HTTP 200`
- Result:
  - toolbox rootfs is writable again
  - Jellyfin auth is server-side healthy again
  - the previous browser-side Jellyfin connection error is no longer attributable to a dead auth backend

## Incident Note 2026-03-26B

- Symptom:
  - `VM 200 nextcloud` showed a warning in the Proxmox UI and reported `status: io-error`.
- Root cause:
  - The earlier host storage pressure on `local` left `VM 200` in a stuck QEMU I/O error state even after host headroom had already been restored.
- Resolution:
  - verified host headroom on `local` and `local-lvm`
  - stopped and started `VM 200` from Proxmox
  - verified Proxmox status returned to `running`
  - verified Nextcloud answered again on `http://192.168.2.21`
- Result:
  - `VM 200 nextcloud` is back in normal `running` state
  - the acute Proxmox warning is no longer backed by a live guest outage
  - Nextcloud HTTP is healthy again

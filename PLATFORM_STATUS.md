# Platform Status

## Current State

| Area | Status | Why it is here now | Next move |
| --- | --- | --- | --- |
| Core LAN frontdoor | green | AdGuard, Caddy, portal and internal domains are live | keep stable and document UCG cutover |
| Nextcloud | green | app works, login works, internal domain works, named users exist | move final values into Bitwarden and standardize system mail |
| Paperless | green | app works, bridge works, login works, named users exist | move final values into Bitwarden and refine filing model |
| Odoo | green | app works, login works, DB name clarified, named users exist | move final values into Bitwarden and keep Studio out of the critical path |
| Home Assistant | green | internal path works | keep stable |
| Jellyfin | green | service is live, named users exist, and the active library is now the canonical SMB path | add first TV clients and optional PINs |
| AzuraCast | green | service is live, station `frawo-funk` is online, SMB is complete, and a personal admin exists | keep playlists and station settings clean |
| Shared media storage | yellow | `CT110` is live, SMB is canonical, Jellyfin is SMB-only, and the old local bootstrap copy is gone | keep stable and decide whether the 2-TB SSD should become the next storage tier |
| Backups | yellow | interim PBS works, proof exists, but long-term storage is not final | enlarge storage strategy, continue restore drills, and keep offsite options secondary for now |
| Surface Go frontend | yellow | kiosk baseline exists, but hardware/boot is blocking the live rollout | recover hardware first, then continue the `frontend` path |
| UCG Ultra | yellow | hardware is attached in test mode only | inventory, isolate, then controlled cutover |
| Public edge | red | intentionally not exposed yet; `2026-04-01` is website-first only | hold the line until DNS, TLS, auth, monitoring and rollback are ready |
| Identity and mail model | yellow | app identities are largely standardized, but the real FRAWO mailboxes do not exist yet | create STRATO mailboxes and then swap remaining temporary identities cleanly |
| Secrets | red | there is still no real password manager in production | introduce Bitwarden Cloud and migrate production logins out of markdown files |
| Stockenweiler / Rentner OS | yellow | target model is now clear, but no operational remote-support onboarding exists yet | build the Tailscale-only support path and inventory the first managed devices |
| 2-TB SSD | yellow | real extra space exists and is now used as interim cold archive relief, but not yet server-optimized | keep NTFS intact, then later shrink it from Windows and add a Linux partition |
| Stress test readiness | yellow | core services are stable enough for a controlled internal stress test, but not for broad public rollout | run internal load and workflow tests before public release |

## Why Work Felt Slow

- Media moved from an old USB/legacy path to a new SMB canonical path while services had to stay online.
- Identity, credentials, and final ownership standards were not defined early enough.
- `local-lvm` ran into a real thinpool saturation incident and caused follow-on storage errors on `CT110`.
- There was no real secret-management home yet; `ACCESS_REGISTER.md` became an interim register instead of a final operating standard.

## Canonical Paths

- Music library: `\\192.168.2.30\Media\yourparty_Libary`
- Linux view of the same library: `//192.168.2.30/Media`
- Documents share: `\\192.168.2.30\Documents`

## Immediate Priorities

1. Introduce Bitwarden Cloud and migrate current production logins out of markdown files.
2. Create the STRATO mailboxes and document SPF, DKIM and DMARC.
3. Hold the public release scope to `www.frawo-tech.de` only.
4. Stabilize `local` storage headroom now that `CT100` moved off `local-lvm` and old local dump archives were moved to the 2-TB SSD.
5. Decide the final 2-TB SSD role and only then repartition it safely.
6. Start the first Stockenweiler support path as a Tailscale-only managed service.

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

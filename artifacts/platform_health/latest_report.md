# Platform Health Audit

- Generated at: `2026-04-04T00:06:27+02:00`
- Anker management path: `root@100.69.179.87`
- Stockenweiler management path: `stock-pve`

## Summary

- Top priority issue: Stockenweiler host is under real memory pressure: swap used `6.3 GiB` / `8.0 GiB`.
- Frontdoors green: `8` / `8`
- Odoo runtime green: `true`
- Blockers: `5` / optimization candidates: `5` / strategic recommendations: `5`

## Anker Host

- Host: `proxmox-anker` / `pve-manager/9.1.6/71482d1833ded40a`
- Memory used: `10.01 GiB` / `15.46 GiB` (`64.8%`) 
- Rootfs used: `46.74 GiB` / `67.61 GiB` (`69.1%`) 
- Swap used: `0.0 GiB` / `8.0 GiB` (`0.0%`) 
- Storages:
  - `local` `dir` active=`true` used=`69.1%`
  - `local-lvm` `lvmthin` active=`true` used=`61.2%`
  - `stockenweiler-data` `nfs` active=`true` used=`25.7%`
  - `pbs-interim` `pbs` active=`false` used=`0.0%`
  - `pbs-usb` `dir` active=`false` used=`0.0%`

## Stockenweiler Host

- Host: `pve` / `pve-manager/9.1.4/5ac30304265fbd8e`
- Memory used: `11.1 GiB` / `15.5 GiB` (`71.6%`) 
- Rootfs used: `17.43 GiB` / `67.73 GiB` (`25.7%`) 
- Swap used: `6.3 GiB` / `8.0 GiB` (`78.8%`) 
- Storages:
  - `hdd-backup` `dir` active=`true` used=`84.0%`
  - `local-lvm` `lvmthin` active=`true` used=`64.6%`
  - `local` `dir` active=`true` used=`25.7%`
  - `anker-music` `nfs` active=`false` used=`0.0%`

## Runtime Notes

- Odoo direct HTTP: `200` / frontdoor HTTP: `200`
- Odoo assessment: `runtime_green_but_production_profile_pending`
- AzuraCast role: `frawo_hobby_media_engine`
- Listener binding recommendation: Use Odoo for CRM, website, portal, newsletters, sponsors, and supporter flows; keep AzuraCast as streaming/schedule/metadata engine.

## Stockenweiler Legacy yourparty Payload

- VM 210 azuracast-vm
- CT 207 radio-wordpress-prod
- CT 208 mariadb-server
- CT 211 radio-api

## Blockers

- Stockenweiler host is under real memory pressure: swap used `6.3 GiB` / `8.0 GiB`.
- Stockenweiler storage `hdd-backup` is at `84.0%` and should not receive new backup or migration load yet.
- Anker PBS path `pbs-interim` is not active; backup consolidation is still not green.
- Anker PBS path `pbs-usb` is not active; backup consolidation is still not green.
- VM 240 PBS is still stopped, so there is no current green dedicated PBS runtime on Anker.

## Optimization Candidates

- Anker guest `toolbox` (`100`) runs at only `14.1%` RAM use and is a later rightsizing candidate.
- Anker guest `storage-node` (`110`) runs at only `2.6%` RAM use and is a later rightsizing candidate.
- Anker guest `vaultwarden` (`120`) runs at only `9.0%` RAM use and is a later rightsizing candidate.
- Stockenweiler guest `azuracast-vm` (`210`) is at `89.7%` RAM use and should be reviewed before adding workloads.
- Stockenweiler guest `homeassistant-eltern` (`360`) is at `88.0%` RAM use and should be reviewed before adding workloads.

## Strategic Recommendations

- Stockenweiler still carries a fragmented legacy yourparty stack across VM 210 azuracast-vm, CT 207 radio-wordpress-prod, CT 208 mariadb-server, and CT 211 radio-api.
- Odoo is runtime-green, but production-ready should mean a defined module/profile rollout, customer portal scope, backup/restore path, and mail/identity workflow, not only HTTP 200.
- Best-fit product model is Odoo as CRM/portal/business shell around radio, while AzuraCast remains the media engine rather than the master identity system for listeners.
- Home Assistant should stay separated per household first; later integration should expose selected entities only, not merge both households into one HA runtime.
- Before thinning Stockenweiler, capture the essential yourparty payload into Rothkreuz: AzuraCast station config, WordPress content, MariaDB data, and radio API/config.

## Recommended Next Order

- Keep Anker stable; do not start broad migrations while PBS and Stockenweiler pressure remain open.
- Define the Odoo production profile and customer portal scope before calling it production-ready.
- Capture the essential yourparty payload from Stockenweiler into Rothkreuz before deleting or thinning radio/web components.
- Only after payload capture: retire duplicated Stockenweiler radio/web/api roles stepwise.
- Keep Home Assistant separated per household; integrate selected entities later via the management bridge.

# Platform Health Audit

- Generated at: `2026-05-04T09:18:47+02:00`
- Anker management path: `pve-anker`
- Stockenweiler management path: `pve-stock`

## Summary

- Top priority issue: none
- Frontdoors green: `4` / `8`
- Odoo runtime green: `true`
- Blockers: `0` / optimization candidates: `5` / strategic recommendations: `4`

## Anker Host

- Host: `proxmox-anker` / `pve-manager/9.1.9/ee7bad0a3d1546c9`
- Memory used: `9.1 GiB` / `15.46 GiB` (`58.9%`) 
- Rootfs used: `28.46 GiB` / `67.61 GiB` (`42.1%`) 
- Swap used: `0.0 GiB` / `8.0 GiB` (`0.0%`) 
- Storages:
  - `local-lvm` `lvmthin` active=`true` used=`89.4%`
  - `local` `dir` active=`true` used=`42.1%`
  - `pbs-usb` `dir` active=`true` used=`42.1%`
  - `stockenweiler-data` `nfs` active=`true` used=`31.7%`
  - `google-drive` `dir` active=`true` used=`28.0%`

## Stockenweiler Host

- Host: `pve` / `pve-manager/9.1.4/5ac30304265fbd8e`
- Memory used: `8.43 GiB` / `15.5 GiB` (`54.4%`) 
- Rootfs used: `21.49 GiB` / `67.73 GiB` (`31.7%`) 
- Swap used: `3.77 GiB` / `8.0 GiB` (`47.1%`) 
- Storages:
  - `hdd-backup` `dir` active=`true` used=`76.0%`
  - `local-lvm` `lvmthin` active=`true` used=`57.7%`
  - `local` `dir` active=`true` used=`31.7%`
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


## Optimization Candidates

- Anker guest `toolbox` (`100`) runs at only `16.2%` RAM use and is a later rightsizing candidate.
- Anker guest `PBS-FraWo` (`240`) runs at only `1.5%` RAM use and is a later rightsizing candidate.
- Anker guest `storage-node` (`110`) runs at only `3.7%` RAM use and is a later rightsizing candidate.
- Stockenweiler guest `homeassistant-eltern` (`360`) is at `93.8%` RAM use and should be reviewed before adding workloads.
- Stockenweiler guest `azuracast-vm` (`210`) is at `85.8%` RAM use and should be reviewed before adding workloads.

## Strategic Recommendations

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

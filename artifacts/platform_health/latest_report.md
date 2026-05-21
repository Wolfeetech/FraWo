# Platform Health Audit

- Generated at: `2026-05-20T22:19:10+02:00`
- Anker management path: `pve-anker`
- Stockenweiler management path: `pve-stock`

## Summary

- Top priority issue: none
- Frontdoors green: `7` / `8`
- Odoo runtime green: `true`
- Blockers: `0` / optimization candidates: `3` / strategic recommendations: `4`

## Anker Host

- Host: `proxmox-anker` / `pve-manager/9.1.9/ee7bad0a3d1546c9`
- Memory used: `12.27 GiB` / `15.46 GiB` (`79.4%`) 
- Rootfs used: `32.62 GiB` / `67.61 GiB` (`48.2%`) 
- Swap used: `2.39 GiB` / `8.0 GiB` (`29.9%`) 
- Storages:
  - `local-lvm` `lvmthin` active=`true` used=`89.8%`
  - `pbs-usb` `dir` active=`true` used=`48.2%`
  - `local` `dir` active=`true` used=`48.2%`
  - `google-drive` `dir` active=`true` used=`34.1%`
  - `ssd2tb` `dir` active=`true` used=`4.8%`

## Stockenweiler Host

- Host: `pve` / `unknown`
- Memory used: `0.0 GiB` / `0.0 GiB` (`0.0%`) 
- Rootfs used: `0.0 GiB` / `0.0 GiB` (`0.0%`) 
- Swap used: `0.0 GiB` / `0.0 GiB` (`0.0%`) 
- Storages:

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

- Anker guest `PBS-FraWo` (`240`) runs at only `1.0%` RAM use and is a later rightsizing candidate.
- Anker guest `storage-node` (`110`) runs at only `2.1%` RAM use and is a later rightsizing candidate.
- Anker guest `vaultwarden` (`120`) runs at only `6.1%` RAM use and is a later rightsizing candidate.

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

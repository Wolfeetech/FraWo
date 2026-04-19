# Platform Health Audit

- Generated at: `2026-04-18T11:25:05+02:00`
- Anker management path: `root@100.69.179.87`
- Stockenweiler management path: `stock-pve`

## Summary

- Top priority issue: Stockenweiler host is under real memory pressure: swap used `5.64 GiB` / `8.0 GiB`.
- Frontdoors green: `0` / `8`
- Odoo runtime green: `false`
- Blockers: `4` / optimization candidates: `3` / strategic recommendations: `4`

## Anker Host

- Host: `proxmox-anker` / `pve-manager/9.1.6/71482d1833ded40a`
- Memory used: `11.82 GiB` / `15.46 GiB` (`76.4%`) 
- Rootfs used: `20.28 GiB` / `67.61 GiB` (`30.0%`) 
- Swap used: `5.01 GiB` / `8.0 GiB` (`62.6%`) 
- Storages:
  - `local-lvm` `lvmthin` active=`true` used=`71.4%`
  - `stockenweiler-data` `nfs` active=`true` used=`30.4%`
  - `local` `dir` active=`true` used=`30.0%`
  - `google-drive` `dir` active=`true` used=`20.9%`

## Stockenweiler Host

- Host: `pve` / `pve-manager/9.1.4/5ac30304265fbd8e`
- Memory used: `9.64 GiB` / `15.5 GiB` (`62.2%`) 
- Rootfs used: `20.59 GiB` / `67.73 GiB` (`30.4%`) 
- Swap used: `5.64 GiB` / `8.0 GiB` (`70.6%`) 
- Storages:
  - `hdd-backup` `dir` active=`true` used=`85.6%`
  - `local-lvm` `lvmthin` active=`true` used=`64.8%`
  - `local` `dir` active=`true` used=`30.4%`
  - `anker-music` `nfs` active=`false` used=`0.0%`

## Runtime Notes

- Odoo direct HTTP: `200` / frontdoor HTTP: `000`
- Odoo assessment: `runtime_green_but_production_profile_pending`
- AzuraCast role: `frawo_hobby_media_engine`
- Listener binding recommendation: Use Odoo for CRM, website, portal, newsletters, sponsors, and supporter flows; keep AzuraCast as streaming/schedule/metadata engine.

## Stockenweiler Legacy yourparty Payload

- VM 210 azuracast-vm
- CT 207 radio-wordpress-prod
- CT 208 mariadb-server
- CT 211 radio-api

## Blockers

- Stockenweiler host is under real memory pressure: swap used `5.64 GiB` / `8.0 GiB`.
- Stockenweiler storage `hdd-backup` is at `85.6%` and should not receive new backup or migration load yet.
- VM 240 PBS is still stopped, so there is no current green dedicated PBS runtime on Anker.
- Odoo frontdoor is not green from StudioPC: HTTP `000`.

## Optimization Candidates

- Anker guest `toolbox` (`100`) runs at only `3.9%` RAM use and is a later rightsizing candidate.
- Anker guest `storage-node` (`110`) runs at only `3.1%` RAM use and is a later rightsizing candidate.
- Anker guest `vaultwarden` (`120`) runs at only `5.9%` RAM use and is a later rightsizing candidate.

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

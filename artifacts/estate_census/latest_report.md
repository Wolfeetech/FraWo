# Estate Census

- generated_at: `2026-04-09 17:23:24`
- tailscale_backend_state: `Running`
- local_ipv4_interfaces: `5`
- local_active_dns_sets: `2`
- online_tailscale_peers: `5`
- offline_tailscale_peers: `6`
- routed_tailscale_peers: `2`
- anker_running_containers: `3`
- anker_running_vms: `4`
- stock_running_containers: `6`
- stock_running_vms: `1`
- frontdoors_ok: `5` / `8`
- stock_public_ok: `0` / `4`

## Usable Now

- management: `ssh root@100.69.179.87 (proxmox-anker)`
- management: `ssh root@100.91.20.116 (stockenweiler-pve)`
- management: `Tailscale peer toolbox.tail150400.ts.net / 100.99.206.128`
- service: `http://100.99.206.128:8444/web/login`
- service: `http://100.99.206.128:8445/`
- service: `http://100.99.206.128:8446/accounts/login/`
- service: `http://100.99.206.128:8447/`
- service: `http://100.99.206.128:8449/`

## Local Control Plane

- iface `vEthernet (WSL (Hyper-V firewall))` -> `172.24.176.1/20`
- iface `Tailscale` -> `100.98.31.60/32`
- iface `WLAN` -> `192.168.2.161/24`
- iface `wg-studiopc` -> `10.0.0.2/32`
- iface `Ethernet` -> `10.1.0.254/24`
- dns `Ethernet` -> `10.1.0.1`
- dns `WLAN` -> `192.168.2.1`

## Tailscale Peers

- `desktop-7lmp02s.tail150400.ts.net` -> online `true` / ip `100.79.103.59, fd7a:115c:a1e0::b3a:673b`
- `iphone-15.tail150400.ts.net` -> online `false` / ip `100.106.111.38, fd7a:115c:a1e0::243a:6f26`
- `pixel-8a.tail150400.ts.net` -> online `false` / ip `100.102.51.64, fd7a:115c:a1e0::3d3a:3340`
- `pixel-9-pro.tail150400.ts.net` -> online `true` / ip `100.83.213.17, fd7a:115c:a1e0::683a:d511`
- `proxmox-anker.tail150400.ts.net` -> online `true` / ip `100.69.179.87, fd7a:115c:a1e0::c63a:b357` / routes `10.1.0.0/24`
- `radio-node.tail150400.ts.net` -> online `false` / ip `100.64.23.77, fd7a:115c:a1e0::243a:174d`
- `stockenweiler-pve.tail150400.ts.net` -> online `true` / ip `100.91.20.116, fd7a:115c:a1e0::ed3a:1474` / routes `192.168.178.0/24`
- `surface-go-frontend.tail150400.ts.net` -> online `false` / ip `100.106.67.127, fd7a:115c:a1e0::113a:437f`
- `toolbox.tail150400.ts.net` -> online `true` / ip `100.99.206.128, fd7a:115c:a1e0::af01:cea1`
- `wohnzimmertv.tail150400.ts.net` -> online `false` / ip `100.84.241.124, fd7a:115c:a1e0::da3a:f17c`
- `wolf-zenbook-ux325ea-ux325ea.tail150400.ts.net` -> online `false` / ip `100.76.249.126, fd7a:115c:a1e0::d03a:f97e`

## Frontdoors

- `vaultwarden` -> `000` (`down`) via `http://100.99.206.128:8442/alive`
- `home_assistant` -> `400` (`degraded`) via `http://100.99.206.128:8443/`
- `odoo` -> `200` (`ok`) via `http://100.99.206.128:8444/web/login`
- `nextcloud` -> `302` (`ok`) via `http://100.99.206.128:8445/`
- `paperless` -> `200` (`ok`) via `http://100.99.206.128:8446/accounts/login/`
- `portal` -> `200` (`ok`) via `http://100.99.206.128:8447/`
- `radio` -> `502` (`degraded`) via `http://100.99.206.128:8448/`
- `media` -> `302` (`ok`) via `http://100.99.206.128:8449/`

## Proxmox Anker

- host: `proxmox-anker` / `pve-manager/9.1.6/71482d1833ded40a (running kernel: 6.17.13-2-pve)`
- vmbr0_ipv4: `10.1.0.92/24, 192.168.2.10/24, 192.168.2.1/24`
- transition_router: active `active` / enabled `enabled`
- running_containers: `toolbox, storage-node, vaultwarden`
- running_vms: `nextcloud, haos, odoo, paperless`
- stopped_vms: `pbs`
- internal_http_nextcloud: `302`
- internal_http_odoo: `200`
- internal_http_paperless: `000`
- internal_http_haos: `200`
- internal_http_vaultwarden: `200`

## Stockenweiler

- host: `pve` / `pve-manager/9.1.4/5ac30304265fbd8e (running kernel: 6.17.2-2-pve)`
- vmbr0_ipv4: `192.168.178.25/24`
- tailscale_ipv4: `100.91.20.116/32`
- running_containers: `adguard, npm, wireguard, vaultwarden, pbs, fileserver`
- running_vms: `homeassistant-eltern`
- storage `anker-music`: `inactive` (nfs) / used `0.00%`
- storage `hdd-backup`: `active` (dir) / used `89.11%`
- storage `local`: `active` (dir) / used `25.74%`
- storage `local-lvm`: `active` (lvmthin) / used `64.71%`

## Blockers

- Home Assistant mobile/frontdoor is still degraded and returns HTTP 400 through toolbox.
- StudioPC direct access to legacy guest 192.168.2.x is not the working path during the UCG transition because the same subnet exists on two different L2 domains.
- Stockenweiler has inactive storage targets: anker-music.
- Stockenweiler public legacy endpoints are still broken: https://home.prinz-stockenweiler.de, https://papierkram.prinz-stockenweiler.de/dashboard, https://cloud.prinz-stockenweiler.de/apps/dashboard/, https://pve.prinz-stockenweiler.de.
- Some expected Tailscale peers are offline: iphone-15.tail150400.ts.net, pixel-8a.tail150400.ts.net, radio-node.tail150400.ts.net, surface-go-frontend.tail150400.ts.net, wohnzimmertv.tail150400.ts.net, wolf-zenbook-ux325ea-ux325ea.tail150400.ts.net.

## Recommended Next Order

- Treat Tailscale as the only professional operator path; stop depending on direct StudioPC-to-legacy 192.168.2.x reachability during migration.
- Freeze the current working transition state: Proxmox on 10.1.0.92, toolbox frontdoors 8/8 green, guests still isolated behind the transition router.
- Use the existing published UCG VLAN schema as the target network model; do not reopen subnet design unless the SSOT itself changes.
- Use a low-risk pilot service after the subnet decision, then migrate business services one by one behind the stable frontdoor names.
- Normalize Stockenweiler access and storage facts before any site-marriage or shared-storage work.

## Canonical Transition Sequence

- Freeze the current working control plane and keep Tailscale/frontdoor access as the canonical operator path.
- Use `UCG_NETWORK_ARCHITECTURE.md` as the binding target VLAN/subnet model and focus only on service-to-VLAN adoption plus runtime cutover order.
- Keep DNS and browser entrypoints target-agnostic; users should prefer toolbox frontdoors and hs27.internal names instead of direct guest IPs.
- Run one low-risk pilot move first, preferably a non-business-critical endpoint such as portal, media, or radio pathing.
- After the pilot is green, migrate the core business services in order: Odoo, Nextcloud, Paperless.
- Move Home Assistant only after the business trio is stable on the new model.
- Revisit Vaultwarden only with explicit rollback and maintenance discipline because it is security-critical.
- Handle PBS and any storage redesign last, after networking and service naming are stable.

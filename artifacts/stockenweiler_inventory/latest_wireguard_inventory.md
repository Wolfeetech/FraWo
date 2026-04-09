# Stockenweiler WireGuard Inventory

- generated_at: `2026-04-03 22:03:02`
- target: `100.91.20.116`
- reachable: `true`
- host: `pve` / `pve-manager/9.1.4/5ac30304265fbd8e (running kernel: 6.17.2-2-pve)`
- ct106_status: `status: running`
- ct106_net0: `name=eth0,bridge=vmbr0,gw=192.168.178.1,hwaddr=BC:24:11:EF:FF:1A,ip=192.168.178.186/24,type=veth`
- server_address: `10.0.0.1/24`
- listen_port: `51820`
- configured_peers: `5`
- peers_with_runtime_handshake_info: `3`

## Known Client Profiles

- `google-pixel` -> address `10.0.0.3/32`, endpoint `192.168.178.186:51820`, allowed `10.0.0.0/24, 192.168.178.0/24`
- `studio-pc` -> address `10.0.0.2/32`, endpoint `vpn.prinz-stockenweiler.de:51820`, allowed `10.0.0.0/24, 192.168.178.0/24`
- `surface` -> address `10.0.0.5/32`, endpoint `vpn.prinz-stockenweiler.de:51820`, allowed `10.0.0.0/24, 192.168.178.0/24`
- `zenbook` -> address `10.0.0.4/32`, endpoint `vpn.prinz-stockenweiler.de:51820`, allowed `10.0.0.0/24, 192.168.178.0/24`

## Runtime Peer Snapshot

- allowed `10.0.0.2/32` / endpoint `192.168.178.25:30404` / latest_handshake `1 hour, 51 minutes, 29 seconds ago` / transfer `124.28 MiB received, 844.21 MiB sent`
- allowed `10.0.0.3/32` / endpoint `80.187.82.168:18442` / latest_handshake `83 days, 1 hour, 49 minutes, 48 seconds ago` / transfer `1.56 KiB received, 157.71 MiB sent`
- allowed `10.0.0.4/32` / endpoint `80.187.82.168:4674` / latest_handshake `83 days, 1 hour, 50 minutes, 48 seconds ago` / transfer `1.43 MiB received, 167.94 MiB sent`
- allowed `10.0.0.5/32` / endpoint `-` / latest_handshake `-` / transfer `-`
- allowed `10.0.0.6/32` / endpoint `-` / latest_handshake `-` / transfer `-`

## Conclusions

- CT 106 is a running dedicated WireGuard server in Stockenweiler.
- The server currently listens on port 51820 and serves the VPN subnet 10.0.0.1/24.
- This confirms that Stockenweiler already hosts an existing WireGuard server topology; the local StudioPC WireGuard profile is only one client path into that topology.
- For a future professional site bridge, Variant A (UCG as client to the existing Stockenweiler WireGuard server) is the lower-friction starting candidate because clients and subnet expectations already exist.
- Variant B (UCG as new WireGuard server and Stockenweiler as client) remains possible, but it would be a conscious migration/rebuild, not a continuation of the current topology.

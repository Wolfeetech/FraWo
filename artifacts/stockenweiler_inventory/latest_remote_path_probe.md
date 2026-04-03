# Stockenweiler Remote Path Probe

- generated_at: `2026-04-03 18:47:10`

## Summary

- Tailscale backend is `Running` on StudioPC.
- Visible Tailscale primary routes are currently limited to: 192.168.2.0/24 via toolbox.tail150400.ts.net.
- No Stockenweiler subnet route `192.168.178.0/24` is currently visible in local Tailscale status.
- SSH to `stock-pve` is currently reachable from StudioPC.
- AnyDesk is installed locally and exposes `9` recovered remote-ID candidates, but they are not yet mapped to live Stockenweiler device names.

## Tailscale

- backend_state: `Running`
- self_dns_name: `wolfstudiopc.tail150400.ts.net.`
- self_ips: `100.98.31.60`, `fd7a:115c:a1e0::7b3a:1f3c`
- route_all: `True`
- corp_dns: `True`
- stockenweiler_subnet_route_present: `False`

### Health

- Tailscale can't reach the configured DNS servers. Internet connectivity may be affected.

### Visible Primary Routes

- 192.168.2.0/24 via toolbox.tail150400.ts.net

## SSH Probe

- target: `stock-pve`
- status: `reachable`
- stdout: `stockenweiler_remote_probe_ok`
- stderr: `Warning: Permanently added '100.91.20.116' (ED25519) to the list of known hosts.`

## AnyDesk

- installed: `True`
- roster_ids: `1580356160`, `1971554928`
- permission_profile_ids: `1129124189`, `1174136922`, `1342642678`, `859293713`
- history_ids: `1342642678`, `1374777405`, `1468499678`, `1935329794`

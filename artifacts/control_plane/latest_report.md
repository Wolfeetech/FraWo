# Control Plane Audit

- generated_at: `2026-04-09 17:19:47`
- workspace_pyrefly_disabled: `true`
- pyrefly_process_present: `false`
- stale_ssh_count: `0`
- stale_mail_powershell_count: `0`
- tailscale_backend_state: `Running`
- tailscale_stockenweiler_route_present: `True`
- ssh_stock_pve: `unreachable`
- wireguard_vpn_running: `false`

## Primary Paths

- anker_admin_path: `LAN + SSH aliases via ~/.ssh/hs27_ops_ed25519`
- stockenweiler_admin_path: `ssh stock-pve via toolbox-backed userspace WireGuard`
- stockenweiler_target_path: `Tailscale subnet-router on stockenweiler-pve for 192.168.178.0/24`

## Observations

- Primary Stockenweiler admin path is currently ssh stock-pve via toolbox-backed userspace WireGuard.
- Target professional bridge remains Tailscale subnet routing, not permanent dependence on the local stale Windows WireGuard tunnel.
- Workspace disables Pyrefly language services to avoid editor-side notify-file spam from a dead client.

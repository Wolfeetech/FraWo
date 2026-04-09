# Stockenweiler Tailscale Bridge Check

- generated_at: `2026-04-03 18:49:09`
- bridge_state: `route_approval_pending`
- remote_backend_state: `Running`
- remote_current_tailnet: `tail150400.ts.net`
- local_stockenweiler_route_present: `False`
- local_accept_routes_enabled: `True`
- remote_route_configured: `True`

## Observations

- Stockenweiler pve Tailscale backend is running.
- stockenweiler-pve is already joined to tail150400 and configured to advertise `192.168.178.0/24`, but the subnet route is not visible locally yet.
- The remaining blocker is route approval/distribution in Tailscale admin, not another login on stockenweiler-pve.
- visible local primary route: `192.168.2.0/24 via toolbox.tail150400.ts.net`

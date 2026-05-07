# Odoo Progress Note 2026-05-03

- Project: `🚀 Homeserver 2027: Masterplan`
- Suggested lane tags: `Lane C: Infra`, `Lane D: Stockenweiler`
- Suggested task/comment target: `Stockenweiler Monitoring & Host Stability`

## Impact

- `pve-stock` reached full host swap pressure (`8.0 / 8.0 GiB`) and the platform audit flagged an active blocker.

## Root Cause

- The primary cause was host-side `telegraf`, not AzuraCast itself.
- `telegraf` buffered several GiB of metrics against unreachable InfluxDB target `http://192.168.178.168:8086`.
- Observed footprint during incident:
  - `telegraf` approx. `5.2 GiB` RSS
  - `telegraf` approx. `3.8 GiB` swap

## Remediation

- Stopped `telegraf` on `pve-stock`
- Replaced `[[outputs.influxdb]]` temporarily with `[[outputs.discard]]`
- Backed up original config to `/etc/telegraf/telegraf.conf.bak.20260503_162434`
- Restarted `telegraf`
- Reclaimed swap with `swapoff -a && swapon -a`

## Verification

- `telegraf` stable again at roughly `32 MiB`
- `pve-stock` swap back to `0.0 / 8.0 GiB`
- Odoo direct/frontdoor stayed green (`HTTP 200` / `HTTP 200`)
- Latest platform audit moved to:
  - `top_priority_issue = none`
  - `blocker_count = 0`

## Follow-up

- Restore a real reachable Influx/metrics sink for `pve-stock`
- Keep `outputs.discard` only as a temporary protective stopgap
- Re-check host memory after steady runtime before deciding on VM rightsizing

## Additional Intake Drift Follow-up

- A separate `VM 200 nextcloud` restore path is now documented in:
  - `OPERATIONS/ODOO_AGENT_INTAKE_OPERATIONS.md`
  - `OPERATIONS/ODOO_AGENT_INTAKE_RESTORE_2026-05-03.md`
- Attempted board mirroring for that restore item was blocked in this session by intermittent `VM 220` guest-agent failures:
  - `QEMU guest agent is not running`
  - `qga command 'guest-exec' failed - got timeout`
- Retry the dedicated Odoo task creation or update only after the direct `qm guest exec 220` path is stable again.

## Board Rule Reminder

- The Odoo board should keep the operator-facing summary.
- The repo SSOT keeps the full technical root cause, commands, verification and rollback path.
- Actual board write should happen only via `ODOO_RPC_API_KEY` / `ODOO_RPC_PASSWORD` or an equivalent root-only runtime secret, not via local Klartext fallbacks.
- Board status on `2026-05-03`: the note landed in Odoo as task `Stockenweiler Monitoring & Host Stability`, written via the direct internal Odoo runtime on `VM 220` after the assumed `VM 200 nextcloud` secret path proved absent in the live filesystem probe.

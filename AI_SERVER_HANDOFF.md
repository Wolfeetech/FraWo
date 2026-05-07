# Handoff: OpenClaw Agent 3.1 & Odoo-Aligned Ops Update (2026-05-03)

## Status Summary
- **Agent Version:** 3.1 (Agentic ReAct Loop enabled).
- **Portal:** Stellar UI deployed to Toolbox (CT 100).
- **Odoo Runtime:** Direct path and frontdoor are green (`HTTP 200`); the `2026-05-03` Stockenweiler remediation is already mirrored into the Odoo master board via the internal runtime path on `VM 220`.
- **Safety:** Antigravity Guardian protocols active in `openclaw_web_server.py`.
- **Stockenweiler:** The swap incident from `2026-05-03` is remediated; root cause was `telegraf` buffering against unreachable `http://192.168.178.168:8086`.

## Current Findings
1. **`pve-stock` is stable again:** Host swap is back at `0.0 / 8.0 GiB` after `telegraf` stop, temporary `outputs.discard` switch and `swapoff/swapon`.
2. **Monitoring is only temporarily neutralized:** `telegraf` is healthy again, but metrics are currently discarded until a real reachable Influx/metrics sink is restored.
3. **Odoo board documentation is back in sync:** the latest remediation was written without local Klartext fallbacks, but the older `VM 200 nextcloud` secret/runbook path is currently drifted and should not be trusted blindly.
4. **`VM 200` intake is not live-ready:** the guest probe currently finds only `homeserver-compose-nextcloud.service`; the documented alias-router and Odoo-intake units/files are absent, `agent@frawo-tech.de` has `0` API keys, and external IMAP resolution on `VM 200` is not yet healthy.

## Ready-to-Run Skills
- `health_audit`: Full system check.
- `remote_exec`: Safe SSH execution via jump host.
- `sync_masterplan`: Odoo <-> Repo sync.

## Next Strategic Steps
1. Restore a real metrics sink for `pve-stock` and remove the temporary `outputs.discard` workaround.
2. Restore and re-validate the documented `VM 200 nextcloud` intake path: DNS, runtime files/units and a safe root-only `agent@` credential path all need to exist again before any automation resumes.
3. Continue `AZURACAST_PLAN.md` only after monitoring restoration and the `VM 200` doc drift are both closed.

---
**Operator Note:** The Stellar UI is live; the currently relevant runtime follow-up is monitoring restoration plus Odoo-side documentation, not another swap firefight.

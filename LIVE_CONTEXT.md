# LIVE CONTEXT

## Infrastructure Status & Governance (2026-05-10)

- **Status**: **ANKER OPERATIONAL, STOCKENWEILER OFFLINE**. CT 100 `toolbox` and all Anker-based services are operational.
- **CRITICAL**: **Stockenweiler PVE (`100.91.20.116` / `192.168.178.25`) is COMPLETELY OFFLINE**
  - Last seen on Tailscale: 1 day ago
  - Does not respond to ping via Tailscale, local network, or from Anker PVE bridge
  - **Requires physical intervention in Rothkreuz** to power on
  - **Affected services**: AzuraCast (VM 210), Home Assistant Eltern (VM 360), AdGuard (CT 101), Vaultwarden (CT 108)
  - **Blocked tasks**: All Lane E Radio tests, Lane D Remote Support tasks

- **Anker PVE (`100.69.179.87` / `10.4.0.92`)**: OPERATIONAL via Tailscale
- **Toolbox (CT 100)**: OPERATIONAL on `10.4.0.20`, Tailscale IP `100.82.26.53`. Caddy, AdGuard and Jellyfin running.

- **Verified frontdoors via Caddy/Tailscale (2026-05-10 22:55):**
  - `portal.hs27.internal` -> `HTTP 200` (64ms)
  - `odoo.hs27.internal` -> `HTTPS 200` (64ms) **[Note: Now requires HTTPS due to Caddy 308 redirect]**
  - `vault.hs27.internal` -> `HTTP 502` (3058ms) **[Backend down - likely on Stockenweiler]**
  - `ha.hs27.internal` -> `HTTP 502` (3040ms) **[Backend down - likely on Stockenweiler]**
  - `cloud.hs27.internal` -> `TIMEOUT` (>3s) **[Nextcloud backend issue]**
  - `paperless.hs27.internal` -> `HTTP 502` (3045ms) **[Backend down]**
  - `media.hs27.internal` -> Jellyfin redirect (not tested in latest check)

- **Odoo (VM 220 on Anker)**: LIVE via HTTPS at `https://odoo.hs27.internal`.
  - Database: `FraWo_GbR`
  - **42 active tasks** across 5 Lane projects (A, B, C, D, E)
  - Auth working with `admin@frawo-tech.de` / API access confirmed
  - **Lane projects** exist (no unified "Masterplan" project):
    - Lane A: Heritage & History (9 tasks, 2 in progress, 2 blocked)
    - Lane B: Website & Public Edge (9 tasks, 3 completed, 5 blocked)
    - Lane C: Security & PBS (9 tasks, 3 completed, 1 in progress, 2 blocked)
    - Lane D: Stockenweiler Migration (3 tasks, 1 blocked, 2 planning)
    - Lane E: Radio & Media (12 tasks, 3 completed, 4 blocked)

- **Security note**: VM-level firewalls on VM 210 and VM 220 are currently disabled to keep services reachable. A tested Proxmox firewall design is required before re-enabling them. Do not blindly set `firewall=1`; the first re-enable attempt dropped CT 100 traffic despite intended allow rules.

- **SSOT**: Repository at `~/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace` (Windows user: StudioPC, not Admin)

## Workspace Status

- Name: `FraWo GbR Ops Workspace`
- Operator: **Wolf** | Business User: **Franz**
- Current working path: `C:\Users\StudioPC\.gemini\antigravity\brain\Homeserver_2027_Ops_Workspace`
- Git status: clean, on `main` branch, synced with origin
- Identity: `hs27_ops_ed25519` / OpenClaw infra key for PVE access

## Active Track (2026-05-10)

- **Lane A**: Heritage/History - GbR Gründung in progress, Notar/Finanzamt blocked
- **Lane B**: Website/Public Edge - CSS/redesign completed, Logo/Public Edge/Cloudflare blocked
- **Lane C**: Security/PBS - **PBS Backups** task currently "In Arbeit" in Odoo - **PRIORITY**
- **Lane D**: Stockenweiler - **BLOCKED** until physical server access restored
- **Lane E**: Radio/Media - **BLOCKED** until Stockenweiler PVE restored

## Immediate Blocker Analysis (2026-05-10)

### **UNBLOCK NEEDED:**
1. **Stockenweiler PVE physical power-on** (Rothkreuz site visit required)
   - Blocks: Lane D (all 3 tasks), Lane E Radio tests (4 tasks)
   - Blocks: Services (AzuraCast, HA Eltern, AdGuard, Vaultwarden on Stockenweiler)

2. **Nextcloud backend timeout** (cloud.hs27.internal)
   - Blocks: Lane B "Nextcloud Desktop HTTPS Callback" task
   - Needs investigation: VM 200 status on Anker PVE

3. **Vaultwarden 502 error** (vault.hs27.internal)
   - Blocks: Lane C "Vaultwarden Sync" task
   - Likely running on Stockenweiler CT 108 (offline)

### **CAN PROCEED WITHOUT STOCKENWEILER:**
1. **Lane C: PBS Backups produktiv** ✅ Currently "In Arbeit" in Odoo
   - PBS should be on Anker infrastructure
   - Can proceed independently

2. **Lane A: GbR Gründung tasks** ✅ Business/administrative work
   - Not infrastructure-dependent

3. **Lane B: Logo/CI definition** ✅ Design work
   - Not infrastructure-dependent

## Immediate Next Actions (Prioritized for 2026-05-10)

1. **PRIORITY: Lane C - PBS Backups produktiv**
   - This is the only "In Arbeit" infrastructure task
   - Can proceed without Stockenweiler
   - Verify PBS status on Anker PVE
   - Check backup configuration and test restore

2. **Investigate Nextcloud timeout**
   - Check VM 200 status on Anker PVE
   - Verify Nextcloud container/service health
   - Potential quick win for Lane B unblock

3. **Document Stockenweiler outage for operator**
   - Update GitHub issue if exists
   - Create incident report
   - Schedule physical site visit to Rothkreuz

4. **Lane A business tasks**
   - GbR Gründung documentation (non-blocked tasks)
   - Can proceed in parallel to infrastructure work

---
*Updated: 2026-05-10 23:15 Europe/Berlin*
*Agent: Claude Sonnet 4.5 via claude-code*

# LIVE CONTEXT

## Infrastructure Status & Governance (2026-05-20)

- **Status**: **ANKER OPERATIONAL, STOCKENWEILER OFFLINE**. CT 100 `toolbox` and all Anker-based services are operational.
- **CRITICAL**: **Stockenweiler PVE (`100.91.20.116` / `192.168.178.25`) is COMPLETELY OFFLINE**
  - Last seen on Tailscale: 11 days ago (Needs physical power-on)
  - **Requires physical intervention in Rothkreuz** to power on.
  - **Affected services**: AzuraCast (VM 210), Home Assistant Eltern (VM 360), AdGuard (CT 101), Vaultwarden (CT 108)
  - **Blocked tasks**: All Lane E Radio tests, Lane D Remote Support tasks (now tagged `🛑 Blockiert` in Odoo)
  - **Action item**: Wolf must physically power on the server in Stockenweiler/Rothkreuz. Assigned to task: `[👤 WOLF] 🔌 Stockenweiler PVE physisch einschalten (Rothkreuz vor Ort)`.

- **Anker PVE (`100.69.179.87` / `10.4.0.92`)**: OPERATIONAL via Tailscale
- **Toolbox (CT 100)**: OPERATIONAL on `10.4.0.20`, Tailscale IP `100.82.26.53`. Caddy, AdGuard and Jellyfin running.

- **Verified frontdoors via Caddy/Tailscale (2026-05-20 15:50):**
  - `portal.hs27.internal` -> `HTTP 200` (60ms)
  - `odoo.hs27.internal` -> `HTTPS 200` (60ms)
  - `vault.hs27.internal` -> `HTTP 502` [Backend down - Stockenweiler offline]
  - `ha.hs27.internal` -> `HTTP 502` [Backend down - Stockenweiler offline]
  - `cloud.hs27.internal` -> `TIMEOUT` (>3s) [Nextcloud backend issue]
  - `paperless.hs27.internal` -> `HTTP 502` [Backend down]
  - `media.hs27.internal` -> Jellyfin redirect (Operational)

- **Odoo (VM 220 on Anker)**: LIVE via HTTPS at `https://odoo.hs27.internal`.
  - Database: `FraWo_GbR`
  - **85+ active tasks** consolidated into a single unified project: **`🚀 Homeserver 2027: Masterplan`**!
  - **Consolidation**: Completed today. All separate lane projects archived, creating a single unified SSOT Kanban board.
  - **Demarcation**: Tasks clearly split and prefixed:
    - `[🤖 AGENT]` for Agent automation & configuration tasks.
    - `[👤 WOLF]` for Wolf's business, physical, and manual tasks.
    - `[👤 FRANZ]` for Franz's Villa Bienert audio/visual stream tasks.
  - **Documentation**: Sync script configured. `MASTERPLAN.md`, `LIVE_CONTEXT.md`, and `STATUS.md` synced directly into Odoo under `📚 System-Dokumentation & SSOT (Masterplan, Live-Context, Status)` task description, with original markdown files attached.

- **Network Loop & Port Exhaustion Diagnostic (2026-05-20)**:
  - Dual-connection (WLAN to Easybox `192.168.2.1` and LAN to UCG `10.1.0.1`/`10.4.0.1`) causes WireGuard tunnels (Tailscale, Netbird, Cloudflared) to flap default gateways.
  - This flapping resulted in rapid UDP Port Exhaustion (Event 4266), crashing network connectivity.
  - Mitigated temporarily via routing metrics. Permanent solution is optimizing registry port parameters (MaxUserPort = 65534, TcpTimedWaitDelay = 30) via elevated Powershell terminal and eventually migrating all Shelly smart home devices from Easybox WLAN to the UCG's Wi-Fi network.

## Workspace Status

- Name: `FraWo GbR Ops Workspace`
- Operator: **Wolf** | Business User: **Franz**
- Current working path: `C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo`
- Git status: clean, on `main` branch, synced with remote origin.
- Identity: `hs27_ops_ed25519` / OpenClaw infra key for PVE access.

## Active Track (2026-05-20)

- **Lane A**: Heritage/History - GbR founding and administrative tasks in progress.
- **Lane B**: Website/Public Edge - Production live. CSS mobile wrap fixes applied and pushed. Cloudflare transform rules for security headers pending.
- **Lane C**: Security/PBS - Consolidated Masterplan. PBS tasks blocked until Stockenweiler host is online.
- **Lane D**: Stockenweiler - **BLOCKED** (Physical server visit by Wolf required).
- **Lane E**: Radio/Media - **BLOCKED** (Stockenweiler host offline).

---
*Updated: 2026-05-20 15:52 Europe/Berlin*
*Agent: Antigravity (Google DeepMind Advanced Agentic Coding)*

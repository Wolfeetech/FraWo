# LIVE CONTEXT

## Infrastructure Status & Governance (2026-05-03)

- **Status**: **STABLE AFTER RESTORE AND STOCKENWEILER SWAP FIX**. CT 100 `toolbox` is restored and the internal frontdoor is green again.
- **Stockenweiler**: Host `pve-stock` was stabilized on `2026-05-03`. Root cause was host-side `telegraf` buffering against unreachable `http://192.168.178.168:8086`; swap is now back at `0 GiB / 8 GiB`.
- **Verified frontdoors via Caddy/Tailscale `100.82.26.53`**:
  - `portal.hs27.internal` -> `HTTP 200`
  - `odoo.hs27.internal` -> `HTTP 200`
  - `vault.hs27.internal` -> `HTTP 200`
  - `ha.hs27.internal` -> `HTTP 200`
  - `cloud.hs27.internal` -> `HTTP 302` login/HTTPS redirect
  - `paperless.hs27.internal` -> `HTTP 302` login redirect
  - `media.hs27.internal` -> `HTTP 302` Jellyfin login redirect
- **Toolbox**: OPERATIONAL on `10.1.0.20`, Tailscale IP `100.82.26.53`. Caddy, AdGuard and Jellyfin are running.
- **Odoo (VM 220)**: LIVE on `10.1.0.22:8069`. The restore issue was not Docker-in-LXC; VM-level Proxmox firewall blocked CT 100 to VM 220.
- **VM 200 intake drift**: the historical `agent@`/alias-router runtime on `VM 200 nextcloud` is currently not present in the live guest probe. Only `homeserver-compose-nextcloud.service` was found; `agent@frawo-tech.de` also has `0` API keys at the moment, and external IMAP resolution from `VM 200` is not yet healthy.
- **Odoo app mail**: Sender error for sales cancellation was server-side fixed on `2026-04-22`: `wolf@frawo-tech.de` now has a partner email and `admin` uses `noreply@frawo-tech.de`. Template `Sales: Order Cancellation` renders `S00001` from `"Wolf Admin" <wolf@frawo-tech.de>`. Browser retest is still required before closing GitHub issue `#11`.
- **Home Assistant (VM 210)**: LIVE on `10.1.0.24:8123`. `trusted_proxies` includes `10.1.0.0/24` and `172.30.32.0/23`.
- **Vaultwarden (CT 120)**: LIVE on `10.1.0.26:8080`. Caddy upstream corrected from `:80` to `:8080`.
- **Media**: Jellyfin LIVE on host-network port `10.1.0.20:8096`; Caddy upstream corrected away from container-local `localhost`.
- **Storage**: root `/` at ~19% used, `ssd2tb` at ~4% used, `gdrive:` at ~22% used.
- **rclone**: Google Drive mount is active; nightly backup activity hit Google API quota/rate limits and needs backup-throttle/fallback work.
- **Security note**: VM-level firewalls on VM 210 and VM 220 are currently disabled to keep services reachable. A tested Proxmox firewall design is required before re-enabling them. Do not blindly set `firewall=1`; the first re-enable attempt dropped CT 100 traffic despite intended allow rules.
- **SSOT**: Repository `https://github.com/Wolfeetech/FraWo` and Odoo master project must be kept in sync.

## Workspace Status

- Name: `FraWo GbR Ops Workspace`
- Operator: **Wolf** | Business User: **Franz**
- Canonical Root: `C:\WORKSPACE`
- Working checkout: `C:\WORKSPACE\FraWo`
- Identity: `hs27_ops_ed25519` / OpenClaw infra key for PVE access

## Active Track

- **Lane A**: internal MVP remains sealed, but post-restore regression checks continue.
- **Lane B**: public website/HTTPS remains active and blocked by public edge/TLS path.
- **Lane C**: active priority for security audit, backups, DNS and storage sustainability.
- **Lane D**: active and stabilized; the host swap incident is remediated, but the monitoring output on `pve-stock` is only temporarily neutralized via `outputs.discard`.
- **Lane E**: media is green; the radio dual-site frontdoor is corrected live and now separates Anker (`radio.hs27.internal`, `radio-anker.hs27.internal`) from Stockenweiler (`radio-stock.hs27.internal`).

## Immediate Next Projects

1. **Security audit follow-through**
   - design and test VM 210/220 firewall rules without breaking CT 100 frontdoor traffic
   - restrict PVE host NFS/RPC exposure to trusted internal networks
   - review SSH authorized keys and keep OpenClaw key state documented
2. **Backups after restore**
   - verify nightly backup target and storage mapping
   - add rclone rate-limit/backoff or local `ssd2tb` fallback
   - run a post-restore backup/restore proof after the firewall and Caddy changes
3. **DNS cleanup**
   - move from Windows hosts-file workaround toward UniFi/Tailscale split-DNS
   - finalize `hs27.internal` restricted nameserver path
4. **CT 100 storage migration**
   - migrate CT 100 disk from `local-lvm`/NVMe to `ssd2tb` in a controlled maintenance window
5. **Odoo application layer**
   - the Odoo SSOT project now carries the `2026-05-03` Stockenweiler remediation, root cause, verification and follow-up via direct internal write on `VM 220`
   - `VM 200 nextcloud` intake automation is currently a restore target, not a trusted runtime; restore DNS, runtime files/units and the `agent@` credential path before reusing it
   - browser-retest quote cancellation mail after sender fix, then close GitHub `#11`
   - resolve `res.users.log` ACL warnings and finalize productive user/project setup
6. **Radio dual-site stabilization**
   - keep `toolbox` on the corrected split: Anker default host plus explicit Stockenweiler host
   - expand the central media target before attempting any full `283G` Stockenweiler library migration
   - normalize AzuraCast credentials and public listen URLs across both radio nodes
7. **Stockenweiler monitoring follow-through**
   - restore a real reachable metrics sink for `telegraf`; the current `discard` output is only a protective stopgap
   - re-check host memory after 24h steady-state runtime
   - only then decide on VM rightsizing or workload moves

---
*Updated: 2026-05-03 16:27 Europe/Berlin*

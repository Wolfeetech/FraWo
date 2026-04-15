# Security Baseline

## Goal

Capture the current low-drama security posture for the Homeserver 2027 platform and make the daily checks repeatable.

## Baseline Controls

- No public exposure is enabled in the current operating model.
- Business services run on dedicated VMs.
- Secrets belong only in `ansible/inventory/group_vars/all/vault.yml`.
- Local backup protection for `VM 200`, `VM 220` and `VM 230` is live on Proxmox.
- AdGuard Home admin is loopback-only on `toolbox`.
- The mobile Tailscale frontdoor on `toolbox` is restricted to Tailscale traffic and no longer reachable from the LAN.
- The shared internal portal `portal.hs27.internal` is now part of the managed frontdoor set.

## Latest Verified Snapshot - 2026-03-19

- Workspace secret hygiene:
  - no plaintext router password found outside Vault
  - no plaintext Tailscale auth key found in the workspace
- Network surface:
  - `toolbox` exposes `22`, `53` and `80` on the LAN
  - `toolbox` mobile proxy ports `8443-8448` are intentionally available only over Tailscale and are blocked from the LAN by `homeserver2027-toolbox-mobile-firewall.service`
  - `tailscaled` also keeps dynamic listener ports on the Tailscale-only addresses; these are expected control-plane listeners and are no longer treated as LAN surface
  - AdGuard Home admin remains available only on `127.0.0.1:3000` inside `toolbox`
  - `nextcloud` exposes app port `80` plus SSH
  - `odoo` exposes app port `8069` plus SSH
  - `paperless` exposes app port `8000` plus SSH
  - no database ports were observed on public interfaces of the business VMs
  - `LLMNR` port `5355` is no longer exposed on the business VMs after the morning hardening pass
- Control-plane state:
  - Tailscale on `toolbox` is joined and healthy
  - the mobile Tailscale frontdoor is live on `100.99.206.128:8443-8448`
  - PBS rollout is prepared, the official installer ISO is staged on Proxmox, and the remaining stage-gate blocker is missing separate backup storage
  - public exposure remains disabled
  - `make security-baseline-check` is currently green with `security_status=ok`

## Findings

1. Medium: The durable PBS operating model is not live yet.
   - The runner path and stage-gate checks are now prepared.
   - The blocker is no longer design uncertainty or installer media, but missing separate backup storage.
2. Medium: Tailnet route approval and split-DNS are still not finished.
   - The mobile Tailscale frontdoor is a clean interim path, but the long-term DNS model is not fully closed yet.
3. Low: Business VMs inherited `LLMNR` and `MulticastDNS` defaults from the guest OS.
   - This was unnecessary on server nodes.
   - The issue is remediated as of `2026-03-18` through `ansible/playbooks/harden_business_network_baseline.yml`.

## Daily Operator Command

```bash
make security-baseline-check
```

## Next Hardening Moves

1. Complete Tailnet route approval and then close the `hs27.internal` split-DNS path.
2. Reconcile router leases and reservations.
3. Keep AdGuard Home in pilot mode with localhost-only admin until DHCP ownership and rollback are documented.
4. Move from local backup stopgap to PBS-backed standard by adding separate backup storage and then building `VM 240` through the staged runner path.
5. Keep the mobile frontdoor Tailscale-only unless and until a different managed edge pattern replaces it.

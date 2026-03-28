# Introduction Prompt

## Purpose

- Use this file as the first context block for AI research tasks.
- This file contains only hard current-state facts, not target architecture or wishful planning.
- If a fact is not listed here, verify it against the latest audit artifacts before using it.
- After reading this file, choose the specialized prompt that matches the task:
  - `BUSINESS_MVP_PROMPT.md`
  - `WEBSITE_RELEASE_PROMPT.md`
  - `FULL_CERTIFICATION_PROMPT.md`

## Hard Verification Sources

- Proxmox guest status was queried live on `2026-03-28`.
- Business-MVP technical snapshot:
  - `artifacts/release_mvp_audit/20260328_004657/summary.tsv`
- Business-MVP decision:
  - `artifacts/release_mvp_gate/20260328_004741/release_mvp_gate.md`
- Full certification decision:
  - `artifacts/production_gate/20260327_235023/production_gate.md`
- Shared frontend live audit:
  - `artifacts/stress_tests/20260327_234807/surface-go-check.log`
- Radio integration live audit:
  - `artifacts/stress_tests/20260327_234807/rpi-radio-integration-check.log`
- App SMTP live audit:
  - `artifacts/stress_tests/20260327_234807/app-smtp-check.log`

## Estate Snapshot

- Router / gateway: `192.168.2.1` `easy_box`
- Hypervisor: `192.168.2.10` `proxmox`
- Internal DNS zone: `hs27.internal`
- Main admin workstation: `wolfstudiopc`
- Organization: `FraWo`
- Primary operator: `Wolf`
- Primary business user rollout: `Franz`

## Live Guest Inventory

- Running CTs:
  - `100` `toolbox`
  - `110` `storage-node`
  - `120` `vaultwarden`
- Running VMs:
  - `200` `nextcloud`
  - `210` `haos`
  - `220` `odoo`
  - `230` `paperless`
- Stopped VMs:
  - `240` `pbs`

## What Runs Where

- `CT100 toolbox`:
  - internal reverse proxy / Caddy
  - root portal
  - Tailscale subnet router and mobile frontdoor
  - AdGuard Home in opt-in/internal mode
  - Jellyfin
- `CT110 storage-node`:
  - running as the current shared storage node on Proxmox
- `CT120 vaultwarden`:
  - Vaultwarden service
  - direct container health path on `192.168.2.26:8080`
  - productive entry through internal HTTPS
- `VM200 nextcloud`:
  - Nextcloud
- `VM220 odoo`:
  - Odoo
- `VM230 paperless`:
  - Paperless
- `VM210 haos`:
  - Home Assistant OS
- `VM240 pbs`:
  - exists, but currently stopped and not green
- External/standalone nodes:
  - radio node at `192.168.2.155` and Tailscale `100.64.23.77`
  - shared frontend target `surface-go-frontend` at `192.168.2.154`

## Current Internal Entry Points

- Portal: `http://portal.hs27.internal`
- Franz portal: `http://portal.hs27.internal/franz/`
- Vaultwarden: `https://vault.hs27.internal`
- Vaultwarden health: `http://192.168.2.26:8080/alive`
- Nextcloud: `http://cloud.hs27.internal`
- Paperless: `http://paperless.hs27.internal`
- Odoo: `http://odoo.hs27.internal`
- Home Assistant: `http://ha.hs27.internal`
- Jellyfin browser path: `http://media.hs27.internal`
- Jellyfin TV-safe direct path: `http://192.168.2.20:8096`
- Radio frontdoor path: `http://radio.hs27.internal`

## Current Mobile / Tailscale Frontdoor Paths

- Home Assistant: `http://100.99.206.128:8443`
- Odoo: `http://100.99.206.128:8444`
- Nextcloud: `http://100.99.206.128:8445`
- Paperless: `http://100.99.206.128:8446`
- Portal: `http://100.99.206.128:8447`
- Radio: `http://100.99.206.128:8448`
- Jellyfin: `http://100.99.206.128:8449`

## Current Hard-Green Business Facts

- `Nextcloud`, `Paperless`, and `Odoo` are technically green in the current Business-MVP audit.
- `Vaultwarden` SMTP is green and invitation mail is working.
- `Franz` accepted the `FraWo` invite.
- `webmaster@frawo-tech.de` and `franz@frawo-tech.de` are technically verified for `IMAP` and `SMTP AUTH`.
- Local Proxmox business backups are present and green in the current Business-MVP audit.
- `core_business_app_smtp_ready=yes` for:
  - `Nextcloud`
  - `Paperless`
  - `Odoo`

## Current Hard-Blocked Facts

- `release-mvp-gate` is currently `BLOCKED`, but only because manual evidence is still pending.
- Full `production-gate` is `BLOCKED`.
- `PBS` is not operationally green:
  - `VM240` is stopped
  - datastore is not green
  - proof backup is not green
  - restore proof is not green
- `surface-go-frontend` is not operationally green:
  - `SSH` closed
  - `HTTP` closed
  - `HTTPS` closed
  - current recommendation is `clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook`
- `Radio/AzuraCast` is not operationally green:
  - proxy/frontdoor answers
  - radio node itself does not answer cleanly
  - `rpi_radio_integrated=no`
  - `rpi_radio_usb_music_ready=no`
- Full-scope app SMTP is not green:
  - `AzuraCast` SMTP is still not ready

## Current Release Boundaries

- Current internal Business-MVP scope:
  - `Portal`
  - `Vaultwarden`
  - `Nextcloud`
  - `Paperless`
  - `Odoo`
  - STRATO mail backbone
  - local Proxmox business backups
- Explicitly outside the current Business-MVP gate:
  - `PBS`
  - `surface-go-frontend`
  - `Radio/AzuraCast`
  - shared frontend certification
  - full-scope app SMTP
- Current public release scope:
  - website only on `www.frawo-tech.de`
  - no public business UIs
  - no public radio path in the first release

## Research Guardrails

- Do not call the platform production-ready unless the latest full `production-gate` says `CERTIFIED`.
- Do not assume `PBS`, `surface-go-frontend`, or `Radio/AzuraCast` are healthy.
- Do not assume every document in the repo is current; treat the latest audit artifacts as the deciding truth.
- For current research, prioritize the Business-MVP unless the task explicitly targets certification, backups, radio, or the shared frontend.

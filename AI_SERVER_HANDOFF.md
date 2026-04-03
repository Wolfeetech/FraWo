# AI Server Handoff

Automatisch generierter Ein-Datei-Handoff fuer den aktuellen Homeserver-Stand.
Keine Secrets. Keine Passwoerter. Diese Datei ist dafuer gedacht, sie direkt an eine andere KI zu geben.

## Nutzung

- Primaerer Read-First fuer eine andere KI: diese Datei
- Wenn tieferer Repo-Kontext noetig ist: `INTRODUCTION_PROMPT.md`, `OPS_HOME.md`, `OPERATOR_TODO_QUEUE.md`
- Diese Datei neu erzeugen mit: `python scripts/generate_ai_server_handoff.py`

## Generierung

- Generated at: `2026-04-03 19:32:27`
- Workspace root: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace`
- Git branch: `main`
- Pending git changes: `49`
- Managed hosts in inventory: `30`

## Source Freshness

- `AI_BOOTSTRAP_CONTEXT.md`: `2026-04-03 19:13:57`
- `OPS_HOME.md`: `2026-03-31 06:53:07`
- `OPERATOR_TODO_QUEUE.md`: `2026-04-03 19:13:16`
- `manifests/work_lanes/current_plan.json`: `2026-04-03 18:48:56`
- `artifacts/release_mvp_gate/latest_release_mvp_gate.json`: `2026-03-31 09:57:09`
- `artifacts/public_ipv6_exposure_audit/latest_report.md`: `2026-03-31 06:32:34`
- `artifacts\website_release_gate\20260330_161648\website_release_gate.md`: `2026-03-30 16:16:48`
- `artifacts\production_gate\20260328_072130\production_gate.md`: `2026-03-28 07:21:32`
- `manifests/control_surface/actions.json`: `2026-03-30 21:53:25`

## Estate Snapshot

- Organization: `FraWo`
- Primary operator/admin: `Wolf`
- Primary business user rollout: `Franz`
- Gateway/router: `192.168.2.1` `easy_box`
- Proxmox host: `192.168.2.10` `proxmox`
- Core toolbox/control node: `192.168.2.20` `toolbox`
- Nextcloud VM: `192.168.2.21`
- Odoo VM: `192.168.2.22`
- Paperless VM: `192.168.2.23`
- Home Assistant OS VM: `192.168.2.24`
- PBS VM target: `192.168.2.25`, currently `degraded`
- Vaultwarden CT: `192.168.2.26:8080`, productive entry via `https://vault.hs27.internal`
- Radio node: `192.168.2.155` and Tailscale `100.64.23.77`
- Shared frontend node: `surface-go-frontend` on `192.168.2.154`
- Separate Stockenweiler legacy support LAN exists on `192.168.178.0/24`
- Internal DNS zone: `hs27.internal`
- Tailscale subnet router and internal reverse proxy live on `toolbox`

## Core Service Map

- Root control portal: `http://portal.hs27.internal`
- Franz start page: `http://portal.hs27.internal/franz/`
- Nextcloud: `http://cloud.hs27.internal` and direct `http://192.168.2.21`
- Paperless: `http://paperless.hs27.internal` and direct `http://192.168.2.23`
- Odoo: `http://odoo.hs27.internal` and direct `http://192.168.2.22:8069`
- Home Assistant: `http://ha.hs27.internal` and direct `http://192.168.2.24:8123`
- Vaultwarden: `https://vault.hs27.internal`
- Vaultwarden health/bootstrap path: `http://192.168.2.26:8080/alive`
- Vaultwarden admin path: `https://vault.hs27.internal/admin`
- Jellyfin browser path: `http://media.hs27.internal`
- Jellyfin TV-safe path: `http://192.168.2.20:8096`
- Jellyfin mobile Tailscale path: `http://100.99.206.128:8449`
- Radio UI: `http://radio.hs27.internal`
- Radio mobile Tailscale path: `http://100.99.206.128:8448`

## Current Release State

- Active delivery lane: `Lane A: MVP Closeout`
- Business MVP gate: `BLOCKED`
- Business MVP critical Codex checks: `passed=11` / `non-passed=0`
- Business MVP manual checks: `passed=6` / `pending_or_failed=2`
- Public website gate: `BLOCKED`
- Production certification gate: `BLOCKED`
- Public IPv6 exposure audit: `open_checks=0` / `total_checks=13`

## AI Operating Model

- Model: `professional_autopilot`
- Autonomy: `aggressive_autopilot`
- Primary end state: `internal_ops_first`
- Roles: `codex=lead` / `gemini=visible_verification_only` / `operator=decision_and_physical_actions_only`
- Execution loop: `read_only_truth, professional_check, change_classification, decision, post_verify, ssot_refresh`
- Mandatory stop categories:
  - `infra_public_changes`
  - `network_changes`
  - `data_migrations`
  - `storage_pbs_changes`
  - `router_changes`
  - `ha_pve_changes`
  - `security_boundary_changes`
  - `local_windows_admin_token_changes`
  - `irreversible_or_hard_to_rollback_changes`

## Control Plane Snapshot

- Workspace Pyrefly disabled: `true`
- Pyrefly process present: `false`
- Stale ssh helpers: `0`
- Stale mail powershell: `0`
- Tailscale backend: `Running` / stockenweiler route visible `False`
- ssh stock-pve: `reachable`
- Local WireGuard VPN service running: `true`
- Primary Stockenweiler admin path is currently ssh stock-pve via toolbox-backed userspace WireGuard.
- Target professional bridge remains Tailscale subnet routing, not permanent dependence on the local stale Windows WireGuard tunnel.
- Workspace disables Pyrefly language services to avoid editor-side notify-file spam from a dead client.

## Current Lane Model

- `Lane A: MVP Closeout` -> `active`
  - goal: Close the internal business MVP with the remaining visible manual proofs.
- `Lane B: Website/Public Hold` -> `watch`
  - goal: Keep the public website truth path and blockers visible without pulling the track into active release work.
- `Lane C: Security/PBS/Infra` -> `watch`
  - goal: Keep hardening, reapply paths, and audits green without expanding the scope into a full infrastructure program.
- `Lane D: Stockenweiler` -> `watch`
  - goal: Keep the support concept, inventory baseline, remote-access model, and deferred phase-2 backlog visible without starting a live rollout or network marriage.
- `Lane E: Radio/Media` -> `hold`
  - goal: Keep radio and media operational without new feature work or UI expansion.

## Business MVP Blockers

- `device_rollout_verified`: `pending`
  - Open rollout blocker 2026-03-31: Franz Surface Laptop still needs visible acceptance on http://portal.hs27.internal/franz/ and Franz iPhone still needs visible acceptance on http://100.99.206.128:8447/franz/. Both start paths must visibly expose the core direct targets for Nextcloud, Paperless, Odoo and Vaultwarden before this check can pass. The rollout is currently additionally blocked by the missing 2FA path while the operator smartphone is still lost.
- `vaultwarden_recovery_material_verified`: `pending`
  - No fresh proof yet that the Vaultwarden recovery material exists offline in two separate physical copies.

## Public Website Release State

- This track is separate from the internal business MVP.
- Latest website gate source: `artifacts\website_release_gate\20260330_161648\website_release_gate.md`
- Current blocked reasons:
  - public-http-redirect-check=failed
  - public-dualstack-edge-check=failed
  - public-https-check=failed
  - public-mail-dns-check=failed
  - public_browser_acceptance_verified=failed
  - public_mail_model_verified=pending

## Security Posture Snapshot

- Latest public IPv6 re-audit timestamp: `20260331_063204`
- Public IPv6 direct exposure findings open: `0`
- Verified closed in the current audit: direct public IPv6 checks for `nextcloud`, `odoo`, `paperless`, `vaultwarden`, `storage-node`, `homeassistant`.
- Important limitation: this is risk reduction, not a promise of zero risk.
- Public edge and TLS are still not in a final green release state.

## Stockenweiler Snapshot

- Lane state remains `watch`; no live rollout, no site marriage, no site-to-site VPN.
- Primary remote access model: `tailscale` / fallback `anydesk`
- Stockenweiler endpoints currently modeled: `8`
- Current Stockenweiler blockers: `13`
- Current direction:
  - parents' scan folders stay local first
  - later document automation should use a separate Stockenweiler Paperless DB
  - radio is later hosted on the most stable hardware, not by ideology of site
  - Stockenweiler PVE HDDs are only a future PBS/storage complement candidate
- Public truth / DynDNS split: dyn-dns-like `2`
  - home.prinz-stockenweiler.de resolves via the canonical name yourparty.tech to 91.14.44.20 and returns HTTPS 200.
  - cloud.prinz-stockenweiler.de resolves via the canonical name yourparty.tech to 91.14.44.20 but currently fails TLS/SNI.
  - papierkram.prinz-stockenweiler.de resolves directly to 80.134.168.100 and currently times out on HTTPS.
- Remote path truth: tailscale `Running`, route_all `True`, stockenweiler route visible `False`
  - ssh `stock-pve` is `reachable`; AnyDesk candidates `7`
  - Tailscale backend is `Running` on StudioPC.
  - Visible Tailscale primary routes are currently limited to: 192.168.2.0/24 via toolbox.tail150400.ts.net.
- Management bridge: state `route_approval_pending`, target `Tailscale subnet-router on stockenweiler-pve for 192.168.178.0/24`
  - fallback `StudioPC -> toolbox -> userspace WireGuard wgstkw -> 192.168.178.25` / direct local WG reachable `False`
  - next operator action: Approve the advertised subnet route 192.168.178.0/24 for stockenweiler-pve in Tailscale admin so the route becomes visible on StudioPC.
- Visible legacy host check: reachable `1` / broken `3`
  - Home Assistant is the only legacy host that still presents a frontend at HTTPS level.
  - Paperless currently times out on port 443.
  - Nextcloud currently fails with ERR_SSL_UNRECOGNIZED_NAME_ALERT, which points to a reverse-proxy or certificate SNI mismatch.
- Latest Stockenweiler PVE read-only probe: `reachable` on target `stock-pve`

## Surface Control V1

- Ready actions: `7`
- Ready groups: `Dokumente, Odoo, Radio`
- `Nextcloud Eingang` -> `http://cloud.hs27.internal/apps/files/files?dir=/Paperless/Eingang`
- `Paperless` -> `http://paperless.hs27.internal/dashboard`
- `Odoo Aufgaben` -> `http://odoo.hs27.internal/web#action=118&active_id=8&model=project.task&view_type=kanban&menu_id=352`
- `Odoo Projekte` -> `http://odoo.hs27.internal/web#action=252&model=project.project&view_type=kanban&menu_id=141`
- `Odoo Kalender` -> `http://odoo.hs27.internal/web#action=517&model=project.task&view_type=calendar&menu_id=357`
- `Radio hoeren` -> `http://radio.hs27.internal/public/frawo-funk`
- `Radio Control` -> `http://radio.hs27.internal/login`
- Backlog-only actions remain hidden:
  - `Dokument scannen` (`Dokumente`)
  - `TV / Magenta Hilfe` (`Stockenweiler`)
  - `Fernhilfe` (`Stockenweiler`)
  - `Vater Home Assistant` (`Stockenweiler`)

## Access And Secret Rules

- Shared passwords and shared app credentials belong in the `FraWo` organization in Vaultwarden.
- No plaintext credentials in markdown, ad hoc notes, or repo-tracked local files.
- `wolf@frawo-tech.de` is the operator identity, but the technical base mailbox for app SMTP is `webmaster@frawo-tech.de`.
- `franz@frawo-tech.de` is a real mailbox and was technically verified against STRATO IMAP/SMTP.
- App SMTP authenticates with `webmaster@frawo-tech.de`.
- The visible app sender is `noreply@frawo-tech.de`.
- Vaultwarden is invite-only for productive use.

## Current Operator Queue

### `device_rollout_verified`

- `status`: `pending`
- `lane`: Lane A: MVP Closeout
- `change_class`: repo_only
- `goal`: Franz Surface Laptop and iPhone are visibly accepted as released MVP devices with the required direct entry paths.
- `done_when`: Franz Surface Laptop and Franz iPhone both have the required direct app entrypoints and the visible everyday path is confirmed.
- `blocked_by`: `visible_device_acceptance_missing`, `operator_smartphone_lost_2fa_block`
- `preflight_checks`: `python scripts/device_rollout_preflight.py returns ready_for_manual_device_acceptance`, `latest MVP gate still shows device_rollout_verified as pending before closure`
- `rollback_plan`: If the visible evidence is incomplete or inconsistent, keep the manual check pending and do not refresh the gate as passed.
- `verification_commands`: `python scripts/device_rollout_preflight.py`, `powershell -ExecutionPolicy Bypass -File .\scripts\prove_device_rollout.ps1`
- `last_verified_at`: 2026-04-03
- `next_operator_action`: Recover the missing 2FA path blocked by the lost operator smartphone, then walk the Franz Surface Laptop and iPhone through the real direct entrypoints and capture a fresh visible acceptance result.
- `next_codex_action`: Run scripts/device_rollout_preflight.py first. If it stays ready_for_manual_device_acceptance, use scripts/prove_device_rollout.ps1 with the fresh visible Surface Laptop and iPhone evidence so the MVP gate and AI handoff refresh automatically.

### `vaultwarden_recovery_material_verified`

- `status`: `pending`
- `lane`: Lane A: MVP Closeout
- `change_class`: repo_only
- `goal`: Vaultwarden recovery material exists offline in two separate physical copies.
- `done_when`: Two separate offline copies exist and a fresh visible proof is recorded instead of relying on assumption.
- `blocked_by`: `fresh_offline_proof_missing`
- `preflight_checks`: `Fresh visible proof exists for two separate offline recovery copies`, `latest MVP gate still shows vaultwarden_recovery_material_verified as pending before closure`
- `rollback_plan`: If the proof is stale or not visibly separate, keep the manual check pending and do not refresh the gate as passed.
- `verification_commands`: `python scripts/release_mvp_gate.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Create or verify two separate offline copies of the Vaultwarden recovery material and provide a fresh proof.
- `next_codex_action`: Update the manual MVP check, rerun release_mvp_gate.py, and regenerate AI_SERVER_HANDOFF.md.

## Visible Side Strands

### `website_public_hold`

- `status`: `watch`
- `lane`: Lane B: Website/Public Hold
- `change_class`: read_only
- `goal`: Public website work stays visible as a paused truth path, not as an active release lane.
- `done_when`: Lane A is closed and public edge work is intentionally reactivated.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `preflight_checks`: `Review latest website gate`, `Review latest public IPv6 exposure audit`, `Confirm Lane A is still the active delivery lane`
- `rollback_plan`: No runtime mutation; only truth-path refreshes and blocker updates.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: No action unless a new public regression must be documented.
- `next_codex_action`: Keep the website gate, blockers, and security notes current; do not resume public release implementation.

### `control_plane_clean`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: reversible_runtime
- `goal`: Keep one clean control plane per target, reduce stale helper paths and local noise, and make the primary admin paths explicit.
- `done_when`: Stale local helper processes are reduced, workspace Pyrefly noise is suppressed, and the canonical admin path for Anker and Stockenweiler is verifiably documented.
- `blocked_by`: `local_windows_admin_token_needed_for_full_wireguard_cleanup`, `stockenweiler_tailscale_subnet_route_approval_pending`
- `preflight_checks`: `Collect current process, service and route truth with scripts/control_plane_audit.py`, `Confirm stock-pve remains reachable before cleaning stale local helper paths`, `Do not perform Windows admin-token actions without an explicit gated stop`
- `rollback_plan`: If cleanup removes a useful path, restore the canonical admin path only: direct Anker aliases plus ssh stock-pve via toolbox-backed WireGuard. Do not reactivate old parallel paths blindly.
- `verification_commands`: `python scripts/control_plane_audit.py`, `powershell -ExecutionPolicy Bypass -File .\scripts\cleanup_stale_control_plane_processes.ps1`, `python scripts/control_plane_audit.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Only intervene if an elevated Windows token is needed for full WireGuard cleanup or if the advertised subnet route 192.168.178.0/24 for stockenweiler-pve must be approved in Tailscale admin.
- `next_codex_action`: Run the control-plane audit, keep the workspace-level Pyrefly suppression in place, remove only clearly stale helper processes, and keep Tailscale-first with ssh stock-pve as the current Stockenweiler admin path until the bridge is approved.

### `security_pbs_infra_watch`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: read_only
- `goal`: Hardening, PBS status, and infrastructure guardrails remain visible without becoming the active delivery lane.
- `done_when`: Lane A is closed and a dedicated certification or PBS rebuild block is intentionally resumed.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `preflight_checks`: `Review latest hardening audits`, `Review latest PBS/runtime blockers`, `Confirm no new regression has appeared`
- `rollback_plan`: No broad infra mutation in watch mode; only regression response and audit refresh.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Only escalate if a new regression appears.
- `next_codex_action`: Maintain the existing audit-green state and the reapply paths; avoid broad new infra work.

### `wolf_arbeitssurface_access_model`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `change_class`: repo_only
- `goal`: Keep Wolfs Arbeitssurface as a separate trusted client with split access: normal local work by default, internal full access only on demand.
- `done_when`: The device is documented and treated separately from Franz Surface Laptop, with no permanent full-tunnel and no blind RouteAll requirement.
- `blocked_by`: `surface_laptop_identity_needs_live_revalidation`
- `preflight_checks`: `Confirm Surface_Laptop remains modeled separately from Franz Surface Laptop`, `Confirm no full-tunnel or blind RouteAll requirement has been introduced`
- `rollback_plan`: Revert documentation-only drift if the live identity is disproven; do not push runtime VPN policy without a gated decision.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Confirm that the active WLAN device Surface_Laptop on 192.168.2.118 is Wolfs current Arbeitssurface and whether Tailscale is already installed there.
- `next_codex_action`: Keep the split-access model canonical in NETWORK_INVENTORY.md, OPERATIONS/USER_ONBOARDING_OPERATIONS.md, and AI_BOOTSTRAP_CONTEXT.md; do not fold the device into the Franz or kiosk paths.

### `stockenweiler_watch`

- `status`: `watch`
- `lane`: Lane D: Stockenweiler
- `change_class`: read_only
- `goal`: Stockenweiler stays visible as a prepared support track with inventory, remote-access concept, and a deferred management-first phase-2 backlog only.
- `done_when`: Lane A is closed and Stockenweiler is explicitly promoted into an active rollout.
- `blocked_by`: `lane_a_mvp_closeout_active`, `ucg_2fa_unavailable`
- `preflight_checks`: `Verify stock-pve access path still works`, `Review latest Stockenweiler public truth, remote path and storage probe artifacts`, `Confirm Lane A remains active so no live rollout starts`
- `rollback_plan`: Stay in truth-collection mode only; no site marriage, no migration, no router/public changes.
- `verification_commands`: `python scripts/stockenweiler_public_truth_check.py`, `python scripts/stockenweiler_remote_path_probe.py`, `python scripts/stockenweiler_pve_storage_probe.py`, `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: No live rollout, gateway work, or site marriage; only share new real device facts, provider findings, or FRITZ/Tailscale observations if available.
- `next_codex_action`: Keep inventory, support planning, and the phase-2 backlog current; prefer read-only truth collection such as scripts/stockenweiler_pve_storage_probe.py, but do not start the rollout, site-to-site VPN, or service consolidation.

### `radio_media_hold`

- `status`: `hold`
- `lane`: Lane E: Radio/Media
- `change_class`: read_only
- `goal`: Radio and media remain operational, but expansion work stays out of the active queue.
- `done_when`: Lane A is closed and there is an explicit decision to expand radio/media again.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `preflight_checks`: `Check only for breakage that affects current radio/media operation`
- `rollback_plan`: No expansion in hold mode; only restore known-good operation if breakage appears.
- `verification_commands`: `python scripts/generate_ai_server_handoff.py`
- `last_verified_at`: 2026-03-31
- `next_operator_action`: Only report breakage that impacts current operation.
- `next_codex_action`: Hold the current operating state; no new features, no new public surface.

## Recommended Next Planning Order

- First close `device_rollout_verified` in `Lane A: MVP Closeout`.
- First close `vaultwarden_recovery_material_verified` in `Lane A: MVP Closeout`.
- Keep `website_public_hold` visible in `Lane B: Website/Public Hold` without promoting it into active delivery.
- Keep `control_plane_clean` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `security_pbs_infra_watch` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `wolf_arbeitssurface_access_model` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `stockenweiler_watch` visible in `Lane D: Stockenweiler` without promoting it into active delivery.
- Keep `radio_media_hold` visible in `Lane E: Radio/Media` without promoting it into active delivery.

## Canonical Files To Read Next

- `AI_OPERATING_MODEL.md`
- `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`
- `INTRODUCTION_PROMPT.md`
- `BUSINESS_MVP_PROMPT.md` oder `WEBSITE_RELEASE_PROMPT.md` oder `FULL_CERTIFICATION_PROMPT.md` je nach Arbeitsmodus
- `GEMINI_BROWSER_MVP_ACCEPTANCE_PROMPT.md` fuer die offenen Browser-Abnahmen im MVP
- `AI_BOOTSTRAP_CONTEXT.md`
- `AI_SERVER_HANDOFF.md`
- `OPERATOR_TODO_QUEUE.md`
- Release-MVP-Gate: `artifacts/release_mvp_gate/latest_release_mvp_gate.md`
- Produktions-Gate: `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`
- Dokument-Ownership: `OPERATIONS/DOCUMENT_OWNERSHIP_OPERATIONS.md`
- Benutzer-Onboarding: `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- Operator-Routinen: `OPERATIONS/OPERATOR_ROUTINES.md`
- Vaultwarden Start: `VAULTWARDEN_SELFHOST_START.md`

## Generator Notes

- This file is generated from current source-of-truth docs and latest gate/audit artifacts.
- If a source file is older than the newest hardening change, prefer the fresher artifact listed in `Source Freshness`.
- For runtime operations, do not invent credentials or provider-side state that is not visible in the cited sources.

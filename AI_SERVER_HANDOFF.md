# AI Server Handoff

Automatisch generierter Ein-Datei-Handoff fuer den aktuellen Homeserver-Stand.
Keine Secrets. Keine Passwoerter. Diese Datei ist dafuer gedacht, sie direkt an eine andere KI zu geben.

## Nutzung

- Primaerer Read-First fuer eine andere KI: diese Datei
- Wenn tieferer Repo-Kontext noetig ist: `INTRODUCTION_PROMPT.md`, `OPS_HOME.md`, `OPERATOR_TODO_QUEUE.md`
- Diese Datei neu erzeugen mit: `python scripts/generate_ai_server_handoff.py`

## Generierung

- Generated at: `2026-03-31 08:42:49`
- Workspace root: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace`
- Git branch: `main`
- Pending git changes: `57`
- Managed hosts in inventory: `30`

## Source Freshness

- `AI_BOOTSTRAP_CONTEXT.md`: `2026-03-30 07:32:46`
- `OPS_HOME.md`: `2026-03-31 06:53:07`
- `OPERATOR_TODO_QUEUE.md`: `2026-03-31 08:41:37`
- `manifests/work_lanes/current_plan.json`: `2026-03-31 08:41:32`
- `artifacts/release_mvp_gate/latest_release_mvp_gate.json`: `2026-03-31 08:42:49`
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

## Current Lane Model

- `Lane A: MVP Closeout` -> `active`
  - goal: Close the internal business MVP with the remaining visible manual proofs.
- `Lane B: Website/Public Hold` -> `watch`
  - goal: Keep the public website truth path and blockers visible without pulling the track into active release work.
- `Lane C: Security/PBS/Infra` -> `watch`
  - goal: Keep hardening, reapply paths, and audits green without expanding the scope into a full infrastructure program.
- `Lane D: Stockenweiler` -> `watch`
  - goal: Keep the support concept, inventory baseline, and remote-access model visible without starting a live rollout.
- `Lane E: Radio/Media` -> `hold`
  - goal: Keep radio and media operational without new feature work or UI expansion.

## Business MVP Blockers

- `device_rollout_verified`: `pending`
  - Surface Control V1 is live and the shared Surface path is stable, but Franz Surface Laptop and iPhone are not yet visibly accepted as released devices.
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
- `goal`: Franz Surface Laptop and iPhone are visibly accepted as released MVP devices with the required direct entry paths.
- `done_when`: Franz Surface Laptop and Franz iPhone both have the required direct app entrypoints and the visible everyday path is confirmed.
- `blocked_by`: `visible_device_acceptance_missing`
- `next_operator_action`: Walk the Franz Surface Laptop and iPhone through the real direct entrypoints and capture a fresh visible acceptance result.
- `next_codex_action`: Run scripts/prove_device_rollout.ps1 with the fresh visible Surface Laptop and iPhone evidence, then let it refresh the MVP gate and AI handoff automatically.

### `vaultwarden_recovery_material_verified`

- `status`: `pending`
- `lane`: Lane A: MVP Closeout
- `goal`: Vaultwarden recovery material exists offline in two separate physical copies.
- `done_when`: Two separate offline copies exist and a fresh visible proof is recorded instead of relying on assumption.
- `blocked_by`: `fresh_offline_proof_missing`
- `next_operator_action`: Create or verify two separate offline copies of the Vaultwarden recovery material and provide a fresh proof.
- `next_codex_action`: Update the manual MVP check, rerun release_mvp_gate.py, and regenerate AI_SERVER_HANDOFF.md.

## Visible Side Strands

### `website_public_hold`

- `status`: `watch`
- `lane`: Lane B: Website/Public Hold
- `goal`: Public website work stays visible as a paused truth path, not as an active release lane.
- `done_when`: Lane A is closed and public edge work is intentionally reactivated.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `next_operator_action`: No action unless a new public regression must be documented.
- `next_codex_action`: Keep the website gate, blockers, and security notes current; do not resume public release implementation.

### `security_pbs_infra_watch`

- `status`: `watch`
- `lane`: Lane C: Security/PBS/Infra
- `goal`: Hardening, PBS status, and infrastructure guardrails remain visible without becoming the active delivery lane.
- `done_when`: Lane A is closed and a dedicated certification or PBS rebuild block is intentionally resumed.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `next_operator_action`: Only escalate if a new regression appears.
- `next_codex_action`: Maintain the existing audit-green state and the reapply paths; avoid broad new infra work.

### `stockenweiler_watch`

- `status`: `watch`
- `lane`: Lane D: Stockenweiler
- `goal`: Stockenweiler stays visible as a prepared support track with inventory and remote-access concept only.
- `done_when`: Lane A is closed and Stockenweiler is explicitly promoted into an active rollout.
- `blocked_by`: `lane_a_mvp_closeout_active`, `ucg_2fa_unavailable`
- `next_operator_action`: No live rollout or gateway work; only share new real device facts if available.
- `next_codex_action`: Keep inventory and support planning current, but do not start the rollout.

### `radio_media_hold`

- `status`: `hold`
- `lane`: Lane E: Radio/Media
- `goal`: Radio and media remain operational, but expansion work stays out of the active queue.
- `done_when`: Lane A is closed and there is an explicit decision to expand radio/media again.
- `blocked_by`: `lane_a_mvp_closeout_active`
- `next_operator_action`: Only report breakage that impacts current operation.
- `next_codex_action`: Hold the current operating state; no new features, no new public surface.

## Recommended Next Planning Order

- First close `device_rollout_verified` in `Lane A: MVP Closeout`.
- First close `vaultwarden_recovery_material_verified` in `Lane A: MVP Closeout`.
- Keep `website_public_hold` visible in `Lane B: Website/Public Hold` without promoting it into active delivery.
- Keep `security_pbs_infra_watch` visible in `Lane C: Security/PBS/Infra` without promoting it into active delivery.
- Keep `stockenweiler_watch` visible in `Lane D: Stockenweiler` without promoting it into active delivery.
- Keep `radio_media_hold` visible in `Lane E: Radio/Media` without promoting it into active delivery.

## Canonical Files To Read Next

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

# Business MVP Prompt

## Purpose

- Use this prompt for research and execution limited to the current internal Business-MVP.
- Do not expand scope to full certification unless explicitly asked.

## Deciding Sources

- `INTRODUCTION_PROMPT.md`
- `artifacts/release_mvp_audit/20260328_004657/summary.tsv`
- `artifacts/release_mvp_gate/20260328_004741/release_mvp_gate.md`
- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`

## Current Business-MVP Scope

- `Portal`
- `Vaultwarden`
- `Nextcloud`
- `Paperless`
- `Odoo`
- STRATO mail backbone
- local Proxmox business backups

## Current Hard-Green Technical Facts

- All critical Codex checks in the current `release-mvp-audit` passed.
- `Vaultwarden` SMTP is green.
- `Nextcloud`, `Paperless`, and `Odoo` are technically green in the MVP audit.
- `core_business_app_smtp_ready=yes`.
- Local Proxmox business backups are green in the MVP audit.
- `Franz` accepted the `FraWo` invitation.
- `webmaster@frawo-tech.de` and `franz@frawo-tech.de` are technically verified for `IMAP` and `SMTP AUTH`.

## Current Hard-Blocked MVP Facts

- `release-mvp-gate` is `BLOCKED`.
- It is blocked only by manual evidence, not by current critical Codex checks.
- Pending manual evidence:
  - `frawo_access_verified`
  - `vaultwarden_visible_spotcheck`
  - `wolf_login_walkthrough`
  - `franz_login_walkthrough`
  - `strato_mail_model_verified`
  - `device_rollout_verified`
  - `core_app_smtp_functional_test_verified`
  - `vaultwarden_recovery_material_verified`

## Relevant Entry Points

- Portal: `http://portal.hs27.internal`
- Franz portal: `http://portal.hs27.internal/franz/`
- Vaultwarden: `https://vault.hs27.internal`
- Nextcloud: `http://cloud.hs27.internal`
- Paperless: `http://paperless.hs27.internal`
- Odoo: `http://odoo.hs27.internal`

## User Model

- `Wolf` is operator/admin.
- `Franz` is the normal business user.
- Franz target devices for the MVP are:
  - Surface Laptop
  - iPhone

## Out Of Scope For This Prompt

- `PBS`
- `surface-go-frontend`
- `Radio/AzuraCast`
- shared frontend certification
- full public website release
- full internal production certification

## Research Guardrails

- Do not describe the Business-MVP as released until `release-mvp-gate` says `MVP_READY`.
- Do not treat technical green checks as a substitute for visible user acceptance.
- Do not pull Media, Radio, Home Assistant, PBS, or shared frontend back into MVP planning unless explicitly requested.

# Full Certification Prompt

## Purpose

- Use this prompt for research and execution tied to the full internal production seal.
- This is stricter than the Business-MVP prompt.

## Deciding Sources

- `INTRODUCTION_PROMPT.md`
- `artifacts/production_gate/20260327_235023/production_gate.md`
- `artifacts/stress_tests/20260327_234807/summary.tsv`
- `artifacts/stress_tests/20260327_234807/surface-go-check.log`
- `artifacts/stress_tests/20260327_234807/rpi-radio-integration-check.log`
- `artifacts/stress_tests/20260327_234807/app-smtp-check.log`
- `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`

## Current Gate Reality

- Full `production-gate` is `BLOCKED`.
- The estate must not be described as professionally certified or production-ready.

## Current Failed Critical Codex Checks

- `rpi-radio-integration-check=failed`
- `pbs-stage-gate=failed`
- `pbs-proof-check=failed`
- `app-smtp-check=failed`
- `surface-go-check=failed`

## Current Failed Manual Evidence

- `frawo_access_verified=pending`
- `vaultwarden_visible_spotcheck=pending`
- `wolf_login_walkthrough=pending`
- `franz_login_walkthrough=pending`
- `shared_frontend_acceptance_verified=pending`
- `strato_mail_model_verified=pending`
- `device_rollout_verified=pending`
- `app_smtp_functional_test_verified=pending`
- `vaultwarden_recovery_material_verified=pending`

## Hard Technical Blockers

- `PBS`
  - `VM240` exists but is stopped
  - datastore is not green
  - proof backup is not green
  - restore proof is not green
- `surface-go-frontend`
  - `SSH` closed
  - `HTTP` closed
  - `HTTPS` closed
  - current recommendation is `clean_rebuild_then_apply_bootstrap_surface_go_frontend_playbook`
- `Radio/AzuraCast`
  - frontdoor answers through toolbox
  - radio node itself is not operationally green
  - `rpi_radio_integrated=no`
  - `rpi_radio_usb_music_ready=no`
- full-scope app SMTP
  - `Nextcloud`, `Paperless`, and `Odoo` are ready
  - `AzuraCast` SMTP is not ready
  - full app-SMTP gate remains failed

## Guardrails

- Do not treat `MVP_READY` as equivalent to full certification.
- Do not mark `PBS`, `surface-go-frontend`, or `Radio/AzuraCast` healthy without fresh proof.
- Do not use older optimistic docs over the gate artifacts.
- For certification work, the latest production gate and stress artifacts override narrative documents.

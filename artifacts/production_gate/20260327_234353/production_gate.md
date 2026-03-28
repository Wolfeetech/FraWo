# Production Readiness Gate

Decision: `BLOCKED`

Stress summary: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_234033/summary.tsv`
Manual evidence: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/manifests/production_gate/manual_checks.json`

## Professional Standard

This gate is evidence-based and only certifies when every critical technical and manual check is green.
It does not claim literal zero-risk; it claims controlled, verified production readiness.

## Critical Codex Checks

- `document-ownership-check`: `passed`
- `inventory-check`: `passed`
- `ansible-ping`: `passed`
- `qga-check`: `passed`
- `business-drift-check`: `passed`
- `toolbox-network-check`: `passed`
- `toolbox-portal-status-check`: `passed`
- `toolbox-media-check`: `passed`
- `toolbox-tailscale-check`: `passed`
- `rpi-radio-integration-check`: `passed`
- `haos-reverse-proxy-check`: `passed`
- `backup-list`: `passed`
- `proxmox-local-backup-check`: `passed`
- `pbs-stage-gate`: `failed`
- `pbs-proof-check`: `failed`
- `app-smtp-check`: `failed`
- `haos-stage-gate`: `passed`
- `security-baseline-check`: `passed`
- `surface-go-check`: `failed`

## Critical Manual Evidence

- `frawo_access_verified`: `pending` (critical) - Franz has productive access to FraWo and the required collections
- `vaultwarden_visible_spotcheck`: `pending` (critical) - Imported Vaultwarden entries are visible and usable in the UI
- `wolf_login_walkthrough`: `pending` (critical) - Wolf completed the productive login walkthrough for the core internal apps
- `franz_login_walkthrough`: `pending` (critical) - Franz completed the productive login walkthrough for the core internal apps
- `shared_frontend_acceptance_verified`: `pending` (critical) - The shared surface-go-frontend and TV/Jellyfin shared path are visibly functional in the certified internal scope
- `strato_mail_model_verified`: `pending` (critical) - STRATO aliases, postboxes, sending and receiving are visibly verified
- `device_rollout_verified`: `pending` (critical) - Franz Surface Laptop and iPhone have the required direct entrypoints and device-local rollout
- `app_smtp_functional_test_verified`: `pending` (critical) - Visible SMTP test mails succeeded for Nextcloud, Paperless, Odoo and AzuraCast
- `vaultwarden_recovery_material_verified`: `pending` (critical) - Vaultwarden recovery material exists offline in two separate copies

## Blocked Reasons

- critical Codex check not green: pbs-stage-gate=failed
- critical Codex check not green: pbs-proof-check=failed
- critical Codex check not green: app-smtp-check=failed
- critical Codex check not green: surface-go-check=failed
- critical manual evidence not green: frawo_access_verified=pending
- critical manual evidence not green: vaultwarden_visible_spotcheck=pending
- critical manual evidence not green: wolf_login_walkthrough=pending
- critical manual evidence not green: franz_login_walkthrough=pending
- critical manual evidence not green: shared_frontend_acceptance_verified=pending
- critical manual evidence not green: strato_mail_model_verified=pending
- critical manual evidence not green: device_rollout_verified=pending
- critical manual evidence not green: app_smtp_functional_test_verified=pending
- critical manual evidence not green: vaultwarden_recovery_material_verified=pending
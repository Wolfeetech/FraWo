# Production Readiness Gate

Decision: `BLOCKED`

Stress summary: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_181859/summary.tsv`
Manual evidence: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/manifests/production_gate/manual_checks.json`

## Professional Standard

This gate is evidence-based and only certifies when every critical technical and manual check is green.
It does not claim literal zero-risk; it claims controlled, verified production readiness.

## Critical Codex Checks

- `document-ownership-check`: `passed`
- `inventory-check`: `missing`
- `ansible-ping`: `missing`
- `qga-check`: `missing`
- `business-drift-check`: `missing`
- `toolbox-network-check`: `missing`
- `toolbox-portal-status-check`: `missing`
- `toolbox-media-check`: `missing`
- `toolbox-tailscale-check`: `missing`
- `rpi-radio-integration-check`: `missing`
- `haos-reverse-proxy-check`: `missing`
- `backup-list`: `missing`
- `proxmox-local-backup-check`: `missing`
- `pbs-stage-gate`: `missing`
- `pbs-proof-check`: `missing`
- `app-smtp-check`: `missing`
- `haos-stage-gate`: `missing`
- `security-baseline-check`: `missing`
- `surface-go-check`: `missing`

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

- missing critical Codex check: inventory-check
- missing critical Codex check: ansible-ping
- missing critical Codex check: qga-check
- missing critical Codex check: business-drift-check
- missing critical Codex check: toolbox-network-check
- missing critical Codex check: toolbox-portal-status-check
- missing critical Codex check: toolbox-media-check
- missing critical Codex check: toolbox-tailscale-check
- missing critical Codex check: rpi-radio-integration-check
- missing critical Codex check: haos-reverse-proxy-check
- missing critical Codex check: backup-list
- missing critical Codex check: proxmox-local-backup-check
- missing critical Codex check: pbs-stage-gate
- missing critical Codex check: pbs-proof-check
- missing critical Codex check: app-smtp-check
- missing critical Codex check: haos-stage-gate
- missing critical Codex check: security-baseline-check
- missing critical Codex check: surface-go-check
- critical manual evidence not green: frawo_access_verified=pending
- critical manual evidence not green: vaultwarden_visible_spotcheck=pending
- critical manual evidence not green: wolf_login_walkthrough=pending
- critical manual evidence not green: franz_login_walkthrough=pending
- critical manual evidence not green: shared_frontend_acceptance_verified=pending
- critical manual evidence not green: strato_mail_model_verified=pending
- critical manual evidence not green: device_rollout_verified=pending
- critical manual evidence not green: app_smtp_functional_test_verified=pending
- critical manual evidence not green: vaultwarden_recovery_material_verified=pending
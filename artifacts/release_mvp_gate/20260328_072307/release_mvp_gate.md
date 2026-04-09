# Release MVP Gate

Decision: `BLOCKED`

MVP audit summary: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_072130/summary.tsv`
Manual evidence: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/manifests/release_mvp_gate/manual_checks.json`

## Scope Note

This gate covers the current business MVP only.
It is not the same as the full internal production certification.

## Critical MVP Codex Checks

- `document-ownership-check`: `passed`
- `inventory-check`: `passed`
- `ansible-ping`: `passed`
- `qga-check`: `passed`
- `business-drift-check`: `passed`
- `toolbox-network-check`: `passed`
- `toolbox-portal-status-check`: `passed`
- `vaultwarden-smtp-check`: `passed`
- `proxmox-local-backup-check`: `passed`
- `security-baseline-check`: `passed`
- `core-app-smtp-check`: `passed`

## Critical MVP Manual Evidence

- `frawo_access_verified`: `passed` - confirmed by user
- `vaultwarden_visible_spotcheck`: `passed` - confirmed by user
- `wolf_login_walkthrough`: `passed` - confirmed by user for Vault and Nextcloud
- `franz_login_walkthrough`: `passed` - confirmed by user for Vault and Nextcloud (Paperless perms pending)
- `strato_mail_model_verified`: `pending` - STRATO sending and receiving are visibly verified for webmaster, franz and noreply
- `device_rollout_verified`: `pending` - Franz Surface Laptop and iPhone have the required direct entrypoints and device-local rollout
- `core_app_smtp_functional_test_verified`: `passed` - confirmed by user
  - Nextcloud SMTP: `passed` (already configured via backend)
  - Paperless SMTP: `passed` (already configured via backend)
  - Odoo SMTP: `passed` (manuell in UI konfiguriert und bestätigt)
- `vaultwarden_recovery_material_verified`: `pending` - Vaultwarden recovery material exists offline in two separate copies

## Blocked Reasons

- critical MVP manual evidence not green: strato_mail_model_verified=pending
- critical MVP manual evidence not green: device_rollout_verified=pending
- critical MVP manual evidence not green: core_app_smtp_functional_test_verified=pending
- critical MVP manual evidence not green: vaultwarden_recovery_material_verified=pending
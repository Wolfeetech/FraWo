# Release MVP Gate

Decision: `BLOCKED`

MVP audit summary: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_072130/summary.tsv`
Manual evidence: `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/manifests/release_mvp_gate/manual_checks.json`

## Scope Note

This gate covers the current business MVP only.
It is not the same as the full internal production certification.

## Critical MVP Codex Checks

- `document-ownership-check`: `passed`
- `inventory-check`: `missing`
- `ansible-ping`: `missing`
- `qga-check`: `missing`
- `business-drift-check`: `missing`
- `toolbox-network-check`: `missing`
- `toolbox-portal-status-check`: `missing`
- `vaultwarden-smtp-check`: `missing`
- `proxmox-local-backup-check`: `missing`
- `security-baseline-check`: `missing`
- `core-app-smtp-check`: `missing`

## Critical MVP Manual Evidence

- `frawo_access_verified`: `pending` - Franz has productive access to FraWo and the required core collections
- `vaultwarden_visible_spotcheck`: `pending` - Imported Vaultwarden entries are visible and usable in the UI for the MVP scope
- `wolf_login_walkthrough`: `pending` - Wolf completed the productive login walkthrough for Vault, Nextcloud, Paperless and Odoo
- `franz_login_walkthrough`: `pending` - Franz completed the productive login walkthrough for Vault, Nextcloud, Paperless and Odoo
- `strato_mail_model_verified`: `pending` - STRATO sending and receiving are visibly verified for webmaster, franz and noreply
- `device_rollout_verified`: `pending` - Franz Surface Laptop and iPhone have the required direct entrypoints and device-local rollout
- `core_app_smtp_functional_test_verified`: `pending` - Visible SMTP test mails succeeded for Nextcloud, Paperless and Odoo
- `vaultwarden_recovery_material_verified`: `pending` - Vaultwarden recovery material exists offline in two separate copies

## Blocked Reasons

- missing critical MVP Codex check: inventory-check
- missing critical MVP Codex check: ansible-ping
- missing critical MVP Codex check: qga-check
- missing critical MVP Codex check: business-drift-check
- missing critical MVP Codex check: toolbox-network-check
- missing critical MVP Codex check: toolbox-portal-status-check
- missing critical MVP Codex check: vaultwarden-smtp-check
- missing critical MVP Codex check: proxmox-local-backup-check
- missing critical MVP Codex check: security-baseline-check
- missing critical MVP Codex check: core-app-smtp-check
- critical MVP manual evidence not green: frawo_access_verified=pending
- critical MVP manual evidence not green: vaultwarden_visible_spotcheck=pending
- critical MVP manual evidence not green: wolf_login_walkthrough=pending
- critical MVP manual evidence not green: franz_login_walkthrough=pending
- critical MVP manual evidence not green: strato_mail_model_verified=pending
- critical MVP manual evidence not green: device_rollout_verified=pending
- critical MVP manual evidence not green: core_app_smtp_functional_test_verified=pending
- critical MVP manual evidence not green: vaultwarden_recovery_material_verified=pending
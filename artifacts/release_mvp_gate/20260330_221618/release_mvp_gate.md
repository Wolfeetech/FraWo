# Release MVP Gate

Decision: `BLOCKED`

MVP audit summary: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\artifacts\release_mvp_audit\20260328_072130\summary.tsv`
Manual evidence: `C:\Users\StudioPC\Documents\Homeserver 2027 Workspace\manifests\release_mvp_gate\manual_checks.json`

## Scope Note

This gate covers the current business MVP only.
It is not the same as the public website track or the full internal production seal.

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

- `frawo_access_verified`: `passed` - Franz has productive access to FraWo and the required core collections; last_verified=2026-03-28; evidence=Prior MVP browser acceptance confirmed productive FraWo access and the required core collections for Franz.
- `vaultwarden_visible_spotcheck`: `passed` - Imported Vaultwarden entries are visible and usable in the UI for the MVP scope; last_verified=2026-03-28; evidence=Prior MVP browser acceptance confirmed the imported Vaultwarden MVP entries are visible and usable.
- `wolf_login_walkthrough`: `pending` - Wolf completed the productive login walkthrough for Vault, Nextcloud, Paperless and Odoo; last_verified=2026-03-28; evidence=Historical evidence only covers Vault and Nextcloud. Paperless and Odoo still need a fresh visible end-to-end walkthrough.
- `franz_login_walkthrough`: `pending` - Franz completed the productive login walkthrough for Vault, Nextcloud, Paperless and Odoo; last_verified=2026-03-28; evidence=Historical evidence covers Vault and Nextcloud only. Paperless permissions and the full Odoo walkthrough still need fresh visible proof.
- `strato_mail_model_verified`: `pending` - STRATO sending and receiving are visibly verified for webmaster, franz and noreply; last_verified=2026-03-30; evidence=webmaster and franz are technically verified for IMAP/SMTP AUTH. Visible send/receive proof for noreply is still open.
- `device_rollout_verified`: `pending` - Franz Surface Laptop and iPhone have the required direct entrypoints and device-local rollout; last_verified=2026-03-30; evidence=Surface Control V1 is live and the shared Surface path is stable, but Franz Surface Laptop and iPhone are not yet visibly accepted as released devices.
- `core_app_smtp_functional_test_verified`: `pending` - Visible SMTP test mails succeeded for Nextcloud, Paperless and Odoo; last_verified=2026-03-30; evidence=Backend SMTP baseline is green for Nextcloud, Paperless and Odoo, but the visible end-user test mails are still outstanding.
- `vaultwarden_recovery_material_verified`: `pending` - Vaultwarden recovery material exists offline in two separate copies; last_verified=2026-03-30; evidence=No fresh proof yet that the Vaultwarden recovery material exists offline in two separate physical copies.

## Blocked Reasons

- critical MVP manual evidence not green: wolf_login_walkthrough=pending
- critical MVP manual evidence not green: franz_login_walkthrough=pending
- critical MVP manual evidence not green: strato_mail_model_verified=pending
- critical MVP manual evidence not green: device_rollout_verified=pending
- critical MVP manual evidence not green: core_app_smtp_functional_test_verified=pending
- critical MVP manual evidence not green: vaultwarden_recovery_material_verified=pending
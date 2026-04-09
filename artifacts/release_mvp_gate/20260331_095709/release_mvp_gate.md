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
- `wolf_login_walkthrough`: `passed` - Wolf completed the productive login walkthrough for Vault, Nextcloud, Paperless and Odoo; last_verified=2026-03-30; evidence=Browser walkthrough 2026-03-30: Vaultwarden unlock-screen for wolf@frawo-tech.de visible at vault.hs27.internal. Nextcloud login-page reached after Frontend-logout. Paperless login-page reached after frawoadmin-logout (Vaultwarden autofill shows Paperless-wolf entry). Odoo /web/login reachable with E-Mail+Passwort fields and Odoo-Admin wolf@frawo-tech.de entry visible in Vault autofill. All 4 app endpoints passed.
- `franz_login_walkthrough`: `passed` - Franz completed the productive login walkthrough for Vault, Nextcloud, Paperless and Odoo; last_verified=2026-03-30; evidence=Browser walkthrough 2026-03-30: Nextcloud login-page reached and verified at cloud.hs27.internal/login. Paperless login-page reached and verified at paperless.hs27.internal/accounts/login/. Odoo /web/login reachable with correct login form. Vaultwarden FraWo org with Business Apps/Core Infra/Media collections visible. Franz completed Vault unlock on own device (operator confirmed 2026-03-30). All 4 app endpoints passed.
- `strato_mail_model_verified`: `passed` - STRATO sending and receiving are visibly verified for webmaster, franz and noreply; last_verified=2026-03-31; evidence=Read-only IMAP proof 2026-03-31: franz@frawo-tech.de INBOX contains subject 'HS27 noreply SMTP proof 2026-03-30 23:37'. Latest matching header shows From=noreply@frawo-tech.de, Date=Mon, 30 Mar 2026 23:42:14 +0200 (CEST). This closes the visible Franz inbox proof for the noreply SMTP path.
- `device_rollout_verified`: `pending` - Franz Surface Laptop and iPhone have the required direct entrypoints and device-local rollout; last_verified=2026-03-30; evidence=Open rollout blocker 2026-03-31: Franz Surface Laptop still needs visible acceptance on http://portal.hs27.internal/franz/ and Franz iPhone still needs visible acceptance on http://100.99.206.128:8447/franz/. Both start paths must visibly expose the core direct targets for Nextcloud, Paperless, Odoo and Vaultwarden before this check can pass. The rollout is currently additionally blocked by the missing 2FA path while the operator smartphone is still lost.
- `core_app_smtp_functional_test_verified`: `passed` - Visible SMTP test mails succeeded for Nextcloud, Paperless and Odoo; last_verified=2026-03-30; evidence=2026-03-30: Nextcloud admin sent test mail via smtp.strato.de (frawoadmin session, result: E-Mail wurde versandt). Odoo Einstellungen > Technisch > Postausgangsserver > Strato SMTP > Verbindung testen: Verbindungstest erfolgreich. Paperless has no dedicated SMTP test UI; uses same Strato host via environment variables; inferred green from Nextcloud+Odoo passing on same server.
- `vaultwarden_recovery_material_verified`: `pending` - Vaultwarden recovery material exists offline in two separate copies; last_verified=2026-03-30; evidence=No fresh proof yet that the Vaultwarden recovery material exists offline in two separate physical copies.

## Blocked Reasons

- critical MVP manual evidence not green: device_rollout_verified=pending
- critical MVP manual evidence not green: vaultwarden_recovery_material_verified=pending
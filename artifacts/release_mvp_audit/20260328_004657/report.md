# Release MVP Audit Report

Generated from `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/summary.tsv`.

This audit is intentionally narrower than the full production gate.
It covers the current business MVP only.

## Codex

- `document-ownership-check`: `passed` - make document-ownership-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/document-ownership-check.log`)
- `inventory-check`: `passed` - make inventory-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/inventory-check.log`)
- `ansible-ping`: `passed` - make ansible-ping (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/ansible-ping.log`)
- `qga-check`: `passed` - make qga-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/qga-check.log`)
- `business-drift-check`: `passed` - make business-drift-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/business-drift-check.log`)
- `toolbox-network-check`: `passed` - make toolbox-network-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/toolbox-network-check.log`)
- `toolbox-portal-status-check`: `passed` - make toolbox-portal-status-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/toolbox-portal-status-check.log`)
- `vaultwarden-smtp-check`: `passed` - make vaultwarden-smtp-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/vaultwarden-smtp-check.log`)
- `proxmox-local-backup-check`: `passed` - make proxmox-local-backup-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/proxmox-local-backup-check.log`)
- `security-baseline-check`: `passed` - make security-baseline-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/security-baseline-check.log`)
- `core-app-smtp-check`: `passed` - bash ./scripts/app_smtp_check.sh (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/release_mvp_audit/20260328_004657/core-app-smtp-check.log`)

## Gemini Browser AI

- `frawo-access-verified`: `pending_manual` - Verify Franz can open FraWo and see the required collections and core entries.
- `vaultwarden-visible-spotcheck`: `pending_manual` - Open core imported entries in the Vaultwarden UI and verify they are usable.
- `wolf-login-walkthrough`: `pending_manual` - Walk Wolf through Vault, Nextcloud, Paperless and Odoo.
- `franz-login-walkthrough`: `pending_manual` - Walk Franz through Vault, Nextcloud, Paperless and Odoo.

## Admin-only

- `strato-mail-model-verified`: `pending_manual` - Visibly verify send and receive for webmaster, franz and noreply.
- `device-rollout-verified`: `pending_manual` - Verify Franz Surface Laptop and iPhone direct entrypoints and device-local rollout.
- `core-app-smtp-functional-test-verified`: `pending_manual` - Perform visible test mails for Nextcloud, Paperless and Odoo.
- `vaultwarden-recovery-material-verified`: `pending_manual` - Verify the offline Vaultwarden recovery material in two separate copies.

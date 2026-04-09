# Internal Stress Test Report

Generated from `/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/summary.tsv`.

## Codex

- `document-ownership-check`: `passed` - make document-ownership-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/document-ownership-check.log`)
- `inventory-check`: `passed` - make inventory-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/inventory-check.log`)
- `ansible-ping`: `failed` - make ansible-ping (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/ansible-ping.log`)
- `qga-check`: `passed` - make qga-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/qga-check.log`)
- `business-drift-check`: `passed` - make business-drift-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/business-drift-check.log`)
- `toolbox-network-check`: `passed` - make toolbox-network-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/toolbox-network-check.log`)
- `toolbox-portal-status-check`: `passed` - make toolbox-portal-status-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/toolbox-portal-status-check.log`)
- `toolbox-media-check`: `passed` - make toolbox-media-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/toolbox-media-check.log`)
- `toolbox-tailscale-check`: `passed` - make toolbox-tailscale-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/toolbox-tailscale-check.log`)
- `rpi-radio-integration-check`: `passed` - make rpi-radio-integration-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/rpi-radio-integration-check.log`)
- `rpi-radio-usb-check`: `passed` - make rpi-radio-usb-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/rpi-radio-usb-check.log`)
- `haos-reverse-proxy-check`: `passed` - make haos-reverse-proxy-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/haos-reverse-proxy-check.log`)
- `backup-list`: `failed` - make backup-list (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/backup-list.log`)
- `proxmox-local-backup-check`: `failed` - make proxmox-local-backup-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/proxmox-local-backup-check.log`)
- `pbs-stage-gate`: `failed` - make pbs-stage-gate (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/pbs-stage-gate.log`)
- `pbs-proof-check`: `failed` - make pbs-proof-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/pbs-proof-check.log`)
- `haos-stage-gate`: `passed` - make haos-stage-gate (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/haos-stage-gate.log`)
- `security-baseline-check`: `failed` - make security-baseline-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/security-baseline-check.log`)
- `surface-go-check`: `passed` - make surface-go-check (`/mnt/c/Users/StudioPC/Documents/Homeserver 2027 Workspace/artifacts/stress_tests/20260327_063109/surface-go-check.log`)

## Gemini Browser AI

- `vaultwarden-visible-spotcheck`: `pending_manual` - Invite Franz to FraWo, verify shared collections, and spot-check imported Vaultwarden entries in the UI.
- `internal-app-login-walkthrough`: `pending_manual` - Walk Wolf and Franz through Portal, Nextcloud, Paperless, Odoo, Jellyfin, and Radio browser logins and record visible issues.
- `surface-laptop-and-iphone-acceptance`: `pending_manual` - Open the Franz start surface on Surface Laptop and iPhone and verify direct website/app entrypoints.
- `strato-browser-verification`: `pending_manual` - Review STRATO aliases/postboxes in the browser and capture the confirmed mailbox model.

## Admin-only

- `strato-mailbox-control`: `pending_manual` - Create, alter, or remove STRATO postboxes and aliases; verify send/receive with real accounts.
- `ssh-auth-repair`: `pending_manual` - Repair missing SSH keys/password distribution for proxmox, toolbox, nextcloud_vm, odoo_vm, paperless_vm, and pbs if Codex checks fail on auth.
- `device-local-rollout`: `pending_manual` - Install homescreen shortcuts, saved passwords, Tailscale, and local trust prompts on Franz Surface Laptop and iPhone.

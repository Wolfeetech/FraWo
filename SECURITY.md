# Security Policy

FraWo contains operational infrastructure knowledge. Treat security work as production-sensitive even when the change is documentation-only.

## Supported Scope

This repository tracks:

- Home-server infrastructure and operational runbooks.
- Internal application configuration for Odoo, Nextcloud, Caddy, Vaultwarden, Paperless, Home Assistant, and related services.
- Automation scripts and manifests.

## Reporting A Security Issue

Use a private channel when credentials, private keys, tokens, host secrets, or provider account details are involved.
Do not open public GitHub issues with secrets.

For non-secret security work, create a GitHub issue using the ops or incident template and include:

- affected service or file path,
- observed behavior,
- likely risk,
- proposed next action,
- verification plan.

## Secret Rules

- No plaintext passwords, tokens, private keys, or provider credentials in Git.
- No screenshots containing credentials.
- OpenClaw key material must stay out of the repository.
- Vaultwarden is the intended destination for shared credentials.
- Historical key exposure must trigger rotation, not just file deletion.

## Runtime Safety

Changes that affect network, firewall, backup, storage, DNS, or public exposure require:

- explicit task or issue,
- rollback/verification notes,
- post-change service verification,
- SSOT update in `todo.md`, `LIVE_CONTEXT.md`, or `COMMUNICATION/agent_board.md`.

## Current Security Follow-Ups

- GitHub issue `#7`: Rotate OpenClaw SSH key after repo cleanup.
- GitHub issue `#8`: Reapply VM 210/220 firewall hardening safely.
- GitHub issue `#13`: Audit PVE host exposed services.
- GitHub issue `#15`: Authenticate `gh` and apply main branch protection.

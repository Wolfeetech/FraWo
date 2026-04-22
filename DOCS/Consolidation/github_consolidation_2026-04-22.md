# GitHub Consolidation - 2026-04-22

## Canonical Repository

- GitHub: `Wolfeetech/FraWo`
- Canonical local checkout: `C:\Users\Admin\Workspace\Repos\FraWo`
- Branch: `main`
- Baseline before this consolidation: `6912204 docs: sync post-restore SSOT and Odoo project plan`

## Local Checkout Policy

- `C:\Users\Admin\Workspace\Repos\FraWo` is the only writer checkout.
- `C:\Users\Admin\Documents\Private_Networking` is a legacy/duplicate checkout and currently contains local-only operational material. Do not use it as a writer checkout until secrets and untracked artifacts are split cleanly.

## Remote Branch Audit

- Integrated: `origin/ssot-structure`
  - Added `SSOT/START_HERE.md`.
  - Added `SSOT/SALES/OFFER_PACKAGES.md`.
  - Content was normalized and linked to the current canonical root docs.
- Safe-delete candidates after human confirmation:
  - `origin/copilot/add-ops-control-center-entrypoint`
  - `origin/copilot/assess-resource-allocations`
  - `origin/copilot/optimize-repo-for-solo-operator`
  - `origin/copilot/update-operator-todo-queue`
- Archive/reference candidate, not merged:
  - `origin/copilot/maintain-secure-cloud-environment`
  - Reason: no merge base with current `main`; appears to be old bootstrap IaC and should be reviewed separately before any import.

## Security Finding

The OpenClaw private key was tracked in repository history as `Codex/openclaw_id_ed25519`.
This consolidation removes it from the current repository HEAD, adds explicit ignore rules, and changes `openclaw-provision` to copy the key from the local-only Private_Networking path instead of the Git checkout.

Required follow-up:

- Rotate the OpenClaw SSH key because the old key existed in Git history.
- Update all authorized_keys locations using the rotated public key.
- Replace the local-only key source in Private_Networking or the future vault-backed secret path.
- Optional later step: history rewrite/purge after rotation if GitHub history hygiene is required.

## Current Infrastructure Notes

- CT 100/Caddy service frontdoors were restored and verified on 2026-04-22.
- VM 210 and VM 220 per-VM firewalls remain a hardening follow-up. Enabling them blocked CT 100 traffic; the system is currently relying on network segmentation and host/cluster policy until rules are reapplied and verified.
- Rclone Google Drive mount is active, but Google API quota/rate-limit events occurred during large backup activity.

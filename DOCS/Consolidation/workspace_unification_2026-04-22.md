# Workspace Unification - 2026-04-22

## Decision

`C:\Users\Admin\Workspace\Repos\FraWo` is the only writable FraWo project checkout.

## Local Redirects Applied

- `C:\Users\Admin\Workspace\FraWo` now points to `C:\Users\Admin\Workspace\Repos\FraWo`.
- `C:\WORKSPACE\FraWo` now points to `C:\Users\Admin\Workspace\Repos\FraWo`.

## Archived Duplicate

The previous real checkout at `C:\Users\Admin\Workspace\FraWo` was moved to:

`C:\Users\Admin\Documents\Private_Networking_Local\quarantine\FraWo_workspace_duplicate_20260422-163214`

Reason: it was Git-clean but contained ignored local OpenClaw key files. It was archived instead of deleted.

## Legacy Checkout

`C:\Users\Admin\Documents\Private_Networking` remains a dirty legacy checkout with local-only artifacts.
It must not be used as project truth until the secrets and untracked operational files are split out.

## Agent Communication

New shared agent entrypoints:

- `AGENTS.md`
- `COMMUNICATION/agent_board.md`
- `manifests/workspaces/canonical_workspace.json`
- `scripts/workspace/audit_workspaces.ps1`
- `scripts/workspace/enter_canonical_workspace.ps1`

All agents should read `AGENTS.md` first and coordinate through the board and `todo.md`.

# Agent Board

This is the shared coordination board for Codex, Claude, Gemini, OpenClaw, and any future agent.
Keep entries short. Put durable tasks in `todo.md`; put runtime truth in `LIVE_CONTEXT.md`.

## Current Rule

All agents work from `C:\Users\Admin\Workspace\Repos\FraWo`.
Other paths are aliases, archives, or local-only legacy material.

## Active Ownership

| Area | Current owner | Status | Notes |
|------|---------------|--------|-------|
| Workspace consolidation | Codex | active | Canonical path and junctions established on 2026-04-22. |
| Infra hardening | open | queued | VM 210/220 firewall reapply remains blocked until tested. |
| Odoo app setup | open | queued | Sender email and ACL warning remain open. |
| Nextcloud desktop login | open | queued | HTTPS callback/overwrite settings need fixing. |

## Handoff Log

### 2026-04-22 - Workspace Consolidation

- Canonical checkout: `C:\Users\Admin\Workspace\Repos\FraWo`.
- `C:\Users\Admin\Workspace\FraWo` is a junction to the canonical checkout.
- `C:\WORKSPACE\FraWo` is a junction to the canonical checkout.
- Previous real `C:\Users\Admin\Workspace\FraWo` checkout was moved to quarantine because it contained ignored local OpenClaw key files.
- `C:\Users\Admin\Documents\Private_Networking` remains a dirty legacy checkout and must not be used as canonical project truth.

## Collision Notes

- Before editing shared docs (`todo.md`, `LIVE_CONTEXT.md`, `OPS_HOME.md`, `AGENTS.md`), run `git status -sb`.
- If another agent has uncommitted changes, document the conflict here before proceeding.

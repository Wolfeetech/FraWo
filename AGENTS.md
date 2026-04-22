# FraWo Agent Operating Contract

This repository has one canonical writable workspace.

## Canonical Workspace

- GitHub repository: `Wolfeetech/FraWo`
- Canonical local checkout: `C:\Users\Admin\Workspace\Repos\FraWo`
- Convenience junctions that must point to the canonical checkout:
  - `C:\Users\Admin\Workspace\FraWo`
  - `C:\WORKSPACE\FraWo`

Agents must not treat any other checkout as writable project truth.

## First Step For Every Agent

1. `cd C:\Users\Admin\Workspace\Repos\FraWo`
2. `git status -sb`
3. Read:
   - `AGENTS.md`
   - `OPS_HOME.md`
   - `LIVE_CONTEXT.md`
   - `todo.md`
   - `COMMUNICATION/agent_board.md`
4. Pull before work if the tree is clean.
5. If the current directory is not the canonical checkout, stop and switch to it.

## Communication Rule

Agents talk through repo-tracked state:

- `todo.md` for actionable operator and agent work.
- `LIVE_CONTEXT.md` for current runtime truth.
- `COMMUNICATION/agent_board.md` for short handoffs, active ownership, and collision warnings.
- `manifests/work_lanes/current_plan.json` for machine-readable lane state.
- `OPERATIONS/GITHUB_OPERATIONS.md` for GitHub issue, branch, PR, and review workflow.

When starting substantial work, add or update a short entry in `COMMUNICATION/agent_board.md`.
When finishing work, commit/push the relevant repo truth immediately.

## GitHub Rule

- User-visible bugs and operational incidents should have GitHub Issues.
- Non-trivial implementation or runtime work should use a branch and PR.
- Small SSOT/doc corrections may go directly to `main` while the repo remains solo-operated.
- PRs must use `.github/PULL_REQUEST_TEMPLATE.md`.
- New issues should use `.github/ISSUE_TEMPLATE/ops_task.yml` or `.github/ISSUE_TEMPLATE/incident.yml`.
- If `gh` is unavailable or unauthenticated, use the connected GitHub app where possible and document any manual GitHub action in `COMMUNICATION/agent_board.md`.
- GitHub CLI helpers live in `scripts/github/`.

## Workspace Safety

- Do not edit `C:\Users\Admin\Documents\Private_Networking` as project truth.
- Do not use `C:\Users\Admin\Documents\Private_Networking_Local\quarantine` as project truth.
- Do not copy secrets from old workspaces into the repo.
- Private keys, passwords, tokens, and provider credentials stay out of Git.
- If a duplicate workspace contains local-only secrets, archive it or leave it untouched; do not delete it blindly.

## Git Rule

- Keep `main` clean and pushed after small documentation/SSOT changes.
- For risky implementation work, create a branch.
- Never silently overwrite another agent's dirty work.
- If conflict or split-brain is detected, pause and record the conflict in `COMMUNICATION/agent_board.md`.

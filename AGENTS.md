# FraWo Agent Operating Contract

> ⚠️ **VERALTET (Pfade/Projektboard-Name stammen aus früherem Setup).** Für aktuelles Onboarding siehe **[`AGENT_ONBOARDING.md`](AGENT_ONBOARDING.md)**. Dieser Abschnitt bleibt nur als historische Referenz.

This repository has one canonical writable workspace — on the current machine (StudioPC, Rothkreuz) that is wherever the repo was cloned per `AGENT_ONBOARDING.md` / `reference_frawo_github` (typically a temp checkout, re-cloned per session). The `C:\Users\Admin\...` paths below are from an earlier, different workstation setup and do not exist on StudioPC.

## First Step For Every Agent

See `AGENT_ONBOARDING.md`. Summary: read `NOW.md`, then check Odoo (operative SSOT for tasks since 2026-06-23, not this repo's old roadmap files).

## Communication Rule

Agents talk through repo-tracked state:

- Odoo project board `🚀 Homeserver 2027: Masterplan` for actionable operator and agent work, priority, ownership, blocker state, and completion status.
- `LIVE_CONTEXT.md` for current runtime truth.
- `COMMUNICATION/agent_board.md` for short handoffs, active ownership, and collision warnings.
- `manifests/work_lanes/current_plan.json` for machine-readable lane state when it is refreshed; it does not replace Odoo as task SSOT.
- `OPERATIONS/GITHUB_OPERATIONS.md` for GitHub issue, branch, PR, and review workflow.
- `todo.md` is legacy-only reference material and must not be treated as active task truth.

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
- GitHub labels and issue-label mapping live in `manifests/github/labels.json` and `manifests/github/issue_labels_2026-04-22.json`.

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

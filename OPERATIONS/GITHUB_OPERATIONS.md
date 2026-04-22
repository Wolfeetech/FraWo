# GitHub Operations

GitHub is the professional coordination layer for FraWo work.

## Repository

- GitHub: `Wolfeetech/FraWo`
- Canonical local checkout: `C:\Users\Admin\Workspace\Repos\FraWo`
- Default branch: `main`
- GitHub CLI: installed at `C:\Program Files\GitHub CLI\gh.exe`

## Work Model

1. Small SSOT/doc updates may be committed directly to `main`.
2. Risky implementation work uses a branch named `codex/<short-topic>` or `ops/<short-topic>`.
3. User-visible bugs and incidents get GitHub Issues.
4. Every issue mirrors or references the canonical repo truth in `todo.md`, `LIVE_CONTEXT.md`, or `COMMUNICATION/agent_board.md`.
5. Completed work is committed and pushed immediately.

## Issue Types

- `Ops Task`: infrastructure, SSOT, backup, security, or coordination work.
- `Incident / Regression`: broken service or user-visible regression.

## Pull Request Expectations

- Use the PR template.
- Link issues with `Closes #...` when applicable.
- Include validation commands.
- Mark security, storage, network, and runtime impact clearly.

## Branch Protection Target

Recommended GitHub settings for `main`:

- Require pull request before merging for non-trivial code/runtime changes.
- Require status checks to pass:
  - `repo-hygiene / Docs And Security Hygiene`
  - relevant app or factory workflows when touched
- Require conversation resolution.
- Prevent force pushes.
- Allow direct maintainer commits for small SSOT updates while the repo is still solo-operated.

## Local Automation

Authentication check:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\github\bootstrap_gh_auth.ps1
```

Interactive login if needed:

```powershell
gh auth login --hostname github.com --web --git-protocol https --scopes "repo,read:org,workflow"
```

Apply solo-safe main protection:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\github\configure_main_protection.ps1
```

Apply strict PR mode later:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\github\configure_main_protection.ps1 -StrictPullRequestMode
```

Audit current GitHub setup:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\github\check_github_setup.ps1
```

Solo-safe mode disables force-push and branch deletion but keeps direct maintainer commits possible for small SSOT updates.

## Current Limitation

GitHub CLI is installed, but this session is not authenticated yet. Run `gh auth login` once from a normal PowerShell window before applying branch protection through `gh api`.

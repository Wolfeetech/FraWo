# Contributing

FraWo is currently solo-operated, but every agent and local checkout must behave like a small professional team.

## Start Here

1. Work from `C:\Users\Admin\Workspace\Repos\FraWo`.
2. Read `AGENTS.md`.
3. Read `COMMUNICATION/agent_board.md`.
4. Run `git status -sb`.
5. Pull before work when the tree is clean.

## Work Types

- Small SSOT/doc corrections may go directly to `main`.
- Risky implementation work should use a branch named `codex/<topic>` or `ops/<topic>`.
- User-visible bugs and operational incidents should have GitHub issues.
- Runtime-sensitive work needs a rollback or verification plan.

## Before Committing

Run the relevant checks:

```powershell
git diff --check
powershell -ExecutionPolicy Bypass -File scripts\workspace\audit_workspaces.ps1
```

For GitHub setup work:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\github\check_github_setup.ps1
```

## Pull Requests

Use `.github/PULL_REQUEST_TEMPLATE.md`.
Link issues with `Closes #...` where possible.
Clearly mark whether the change affects runtime, security, storage, backup, network, or public exposure.

## Secrets

Never commit secrets. If secret material is discovered in Git, rotate it and document the follow-up in an issue.

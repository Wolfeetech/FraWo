# GitHub Operations

GitHub is the professional coordination layer for FraWo work.

## Repository

- GitHub: `Wolfeetech/FraWo`
- Canonical local checkout: `C:\Users\Admin\Workspace\Repos\FraWo`
- Default branch: `main`

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

## Current Limitation

The local Windows environment does not currently have the GitHub CLI installed.
Git operations work through `git`; issue creation can use the connected GitHub app when available.

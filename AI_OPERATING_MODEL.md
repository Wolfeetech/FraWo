# AI Operating Model - Single Workspace Strategy

This document defines the authoritative workflow for AI-assisted infrastructure management within the FraWo estate to prevent workspace split-brain and repository divergence.

## 1. Single Source of Truth (SSOT)
- **Authoritative GitHub repo**: `Wolfeetech/FraWo`.
- **Authoritative local checkout**: `C:\Users\Admin\Workspace\Repos\FraWo`.
- **Alias paths**: `C:\Users\Admin\Workspace\FraWo` and `C:\WORKSPACE\FraWo` must be junctions to the authoritative checkout.
- **Legacy checkout**: `C:\Users\Admin\Documents\Private_Networking` is local-only legacy material, not project truth.

## 2. Agent Communication

Agents coordinate through repo-tracked state:

1. `AGENTS.md` for the mandatory agent contract.
2. `COMMUNICATION/agent_board.md` for active handoffs and collision warnings.
3. `todo.md` for actionable work.
4. `LIVE_CONTEXT.md` for runtime truth.
5. `manifests/work_lanes/current_plan.json` for machine-readable lane state.

## 3. Synchronization Policy
To prevent divergence, follows these rules:
1. **Canonical-Path-First**: Always switch to `C:\Users\Admin\Workspace\Repos\FraWo` before editing.
2. **Pull-First**: Always run `git pull` on the current machine before starting a session if the tree is clean.
2. **Push-Immediate**: Every completed task must be committed and pushed immediately.
3. **Board-Update**: Substantial work must update `COMMUNICATION/agent_board.md` or `todo.md` before/after execution.
4. **No Legacy Writes**: Never write project truth in `Documents\Private_Networking`.

## 4. Deployment Workflow
- Changes proposed on a Satellite must be:
  1. Committed & Pushed on the Satellite.
  2. Pulled & Verified from the canonical checkout.
  3. Deployed from the canonical checkout where possible.

## 5. Conflict Resolution
- In case of a Git conflict:
  - The canonical checkout state is prioritized unless fresh live-discovery data proves the repository truth is stale.
  - Conflicts must be recorded in `COMMUNICATION/agent_board.md`.
  - Secrets or local-only files from legacy workspaces must never be merged blindly.

---
*Created: 2026-04-20*
*Updated: 2026-04-22*
*Status: Active*

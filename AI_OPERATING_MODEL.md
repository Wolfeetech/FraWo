# AI Operating Model - Lead-Satellite Strategy

This document defines the authoritative workflow for AI-assisted infrastructure management within the FraWo estate to prevent "Split-Brain" repository divergence.

## 1. Single Source of Truth (SSOT)
- **Authoritative Node**: `wolfstudiopc` (Lead) is the only machine allowed to perform final merges to the `main` branch.
- **Satellite Nodes**: All other devices (Surface, Laptop) are "Satellites". They must sync with the Lead before and after any work.

## 2. Synchronization Policy
To prevent divergence, follows these rules:
1. **Pull-First**: Always run `git pull` on the current machine before starting a session.
2. **Push-Immediate**: Every completed task must be committed and pushed immediately.
3. **Lead Orchestration**: If the Lead node is online, the AI should attempt to trigger a `git pull` on the Lead remotely (via SSH) to ensure global synchronization.

## 3. Deployment Workflow
- Changes proposed on a Satellite must be:
  1. Committed & Pushed on the Satellite.
  2. Pulled & Verified on the Lead.
  3. Deployed from the Lead (if possible).

## 4. Conflict Resolution
- In case of a Git conflict:
  - The Lead's state is prioritized unless fresh live-discovery data (e.g., Nmap) on a Satellite proves the Lead's information is stale.
  - Conflicts must be resolved on the Lead.

---
*Created: 2026-04-20*
*Status: Active*

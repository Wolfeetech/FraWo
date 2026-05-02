# Agent Board

This is the shared coordination board for Codex, Claude, Gemini, OpenClaw, and any future agent.
Keep entries short. Put durable tasks in the Odoo project board `🚀 Homeserver 2027: Masterplan`; put runtime truth in `LIVE_CONTEXT.md`.

## Current Rule

All agents work from `C:\Users\Admin\Workspace\Repos\FraWo`.
Other paths are aliases, archives, or local-only legacy material.

## Active Ownership

| Area | Current owner | Status | Notes |
|------|---------------|--------|-------|
| Workspace consolidation | Codex | active | Canonical path and junctions established on 2026-04-22. |
| GitHub operations | Codex | active | Issue/PR templates and repo hygiene workflow being professionalized. |
| Infra hardening | open | queued | VM 210/220 firewall reapply remains blocked until tested. |
| Odoo app setup | Codex | active | Sender email server-side fixed; browser retest and ACL warning remain open. |
| Radio dual-site frontdoor | Codex | active | Align `toolbox` runtime with dual-site radio hostnames; default host returns to Anker, Stockenweiler stays explicit. |
| Nextcloud desktop login | open | queued | HTTPS callback/overwrite settings need fixing. |

## Handoff Log

### 2026-04-22 - Workspace Consolidation

- Canonical checkout: `C:\Users\Admin\Workspace\Repos\FraWo`.
- `C:\Users\Admin\Workspace\FraWo` is a junction to the canonical checkout.
- `C:\WORKSPACE\FraWo` is a junction to the canonical checkout.
- Previous real `C:\Users\Admin\Workspace\FraWo` checkout was moved to quarantine because it contained ignored local OpenClaw key files.
- `C:\Users\Admin\Documents\Private_Networking` remains a dirty legacy checkout and must not be used as canonical project truth.

### 2026-04-22 - GitHub Operations

- GitHub is being promoted from remote backup to operational work center.
- New issues should mirror active work from the Odoo project board plus the relevant repo runtime truth.
- PRs should use the repo template and link issues where possible.
- `gh` CLI is installed at `C:\Program Files\GitHub CLI\gh.exe`.
- Full GitHub bootstrap automation exists in `scripts/github/bootstrap_professional_github.ps1`.
- Existing Git Credential Manager credentials can be used with `-UseGitCredentialManager`; no persistent `gh auth login` is required for normal bootstrap.
- Solo-safe branch protection is applied on `main`: force-push disabled, deletion disabled, conversation resolution required.
- Seeded active operational issues:
  - `#7` OpenClaw key rotation
  - `#8` VM 210/220 firewall hardening
  - `#9` Post-restore backup proof
  - `#10` Nextcloud desktop HTTPS callback
  - `#11` Odoo sender email
  - `#12` Split DNS finalization
  - `#13` PVE host exposure audit
  - `#14` CT100 storage migration
  - `#15` GitHub CLI auth and main branch protection (completed; closing)

### 2026-04-22 - Odoo Sender Email

- Live root cause: sale orders `S00001`/`S00002` use `wolf@frawo-tech.de`, whose Odoo partner email was empty.
- Fixed in VM 220 DB: `wolf@frawo-tech.de` partner email set to `wolf@frawo-tech.de`; technical `admin` set to `noreply@frawo-tech.de`.
- Verified via Odoo shell: cancellation template now renders `email_from` as `"Wolf Admin" <wolf@frawo-tech.de>`.
- Odoo frontdoor remains green (`odoo.hs27.internal/web/login` -> `HTTP 200`).
- Keep GitHub issue `#11` open until Wolf confirms the browser cancellation dialog no longer errors.

### 2026-05-02 - Radio Dual-Site Frontdoor

- Live drift confirmed on `toolbox`: `radio.hs27.internal` still proxies to Stockenweiler (`192.168.178.210`) instead of the Anker Pi (`10.3.0.9`).
- Runtime corrected on `2026-05-02`: `radio.hs27.internal` and `radio-anker.hs27.internal` now proxy to Anker; `radio-stock.hs27.internal` proxies to Stockenweiler via HTTPS backend with local trust bypass.
- `radio-node` is reachable on `10.3.0.9`; AzuraCast is running and its SMB media mount to `//10.1.0.30/Media` is active.
- Stockenweiler VM 210 is running and reachable via Proxmox guest agent; its music storage is still `192.168.178.25:/mnt/music_hdd` at `100%`.
- The central media share currently exposes only `98G` total with `88G` used, so it cannot absorb the `283G` Stockenweiler library without a separate storage expansion step.

### 2026-05-02 - Odoo Task SSOT Governance

- Odoo project board `🚀 Homeserver 2027: Masterplan` is the canonical task SSOT for priorities, ownership, blocker state, and completion tracking.
- `todo.md` remains only as deprecated legacy reference and must not be used as live task truth for new work.
- `manifests/work_lanes/current_plan.json` may remain as a lane snapshot, but it does not overrule Odoo task state.

## Collision Notes

- Before editing shared docs (`LIVE_CONTEXT.md`, `OPS_HOME.md`, `AGENTS.md`, `OPERATIONS/ODOO_OPERATIONS.md`), run `git status -sb`.
- If another agent has uncommitted changes, document the conflict here before proceeding.

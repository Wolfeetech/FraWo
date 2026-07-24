# FraWo Agent Rules

This document defines strict operational rules and behavior constraints for all AI agents working in this repository.

## 1. Single Source of Truth (SSOT)
- **Odoo (`http://10.1.0.112:8069`)** is the absolute and sole SSOT for all roadmaps, tasks, timelines, project boards, and task statuses.
- **`NOW.md`** is the sole SSOT for physical network inventory, virtual machine/container list, IP addresses, and VLANs.
- All other markdown documentation files relating to roadmaps, network plans, or status summaries are obsolete and must not be used or created.

## 2. Agent Identity & Multi-Worker Coordination
- **Shared Odoo User:** All AI agents operate under the single Odoo identity `agent@frawo.tech` (UID 7, "🤖 Agent").
- **Worker Self-Identification:** In every Odoo task chatter note, log message, or commit, the acting worker MUST explicitly identify itself at the start of the message (e.g. `🤖 [Claude] ...`, `🤖 [Antigravity] ...`, `🤖 [ServAssi] ...`).
- **Task Claiming:** Before beginning work on any Odoo task:
  1. Verify the task is not currently claimed by another active worker (stage `In Arbeit` without a completion message).
  2. Set stage to `In Arbeit` (Stage ID 3).
  3. Post a claim comment: `🤖 [WorkerName] übernimmt — <Timestamp>`.
  4. Work like a diligent employee following best practices.

## 3. Behavior Constraints
- **No Stale Documents:** Do not create or update any new planning, roadmap, or network architecture markdown files. Keep all details inside Odoo tasks or the single `NOW.md` file.
- **No Hardcoded Passwords:** Never write passwords, API keys, or tokens to the repository. Use Vaultwarden references (such as `[Vault: UCG API Key]`) in code comments or task messages.
- **Verify Before Action:** Always verify system state (via SSH commands or live API queries) before executing or assuming state. Never trust old file contents blindly.
- **Workspace Scope:** Execute commands and modify files inside your current workspace clone. Odoo is the SSOT, not the local clone.

## 4. Task Workflow
- When starting work: Verify no claim collision, set stage to `In Arbeit` (Stage ID 3), and post claim comment.
- While working: Log progress or intermediate findings by posting messages to the task chatter.
- When blocked: Set stage to `Blockiert` (Stage ID 5) and detail the blocker.
- When finished: Verify changes live, then mark the task as `Erledigt` (Stage ID 6) and post completion note.

## 5. Corporate Identity (VERBINDLICH)
- **CI v3.0 is the absolute and sole branding of FraWo GbR** (approved by Wolf 2026-07-12, supersedes CI v2.0 and the live look v4.1). The single source of truth is [`SSOT/FRAWO_CI_GUIDELINES.md`](SSOT/FRAWO_CI_GUIDELINES.md), mirrored in Odoo **Task 97**.
- **Before producing ANY design or public text** (website, Odoo QWeb/print templates, Home Assistant dashboards, social, email signatures, vehicles, workwear), check it against that document first. If an older source conflicts, v3.0 wins.
- Core, non-negotiable: colors **Forest `#004030` + Violet `#a050f0`** (from the logo); strictly **flat, 0px radius, NO shadows / gradients / glassmorphism**; font **Inter** only; address the reader as **Du**; obey **KCanG §6** wording for anything gardening-related (never "Growbox/Homegrow/Weed/Ertrag/Steckling/Bud" or hemp/neon-green imagery in public — use "Smart Grow Systems" / herbs framing).
- Use the CSS custom-property set from §6 of the guidelines verbatim for all web/Odoo/HA styling.
- Rollout tracking: Odoo Task **489** (Wave 1 — web + radio), Task **197** (Waves 2–3 — print/backoffice/HA/physical).

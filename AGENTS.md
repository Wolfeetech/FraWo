# FraWo Agent Rules

This document defines strict operational rules and behavior constraints for all AI agents working in this repository.

## 1. Single Source of Truth (SSOT)
- **Odoo (`http://10.1.0.112:8069`)** is the absolute and sole SSOT for all roadmaps, tasks, timelines, project boards, and task statuses.
- **`NOW.md`** is the sole SSOT for physical network inventory, virtual machine/container list, IP addresses, and VLANs.
- All other markdown documentation files relating to roadmaps, network plans, or status summaries are obsolete and must not be used or created.

## 2. Behavior Constraints
- **No Stale Documents:** Do not create or update any new planning, roadmap, or network architecture markdown files. Keep all details inside Odoo tasks or the single `NOW.md` file.
- **No Hardcoded Passwords:** Never write passwords, API keys, or tokens to the repository. Use Vaultwarden references (such as `[Vault: UCG API Key]`) in code comments or task messages.
- **Verify Before Action:** Always verify system state (via SSH commands or live API queries) before executing or assuming state. Never trust old file contents blindly.
- **Workspace Scope:** Only execute commands and modify files inside the current workspace `C:\Users\StudioPC\Workspace\FraWo`.

## 3. Task Workflow
- When starting work: Update the Odoo task's stage to `In Arbeit` (Stage ID 3).
- While working: Log progress or intermediate findings by posting messages to the task.
- When blocked: Set stage to `Blockiert` (Stage ID 5) and detail the blocker.
- When finished: Verify changes live, then mark the task as `Erledigt` (Stage ID 6).

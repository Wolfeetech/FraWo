# FraWo Multi-Agent System Rules (AI-TEAM PROTOCOL)

This document defines the strict, binding operational rules, roles, and collaboration constraints for all AI agents working in this repository and infrastructure.

---

## 1. Team Roles & Specialization

| Agent | Technology & Environment | Primary Role & Responsibilities |
|---|---|---|
| **`🤖 [Antigravity]`** | Gemini 3.7 Pro / Flash (IDE) | **Lead Architect & PC/Server-Doc / Codebase Engineer**<br>• Server & Infrastructure maintenance (SSH, Proxmox PVE, PBS, Docker)<br>• Deep system audits, hardware health checks, database repairs<br>• Large-scale code refactorings, repository architecture, planning |
| **`🤖 [Claude]`** | Claude 3.7 Sonnet (Claude Code CLI / Desktop) | **Senior Backend & Business Logic Specialist**<br>• Python backend modules & Odoo controller logic<br>• XML views, QWeb reports, CSS/Frontend design<br>• In-depth code reviews & algorithmic optimizations |
| **`🤖 [ServAssi]`** | OpenClaw (CT150 / Telegram `@Frawo_bot`) | **24/7 Operations Guard & Mobile Bot**<br>• 24/7 server monitoring, watchdog cron checks, daily morning reports<br>• Fast mobile assistant for Wolf on Telegram<br>• Home Assistant smart home control & quick infrastructure triage |

---

## 2. Single Source of Truth (SSOT)
- **Odoo (`http://10.1.0.112:8069`)** is the absolute and sole SSOT for all roadmaps, tasks, timelines, project boards, and task statuses.
- **`NOW.md`** is the sole SSOT for physical network inventory, virtual machine/container list, IP addresses, and VLANs.
- All other markdown documentation files relating to roadmaps, network plans, or status summaries are obsolete and must not be used or created.

---

## 3. Agent Identity & Multi-Worker Coordination
- **Shared Odoo User:** All AI agents operate under the single Odoo identity `agent@frawo.tech` (UID 7, "🤖 Agent").
- **Worker Self-Identification:** In EVERY Odoo task chatter note, log message, or git commit, the acting worker MUST explicitly identify itself at the start:
  - `🤖 [Antigravity] ...`
  - `🤖 [Claude] ...`
  - `🤖 [ServAssi] ...`
- **Task Claiming (Collision Prevention):** Before beginning work on any Odoo task:
  1. Check if the task is already claimed by another active agent (`stage_id = 3` / *In Arbeit* with an active claim).
  2. If free, set stage to `In Arbeit` (Stage ID 3).
  3. Post claim comment: `🤖 [WorkerName] übernimmt — <Timestamp>`.
- **Handoffs & Delegation between Agents:**
  When passing a task to a teammate:
  1. Post a chatter note: `🤖 [CurrentAgent] 👉 Übergabe an @[TargetAgent]: <Konkrete Aufgabenstellung>`.
  2. Set stage to `In Planung` (Stage ID 2) or `Backlog` (Stage ID 1).
- **Task Completion:**
  1. Live verify changes on real endpoints/files.
  2. Set stage to `✅ Erledigt` (Stage ID 6).
  3. Post completion summary with proof in chatter.
- **Blockers:**
  1. If blocked, set stage to `🛑 Blockiert` (Stage ID 5).
  2. Detail the exact blocker in the chatter and ping the required person/agent.

---

## 4. Behavior Constraints & Best Practices
- **No Stale Documents:** Do not create or update separate roadmap or planning markdown files. Keep all details inside Odoo tasks or `NOW.md`.
- **No Hardcoded Passwords:** Never write passwords, API keys, or tokens in plaintext to files. Reference Vaultwarden (e.g. `[Vault: UCG API Key]`).
- **Never Claim "Done" Without Live Proof:** Always verify live before reporting completion (curl endpoint, read file, query database).
- **Repo Sync:** Always commit and push changes to `main` at the end of a session so all teammates have the latest state.

---

## 5. Corporate Identity (VERBINDLICH)
- **CI v3.0 is the absolute and sole branding of FraWo GbR** (SSOT: [`SSOT/FRAWO_CI_GUIDELINES.md`](SSOT/FRAWO_CI_GUIDELINES.md), mirrored in Odoo **Task 97**).
- Non-negotiable: colors **Forest `#004030` + Violet `#a050f0`**; strictly flat, 0px radius, NO shadows / gradients / glassmorphism; font **Inter** only; address reader as **Du**; KCanG §6 wording for herbs/smart grow systems.


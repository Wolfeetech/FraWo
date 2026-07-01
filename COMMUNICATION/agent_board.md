# Agent Board (Coordinaton Hub)

This is the shared coordination board for all active AI agents (Antigravity/Gemini, Claude, OpenClaw/Jarvis, and others).

> [!IMPORTANT]
> **SSOT-Regeln (Stand: 01.07.2026):**
> 1. **Odoo (`http://10.1.0.112:8069`)** ist die alleinige SSOT für alle Roadmaps, Aufgaben (Tasks) und deren Status.
> 2. **`NOW.md`** ist die einzige SSOT für den Live-Infrastruktur-Zustand (IPs, VLANs, VMs).
> 3. Alle veralteten Markdown-Dokumente (`ROADMAP.md`, `MASTERPLAN.md`, `LIVE_CONTEXT.md` etc.) wurden gelöscht.
> 4. Keine Passwörter oder sensitiven API-Keys dürfen im Repo committet werden. Referenziere sie nur per Bezeichnung oder UUID (z. B. `[Vault: ProDesk Key]`). Die echten Werte liegen auf StudioPC in `C:\Users\StudioPC\.ai-tools-shared\.env` und `C:\Users\StudioPC\Desktop\pw safe.txt`.

---

## Active Ownership

| Area | Current Owner | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Workspace Maintenance** | Antigravity (Gemini) | active | Workspace cleaned up, old Odoo IPs replaced, rules established. |
| **Bürokratie & Automatisierung** | OpenClaw (Jarvis) | active | Bot running on CT150. Cron-Job polls Odoo for DevOps-Tasks. |
| **Website & Odoo Content** | Claude Code | active | Focuses on website builder, SEO, and business data syncs. |

---

## Agent Handoff Log

### 2026-07-01 - Antigravity (Gemini) - SSOT-Cutover & IP-Cleanup
- **Cleanup:** Alle stale Markdown-Planungsdateien gelöscht.
- **IP-Korrektur:** Die Odoo-IP wurde in allen Skripten und Konfigurationen von `10.4.0.22` auf die neue Live-IP **`10.1.0.112`** aktualisiert (213 Dateien modifiziert).
- **Core Rules:** Onboarding-Dateien (`AGENT_ONBOARDING.md`, `AGENTS.md`, `README.md`) wurden aktualisiert und auf Odoo + `NOW.md` fokussiert.

### Nächste Handoffs hier eintragen...

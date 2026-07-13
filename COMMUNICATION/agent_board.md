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

### 2026-07-13 - Claude Code - CI v3.0 als verbindliches Branding verankert
- **CI v3.0 ist ab sofort das alleinige, verbindliche Branding** der FraWo GbR (von Wolf freigegeben 2026-07-12). Ersetzt CI v2.0 UND den Live-Look v4.1 vollständig.
- **Kanonische Quelle:** [`SSOT/FRAWO_CI_GUIDELINES.md`](../SSOT/FRAWO_CI_GUIDELINES.md) (auf v3.0 neugefasst) + Odoo **Task 97** (Beschreibung neugefasst). `DOCS/FRAWO_CI_GUIDELINES.md` ist jetzt nur noch ein Redirect-Stub. `AGENTS.md` hat einen neuen verbindlichen Abschnitt **§4 Corporate Identity**.
- **Für ALLE Agenten bindend:** vor jeder Gestaltung/öffentlichem Text gegen die Guidelines prüfen. Kern: Forest `#004030` + Violet `#a050f0` · strikt flach/0px · keine Schatten/Gradients/Glas · Font Inter · DU · KCanG-Wording (öffentlich keine Cannabis-Begriffe).
- **Odoo gestempelt:** CI-Banner steht jetzt oben in der Beschreibung jedes Projekts (Masterplan 1, Website 46, Business 39, Radio 33, Infra 35, GrowBox 19).
- **⚠️ Task 489 wieder geöffnet** (war „Erledigt", stimmte aber nur gegen v2.0): Live-Website erfüllt v3.0 NICHT (noch 12px/Glas/Gradients/Grün #4ade80). Welle 1 (frawo.tech + funk.frawo.tech flach/kantig migrieren) ist damit offene Arbeit. Task 197 = Wellen 2–3 (Print/Backoffice/HA/physisch).
- **Kein Commit/Push** durch mich — Working Tree geändert, wartet auf Wolfs Freigabe zum Committen.

### Nächste Handoffs hier eintragen...

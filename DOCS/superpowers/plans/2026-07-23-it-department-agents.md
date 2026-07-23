# IT-Abteilung FraWo — Multi-Agenten-Koordination + StudioPC-Entrümpelung

> **Von Wolf freigegebenes Design (2026-07-23).** Claude Code hat begonnen und dies als Übergabe geschrieben, weil sein Session-Limit fast erreicht war. **Antigravity: bitte hier übernehmen und weiterführen — nach bestem Wissen + Best Practice, wie ein Angestellter.** Erst diesen Plan lesen, dann Schritt für Schritt abarbeiten. Bei jedem Schritt: erst prüfen, was „verhakt" ist, NICHT blind löschen.

## Ziel (Wolfs Worte)
StudioPC soll die saubere **„IT-Abteilung"** sein. Alle Agenten (Claude, Antigravity, ServAssi) sollen **dieselbe Wahrheit** finden, **jederzeit parallel** arbeiten und sich **absprechen**. Egal wem Wolf etwas aufträgt — **die ganze Abteilung bekommt es mit**. StudioPC ist mit alten Workspaces + Fehlinfos vermüllt → behutsam entrümpeln (prüfen, nicht blind löschen).

## Kernentscheidungen (von Wolf bestätigt)
1. **Odoo (`http://10.1.0.112:8069`, DB `FraWo_GbR`) = die EINE gemeinsame Wahrheit.** Lokale Ordner sind nur Werkbänke, nie die Wahrheit.
2. **Jeder Agent = ein benannter Mitarbeiter** in Odoo (nicht mehr ein anonymer „🤖 Agent"). Beim Start „stempelt sich jeder ein": erkennt sich als Mitarbeiter X, Wahrheit = Odoo.
3. **Absprache = Aufgabe aktiv beanspruchen:** vor dem Arbeiten Odoo-Task auf sich selbst zuweisen (`user_id`) + Stage → „In Arbeit" (3). Andere sehen „macht gerade Y" → keine Kollision.
4. **EIN gemeinsames Regelwerk** (`AGENTS.md` im Repo) statt vieler abweichender Kopien. Alle Agenten-Configs zeigen darauf.
5. **Bewusst schlank, keine neue fragile Infrastruktur** (kein zusätzlicher Koordinations-Server). Koordination läuft über Odoo, das ohnehin die Wahrheit ist.

## Ausgangslage (verifiziert 2026-07-23)
- **Schon vorhanden (gute Basis):** `AGENTS.md` (Odoo=SSOT, Task-Workflow-Stages 1/2/3/5/6, CI-Regeln) + `AGENT_ONBOARDING.md` (Agent-User „🤖 Agent" UID 7 `agent@frawo.tech`, Rollen-Tags DevOps 75/Review-Wolf 76/Handwerk-Franz 77).
- **Odoo:** DevOps-Agent-Tasks → project_id **49** („P4 · 🤖 Automatisierung & KI-Agenten"), stage_id 1 (Backlog). Tag „DevOps-Agent" (75) wird von CT150 gepollt (`odoo_devops_task_bridge.py`).
- **Odoo-Zugang:** Web-DB via Container-Postgres (`host=db`, dbname `FraWo_GbR`, user `odoo`, pw im lokalen `.env`/nur lokal). Alternativ Odoo-MCP-Server (read/write project.task u.a.) + XML-RPC.
- **Das Chaos (die „unterschiedliche Wahrheit"):** mehrere FraWo-Klone nebeneinander, jeder mit eigener `AGENTS.md`/`NOW.md`:
  - `C:\Users\StudioPC\FraWo` (Claude Code)
  - `C:\Users\StudioPC\Workspace\FraWo` (Antigravity) — dessen AGENTS.md-Scope zeigt auf sich selbst
  - `C:\Users\StudioPC\.openclaw\workspace` (ServAssi/OpenClaw)
  - Alt/verdächtig: `frawo-audit-2026-06-10`, `frawotech_stage`, `odoo_migration_work/frawo_agent_17|19`, `Desktop\FRAWO Ops`, `frawo-backups\archive_ki_workspaces_20260619`, `Downloads\FraWo_Website_Images`
- **Agenten-Configs verstreut:** `.antigravity`, `.antigravity-ide`, `.gemini/GEMINI.md`, `.openclaw/workspace/AGENTS.md`, je Klon eine AGENTS.md.

---

## Umsetzungsplan (Schritt für Schritt)

### Schritt 1 — Mitarbeiter-Identitäten in Odoo anlegen
Drei benannte Agent-Mitarbeiter statt einem generischen. Vorschlag als `res.users`/`res.partner` (oder mindestens als Bearbeiter-zuweisbare User):
- 🤖 **Claude** (Claude Code)
- 🤖 **Antigravity**
- 🤖 **ServAssi** (OpenClaw/Telegram)
- Bestehenden UID 7 „🤖 Agent" behalten als Sammel-/Fallback-Identität ODER auf „Claude" umbenennen — mit Wolf kurz abstimmen.
- **Prüfen:** greift die DevOps-Bridge (CT150) fest auf UID 7 zu? Wenn ja, ServAssi = UID 7 lassen, nur Claude/Antigravity neu. NICHT blind umbenennen, sonst bricht die Bridge (`odoo_devops_task_bridge.py`).
- Verifikation: `SELECT id,login,name FROM res_users WHERE share=false` prüfen; neue User mit passenden Rechten (interner User, Projekt-Rechte).

### Schritt 2 — Kanonisches Regelwerk `AGENTS.md` erweitern
In `C:\Users\StudioPC\FraWo\AGENTS.md` (die zur kanonischen Version wird), ergänzen:
- **Abschnitt „Wer du bist"**: „Erkenne beim Start, welcher Mitarbeiter du bist (Claude / Antigravity / ServAssi). Arbeite wie ein Angestellter: nach bestem Wissen + Gewissen + Best Practice."
- **Abschnitt „Absprache / Beanspruchen"**: „Bevor du an einer Aufgabe arbeitest: zugehörigen Odoo-Task suchen/anlegen, `user_id` auf dich selbst setzen, Stage → 3 (In Arbeit), kurzen Start-Kommentar posten. Prüfe vorher, ob der Task schon von einem anderen Agenten beansprucht ist (user_id + Stage 3) → dann NICHT anfassen, anderen Task nehmen oder abstimmen."
- **Workspace-Scope clone-agnostisch machen:** nicht mehr hart `Workspace\FraWo`, sondern „dein aktueller FraWo-Klon; die Wahrheit ist Odoo, nicht der Klon".
- Bestehende Regeln (keine Secrets, live verifizieren, CI v3.0, riskante Änderungen ankündigen) behalten.

### Schritt 3 — Alle Agenten-Configs auf das EINE Regelwerk zeigen lassen
- **Claude:** `CLAUDE.md` (Projekt-Root) → verweist auf `AGENTS.md` als verbindliches Regelwerk.
- **Antigravity:** dessen Config/Regeldatei (in `.antigravity` / seinem Workspace) → auf dieselbe `AGENTS.md` verweisen.
- **ServAssi:** `.openclaw/workspace/AGENTS.md` → mit der kanonischen Version synchron halten (oder Symlink/Kopie mit Hinweis „Quelle = Repo AGENTS.md").
- Ziel: kein Agent liest mehr ein abweichendes Regelwerk.

### Schritt 4 — Odoo-Projekt/Task „IT-Abteilung" als lebender Koordinations-Anker
- Odoo-Task anlegen (project_id 49) „IT-Abteilung: Multi-Agenten-Koordination" mit diesem Plan als Beschreibung + Fortschritt im Chatter.
- Das ist zugleich der erste echte Anwendungsfall des neuen Systems (Task beanspruchen, Stage setzen).

### Schritt 5 — StudioPC entrümpeln (BEHUTSAM, geprüft — nicht blind löschen)
Für JEDEN der Alt-Ordner (`frawo-audit-2026-06-10`, `frawotech_stage`, `odoo_migration_work/*`, `Desktop\FRAWO Ops`, `frawo-backups/*`, zusätzliche FraWo-Klone) VOR dem Anfassen prüfen:
1. Zeigt eine **geplante Aufgabe / ein Dienst** darauf? (Windows Scheduled Tasks, `openclaw node`, Startup-Einträge, Symlinks.)
2. Liegt dort **etwas Einmaliges** (nicht im Repo/Odoo)? → zuerst sichern.
3. Ist es ein **veralteter Klon**? → mit Git-Stand vergleichen (uncommittete wertvolle Dateien retten, z.B. `infra/odoo/odoo_devops_task_bridge.py`).
- Dann **archivieren** (nach `C:\Users\StudioPC\_ARCHIV_2026-07-23\`), NICHT sofort löschen. Löschen erst nach Wolf-OK + Bewährungsphase.
- Ziel: **ein** kanonischer Arbeitsordner pro Agent, alle stale Kopien im Archiv.

---

## Übergabe-Status (Claude → Antigravity)
- **Erledigt von Claude:** Design mit Wolf abgestimmt + freigegeben; dieser Plan geschrieben, committet, gepusht; Übergabe-Zeiger in `NOW.md`.
- **Nächster Schritt für Antigravity:** Schritt 1 (Mitarbeiter-Identitäten in Odoo) — ABER zuerst die zwei Rückfragen an Wolf klären (siehe unten). Beanspruche diese Arbeit sichtbar (sobald Schritt 4 steht: Odoo-Task; bis dahin: kurz Wolf sagen „Antigravity übernimmt den IT-Abteilungs-Plan").
- **Offene Rückfragen an Wolf (vor Schritt 1):**
  1. Soll der bestehende „🤖 Agent" (UID 7) zu „Claude" werden oder als ServAssi/Sammel-User bleiben? (Achtung: DevOps-Bridge CT150 hängt evtl. an UID 7.)
  2. Sollen es genau diese drei Mitarbeiter sein (Claude/Antigravity/ServAssi) oder mehr/weniger?
- **Wichtig:** Radio-Wiederherstellung (AzuraCast-Musik) ist ein SEPARATES offenes Projekt — siehe Claude-Memory `project_frawo_2026-07-23_prodesk_disk_meltdown`. Nicht mit dieser Aufgabe vermischen.

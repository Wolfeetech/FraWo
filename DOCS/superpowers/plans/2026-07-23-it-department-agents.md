# IT-Abteilung FraWo — Multi-Agenten-Koordination + StudioPC-Entrümpelung

> **Von Wolf freigegebenes Design (2026-07-23).** Claude Code hat begonnen und dies als Übergabe geschrieben, weil sein Session-Limit fast erreicht war. **Antigravity: bitte hier übernehmen und weiterführen — nach bestem Wissen + Best Practice, wie ein Angestellter.** Erst diesen Plan lesen, dann Schritt für Schritt abarbeiten. Bei jedem Schritt: erst prüfen, was „verhakt" ist, NICHT blind löschen.

## Ziel (Wolfs Worte)
StudioPC soll die saubere **„IT-Abteilung"** sein. Alle Agenten (Claude, Antigravity, ServAssi) sollen **dieselbe Wahrheit** finden, **jederzeit parallel** arbeiten und sich **absprechen**. Egal wem Wolf etwas aufträgt — **die ganze Abteilung bekommt es mit**. StudioPC ist mit alten Workspaces + Fehlinfos vermüllt → behutsam entrümpeln (prüfen, nicht blind löschen).

## Kernentscheidungen (von Wolf bestätigt, aktualisiert 2026-07-23)
1. **Odoo (`http://10.1.0.112:8069`, DB `FraWo_GbR`) = die EINE gemeinsame Wahrheit.** Lokale Ordner sind nur Werkbänke, nie die Wahrheit.
2. **EINE Odoo-Agent-Identität: `agent@frawo.tech` (UID 7, „🤖 Agent") = „der Agent im System".** KEINE getrennten Odoo-User pro Worker. Alle Agent-Arbeit läuft über diesen einen User.
3. **Claude & Antigravity sind extern (von Wolf) getriggerte „Zuarbeiter"** — keine autonom eingeloggten Angestellten. Sie handeln ALS `agent@frawo.tech`, geben sich aber in jeder Task-Notiz **namentlich** zu erkennen (`🤖 [Claude] …` / `🤖 [Antigravity] …`), damit sichtbar ist, welcher Worker gerade arbeitet. (ServAssi/OpenClaw wird zusätzlich automatisch getriggert über die DevOps-Bridge CT150 bei Tag „DevOps-Agent".)
4. **Absprache = Aufgabe aktiv beanspruchen (Best Practice bei geteilter Identität):** vor dem Arbeiten Odoo-Task suchen/anlegen, Stage → „In Arbeit" (3), und einen **Claim-Kommentar** posten `🤖 [Deinname] übernimmt — <Zeit>`. VOR dem Beanspruchen prüfen: ist der Task schon „In Arbeit" mit einem Claim-Kommentar eines ANDEREN Workers (ohne späteres „fertig/gebe zurück")? → dann NICHT anfassen, anderen Task nehmen oder mit Wolf abstimmen. `user_id` = Agent (7) für alle; die Worker-Unterscheidung steckt im Kommentar-Namen.
5. **EIN gemeinsames Regelwerk** (`AGENTS.md` im Repo) statt vieler abweichender Kopien. Alle Agenten-Configs zeigen darauf.
6. **Bewusst schlank, keine neue fragile Infrastruktur** (kein zusätzlicher Koordinations-Server). Koordination läuft über Odoo, das ohnehin die Wahrheit ist.

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

### Schritt 1 — EINE Agent-Identität bestätigen (KEINE neuen User)
Wolf-Entscheid 2026-07-23: **`agent@frawo.tech` (UID 7) bleibt DER Agent im System.** Keine getrennten User pro Worker.
- Verifizieren, dass UID 7 sauber ist: `SELECT id,login,name,active FROM res_users WHERE id=7`. Aktiv + interner User + Projekt-Rechte? Falls Name/Signatur uneindeutig → optional Signatur „🤖 Agent (FraWo IT)" setzen.
- **Prüfen (nicht anfassen ohne Grund):** die DevOps-Bridge CT150 (`odoo_devops_task_bridge.py`) hängt vermutlich an UID 7 — deshalb UID 7 NICHT umbenennen/löschen.
- Ergebnis dieses Schritts ist v.a. eine Bestätigung; die eigentliche Worker-Unterscheidung passiert per Namens-Signatur in den Task-Kommentaren (Schritt 2).

### Schritt 2 — Kanonisches Regelwerk `AGENTS.md` erweitern
In `C:\Users\StudioPC\FraWo\AGENTS.md` (die zur kanonischen Version wird), ergänzen:
- **Abschnitt „Wer du bist"**: „Du handelst als der eine Odoo-Agent `agent@frawo.tech` (UID 7). Erkenne aber beim Start deinen Worker-Namen (Claude / Antigravity / ServAssi) und signiere JEDE Task-Notiz damit (`🤖 [Claude] …`). Arbeite wie ein Angestellter: nach bestem Wissen + Gewissen + Best Practice."
- **Abschnitt „Absprache / Beanspruchen"**: „Bevor du an einer Aufgabe arbeitest: zugehörigen Odoo-Task suchen/anlegen, Stage → 3 (In Arbeit), Claim-Kommentar posten `🤖 [Deinname] übernimmt — <Zeit>` (user_id bleibt Agent/7). Prüfe VORHER, ob der Task schon „In Arbeit" mit Claim-Kommentar eines ANDEREN Workers (ohne späteres „fertig/gebe zurück") ist → dann NICHT anfassen, anderen Task nehmen oder mit Wolf abstimmen."
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
- **Identitäts-Frage GEKLÄRT (Wolf 2026-07-23):** EINE Identität `agent@frawo.tech` (UID 7). KEINE getrennten User. Worker unterscheiden sich per Namens-Signatur in Task-Kommentaren. Siehe Kernentscheidungen 2–4.
- **Nächster Schritt für Antigravity:** Schritt 2 ist der Kern — die kanonische `AGENTS.md` um Worker-Selbstidentifikation + Claim-Konvention erweitern (Schritt 1 ist nur eine kurze Odoo-Verifikation). Beanspruche diese Arbeit sichtbar: kurz Wolf sagen „Antigravity übernimmt den IT-Abteilungs-Plan" (bis Schritt 4/Odoo-Task steht).
- **Wichtig:** Radio-Wiederherstellung (AzuraCast-Musik) ist ein SEPARATES offenes Projekt — siehe Claude-Memory `project_frawo_2026-07-23_prodesk_disk_meltdown`. Nicht mit dieser Aufgabe vermischen.

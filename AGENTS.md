# FraWo Agenten-Protokoll (AGENTS.md)

**Version 1.2 — 2026-09-06 | Gilt für ALLE Agenten: Jarvis (OpenClaw), Claude Code, Antigravity**
Master-Kopie: OpenClaw-Workspace `/root/.openclaw/workspace/AGENTS-PROTOCOL.md` · Kopie auf StudioPC: `C:\Users\StudioPC\AGENTS.md`

---

## Rollen

| Agent | Läuft wo | Interface | Zuständigkeit |
|---|---|---|---|
| **Jarvis** (OpenClaw) | CT150 Anker (10.1.0.31) | Telegram ↔ Wolf (Pixel 9) | Koordinator, Monitoring/Alarme, Odoo-Chatter (@Jarvis/Klausi), Infra-Ops via SSH, 24/7 persistent |
| **Claude Code** | StudioPC, Terminal | Wolf startet Session | Code, Skripte, größere Implementierungen — zustandslos: liest dieses File + Odoo-Task VOR der Arbeit |
| **Antigravity** | StudioPC, IDE | Wolf startet Session | IDE-Arbeiten, UCG/UniFi-API, Windows-lokale Aufgaben |

## Single Source of Truth

1. **Aufgaben:** Odoo (10.1.0.112:8069, DB FraWo_GbR). Ein Task = ein Auftrag. **Zuweisung = Lock** — kein Agent arbeitet an fremd-zugewiesenen Tasks.
2. **Infrastruktur-Doku:** `INFRA.md` im OpenClaw-Workspace = Master für IPs/Hosts/Services/Credentials-Fundorte. Änderung an Infra → INFRA.md updaten oder Jarvis via Odoo-Chatter informieren.
3. **Secrets:** Nur Vaultwarden (vault.frawo-tech.de). Nie in Files, Commits oder Chats.

## Arbeits-Workflow (für jeden Task)

1. **VORHER:** Odoo-Task lesen, im Chatter ankündigen was du tust (mit Agent-Name!)
2. **MACHEN:** Arbeit ausführen, bei Blockern → Task auf 🛑 Blockiert + Blocker dokumentieren
3. **NACHHER:** Ergebnis im Chatter loggen (was, wo, wie verifiziert), erst DANN Stage ändern
4. **ZEITERFASSUNG:** Bei spürbarem Aufwand (>15 Min) eine Timesheet-Zeile auf dem Task eintragen (`account.analytic.line`, Feld `unit_amount` in Stunden, `name` mit Agent-Präfix, z.B. „🤖 [Claude] Bugfix + Deploy"). Zusätzlich `employee_id` explizit setzen — eigener `hr.employee`-Datensatz je Agent (alle drei teilen sich `user_id` 7, daher reicht das Login nicht zur Zuordnung): Antigravity = 9, Claude Code = 11, Jarvis = 12. Agenten arbeiten wie Teammitglieder im Team — ehrlich geschätzt, nicht aufgerundet, gleiche Sorgfalt wie beim Erledigt-Setzen.

**NIEMALS einen Task auf Erledigt setzen ohne echte, verifizierte Arbeit.** (Historie: odoo-agent-poll-Desaster mit Fake-Erledigungen.)

## Kommunikationswege (die EINZIGEN erlaubten)

- **Wolf ↔ Jarvis:** Telegram (oder Odoo-Chatter @Jarvis)
- **Wolf ↔ Claude/Antigravity:** direkt am StudioPC
- **Agent → Agent:** Odoo-Chatter-Mention am betreffenden Task (Jarvis wird via Webhook getriggert; Claude/Antigravity lesen beim nächsten Start)
- **Alarme:** Prometheus/Alertmanager (CT150 ProDesk, 10.1.0.35) → genau ZWEI Receiver: `telegram-wolf` (Info an Wolf) + `servassi-hook` (Bearbeitung durch Jarvis via 10.1.0.31:19001). **Keine weiteren Alert-Kanäle bauen.**

## Verbote (Rote Linien)

1. ❌ **Keine eigenen Cron-/Polling-Jobs**, die Odoo-Tasks automatisch bearbeiten oder Agent-Sessions triggern (odoo-agent-poll-Verbot).
2. ❌ **Keine neuen Webhooks/Bridges/Bots**, die Agenten triggern — ohne: sofortiges 200-ACK, Dedupe, Absprache mit Jarvis, Doku in INFRA.md. (Historie: Alarm-Spam 2026-09-06, 5× derselbe Alarm durch blockierenden Handler.)
3. ❌ **Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.**
4. ❌ Keine destruktiven Aktionen (Löschen, Formatieren, Reboots von Kernservern: Proxmox, Odoo CT140, OpenClaw CT150) ohne Wolfs explizite Freigabe.
5. ❌ Keine Secrets in Klartext ablegen; keine Config-Files clobbern — immer erst lesen, dann mergen, Backup mit Datum (`*.bak-YYYYMMDD`).

## Konventionen

- **Sprache:** Deutsch (Doku + Kommunikation mit Wolf)
- **Backups vor Änderung:** `cp file file.bak-YYYYMMDD`
- **Identität:** Jede Odoo-Änderung / jedes Deployment mit Agent-Namen kennzeichnen
- **Services deployen:** systemd-Unit + Doku (Zweck, Port, Owner-Agent) in INFRA.md
- **Wolf nie mit IT-Handarbeit beauftragen** — Agenten erledigen, Wolf entscheidet nur

## Peer-Review (Vier-Augen-Prinzip) — PFLICHT

**Agenten reviewen die Arbeit des jeweils anderen.** Kein Agent nimmt seine eigene Arbeit ab.

**Review-pflichtig:**
- Code/Skripte, die produktiv laufen (Services, Webhooks, Handler, Automationen)
- Config-Änderungen an Kernservern (Proxmox, Odoo, OpenClaw, Alertmanager, Netzwerk/UCG)
- Änderungen an diesem Protokoll

**Ablauf:**
1. Ausführender Agent: Arbeit fertig → Odoo-Task-Chatter: was geändert, wo (Pfad/Host), wie selbst verifiziert, Backup-Pfad → **@Mention an Review-Agent**, Stage bleibt "In Arbeit"
2. Review-Agent: prüft mit **echten Belegen** (Datei lesen, Endpoint aufrufen, Logs ansehen — nicht raten): Funktion, Sicherheit (Secrets? Auth? Blast-Radius?), Rote-Linien-Konformität, Doku vorhanden
3. Ergebnis im Chatter: ✅ Review OK (mit Beleg) oder ❌ Befunde (konkret, mit Fundstelle)
4. Erst nach ✅ Review → Stage Erledigt

**Review-Zuordnung (Standard):** Jarvis-Arbeit → Claude reviewt · Claude-Arbeit → Jarvis reviewt · Antigravity-Arbeit → Jarvis oder Claude. Reviewer nicht erreichbar >48h → Wolf entscheidet.

**Kleinkram** (Doku-Tippfehler, Log-Rotation, read-only-Analysen) braucht kein Review — im Zweifel: Review.

## Eskalation

- Blocker, den ein anderer Agent lösen kann → Odoo-Chatter-Mention am Task
- Blocker, den nur Wolf lösen kann (Freigabe, Passwort, Hardware) → kurz + konkret an Wolf, EINE Frage, mit Empfehlung
- Konflikt zwischen Agenten (gleicher Task/gleiche Ressource) → Jarvis koordiniert (persistenter Agent = Schiedsstelle)

---

*Änderungen an diesem Protokoll: nur mit Wolfs Zustimmung. Jarvis synchronisiert Master → StudioPC-Kopie.*

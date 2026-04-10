# Operator Todo Queue

> **Solo Operator Quick Start:** Pick one item from **Next**, move it to **Doing**, finish it, move to **Done**.
> Don't add more than 3 items to Doing at once.

Stand: `2026-04-10` | Aktualisiert von: Codex

---

## Kanban Board

### 🔴 Blocked
*(Warte auf externen Input – Operator-Aktion erforderlich)*

| Task | Warum blockiert | Frühestes Datum | Was danach? |
|------|-----------------|-----------------|-------------|
| `vaultwarden_recovery_material_verified` | Offline-Kopien aktuell nicht möglich (Operator hat bis Mai 2026 keinen Zugriff auf Druck/USB/physische Ablage) | **2026-05-01** | Checkliste unten ausführen, dann MVP-Gate final schließen |
| `device_rollout_verified` (Franz Surface/iPhone) | Sichtbarer Gerätenachweis fehlt – **offen: ist das bis Mai ebenfalls blockiert?** Am nächsten Laptop-Tag prüfen und diesen Eintrag aktualisieren. | unklar | `scripts/prove_device_rollout.ps1` ausführen |

#### Checkliste: `vaultwarden_recovery_material_verified` (Mai 2026)

Alle Schritte ohne Secrets – keine Passwörter oder Tokens ins Repo:

- [ ] 1. Zwei physische Offline-Kopien der Vaultwarden-Recovery-Infos erstellen (z.B. Papierausdruck + USB-Stick, oder 2× USB-Stick an getrennten Orten).
- [ ] 2. Sichtprüfung: Beide Kopien sind lesbar und vollständig.
- [ ] 3. In `LIVE_CONTEXT.md` nur den Status setzen: `recovery_material: verified` (keinerlei Inhalte eintragen).
- [ ] 4. In `MEMORY.md` unter `## Aktive Operator-Aktionen` den Blocker als erledigt markieren.
- [ ] 5. `scripts/release_mvp_gate.py` ausführen, um das MVP-Gate zu schließen.

---

### 📱 Phone-only next steps

*(Aufgaben, die ohne Terminal/Laptop machbar sind)*

| Aufgabe | Wo / Wie |
|---------|----------|
| Diese Datei und `MEMORY.md` lesen – Kontext auffrischen | GitHub App / Browser |
| `SECURITY_BASELINE.md` lesen – Verständnis, nichts ausführen | GitHub App / Browser |
| `OPS_HOME.md` → Lane C / Security lesen | GitHub App / Browser |
| `docs/plans/next_steps_until_may_2026.md` lesen und Entscheidungen treffen | GitHub App / Browser |
| Entscheiden: Ist `device_rollout_verified` bis Mai blockiert? → Eintrag oben aktualisieren | GitHub App / PR-Kommentar |
| Checkliste in diesem Dokument (Vaultwarden, Mai 2026) mental vorbereiten | keine Tools |

*(Aufgaben, die Terminal / Laptop erfordern)*

| Aufgabe | Einstieg |
|---------|---------|
| PBS-Restore-Drill monatlich wiederholen | `make pbs-restore-proof` |
| Tailnet Route-Freigabe + Split-DNS schließen | `SECURITY_BASELINE.md` → Punkt 2 |
| `NETWORK_INVENTORY.md` via Easy-Box-Abgleich finalisieren | `make easybox-browser-probe` |
| Security-Baseline prüfen | `make security-baseline-check` |

### 🟡 Next (Bereit zum Start – erfordert Laptop/Terminal)

| Task | Lane | Einstieg |
|------|------|---------|
| PBS-Restore-Drill monatlich wiederholen | Lane C | `make pbs-restore-proof` |
| Tailnet Route-Freigabe + Split-DNS schließen | Lane C | `SECURITY_BASELINE.md` → Punkt 2 |
| `NETWORK_INVENTORY.md` via Easy-Box-Abgleich finalisieren | Lane C | `make easybox-browser-probe` |

### 🟢 Doing
*(Max. 3 gleichzeitig)*

| Task | Gestartet | Nächster Schritt |
|------|-----------|-----------------|
| *(leer)* | | |

### ✅ Done (Letzte 30 Tage)

| Task | Abgeschlossen |
|------|---------------|
| Lane A: Business-MVP (Nextcloud, Odoo, Paperless live) | 2026-03-30 |
| PBS-Erstinbetriebnahme + erster Restore-Drill | 2026-03-21 |
| Surface Go Frontend V1 live | 2026-03-25 |
| Radio AzuraCast live auf Pi | 2026-03-28 |
| MVP-Browserabnahme (Wolf + Franz) | 2026-03-30 |
| Repo-Hygiene: .vault_pass entfernt, SECURITY.md hinzugefügt | 2026-04-09 |

---

## Definition of Done (DoD)

Eine Task gilt erst als **Done**, wenn alle folgenden Punkte erfüllt sind:

- [ ] **Verifikation läuft durch**: Mindestens ein `make <check>` oder Script liefert grünes Ergebnis
- [ ] **Runbook existiert**: Wie reproduziert man es? Wie rollt man zurück? (min. 3 Zeilen in einer `.md`)
- [ ] **Secrets nicht im Repo**: Kein Klartext-Passwort, kein Token in einer committed Datei
- [ ] **SSOT aktualisiert**: Mindestens eine kanonische Datei (LIVE_CONTEXT.md, VM_AUDIT.md, MEMORY.md) spiegelt den neuen Zustand
- [ ] **Operator informiert**: Falls Handoff nötig, steht es unter `AKTION VON DIR ERFORDERLICH:` in dieser Datei

---

## Task-Template

```markdown
### [TASK-ID] Kurzbeschreibung

- **Lane:** Lane X
- **Prio:** High / Medium / Low
- **Gestartet:** YYYY-MM-DD
- **Ziel:** Was soll am Ende sichtbar besser sein?
- **Verifikation:** `make <target>` oder manueller Check
- **Runbook:** Link zu `.md` oder Inline-Schritten
- **Blocker:** (leer wenn keiner)
```

---

## Zweck

Diese Datei ist die kurze manuelle Unblock-Queue.

Keine zweite Projektplanung, keine erledigte Historie, keine Nebenstrang-Roadmaps.
Der aktive Arbeitsfokus liegt nun nicht mehr in Lane A, da das MVP abgeschlossen ist.

## Professional-Autopilot Regeln

- Default-Modell: `Aggressive Autopilot`
- `Codex` fuehrt
- `Gemini` prueft sichtbar
- der Operator entscheidet nur an echten Pflicht-Stopps

Pflicht-Stopp vor:

- `Infra/Public`
- `Netzwerk`
- `Datenmigration`
- `Storage/PBS`
- `Router`
- `HA/PVE`
- `Security-Boundary`
- lokalen Windows-Admin-Token-Eingriffen

Alles andere laeuft standardmaessig im Loop:

1. Truth sammeln
2. professionell beurteilen
3. Aenderung klassifizieren
4. ausfuehren oder eskalieren
5. verifizieren
6. SSOT aktualisieren

## Lane Status

- `Lane A: MVP Closeout` -> `completed`
- `Lane B: Website/Public Hold` -> `watch`
- `Lane C: Security/PBS/Infra` -> `completed`
- `Lane D: Stockenweiler` -> `watch`
- `Lane E: Radio/Media` -> `watch`

## Manuelle Unblock-Punkte

- `vaultwarden_recovery_material_verified` – blockiert bis **2026-05-01** (physische Offline-Kopien nicht früher möglich). Checkliste im Blocked-Abschnitt oben.
- `device_rollout_verified` – Status unklar; am nächsten Laptop-Tag prüfen ob ebenfalls bis Mai blockiert.

## Nicht In Dieser Queue

- `Lane B: Website/Public Hold` bleibt sichtbar, aber ohne neue Go-Live-Arbeit.
- `Lane D: Stockenweiler` bleibt sichtbar, aber ohne Live-Rollout.
- `Lane E: Radio/Media` bleibt im Erhaltungsmodus ohne Ausbau.

## Kanonische Steuerdateien

- `AI_OPERATING_MODEL.md` fuer das verbindliche AI-Arbeitsmodell
- `AI_SERVER_HANDOFF.md` fuer externen KI-Handoff
- `MASTERPLAN.md` fuer die strategische Lane-Reihenfolge
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md` als einzige Wahrheit fuer die MVP-Entscheidung
- `GEMINI.md` fuer delegierbare Browser- und Operator-Jobs
- `manifests/work_lanes/current_plan.json` als maschinenlesbare Lane-Quelle

# Operator Todo Queue

> **Solo Operator Quick Start:** Pick one item from **Next**, move it to **Doing**, finish it, move to **Done**.
> Don't add more than 3 items to Doing at once.

Stand: `2026-04-10` | Aktualisiert von: Codex
Stand: `2026-04-11` | Aktualisiert von: Codex

---

## Kanban Board

### 🔴 Blocked
*(Warte auf externen Input – Operator-Aktion erforderlich)*

| Task | Warum blockiert | Frühestes Datum | Was danach? |
|------|-----------------|-----------------|-------------|
| `vaultwarden_recovery_material_verified` | Offline-Kopien aktuell nicht möglich | **2026-05-01** | Checkliste unten ausführen |
| `radio_pi_power_cycle` | LAN blinkt, aber System reagiert nicht | **Sofort** | Status-Check nach Neustart |

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
| AzuraCast Pi-Integration grün schließen | Lane E | `RASPBERRY_PI_RADIO_NODE_PLAN.md` |
| Jellyfin `TV Wohnzimmer`-Passwort hinterlegen | Lane E | `JELLYFIN_USER_SETUP_PLAN.md` |
| Stockenweiler yourparty-Payload sichern (vor Ausdünnung) | Lane D | `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md` |

### 🟢 Doing
*(Max. 3 gleichzeitig)*

| Task | Gestartet | Nächster Schritt |
|------|-----------|-----------------|
| *(leer)* | | |

### ✅ Done (Letzte 30 Tage)

| Task | Abgeschlossen |
|------|---------------|
| Lane A: Business-MVP (Nextcloud, Odoo, Paperless live) | 2026-03-30 |
| `haos_vm_210_trusted_proxies_fix` | 2026-04-14 |
| `public_edge_alpha_tunnel_live` | 2026-04-14 |
| `stockenweiler_ssh_recovery` | 2026-04-14 |
| `frawo_gbr_branding_sync` | 2026-04-14 |
| Odoo-Website: FraWo-Eventdienstleister-Auftritt published | 2026-04-09 |

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

- `Lane A: MVP Closeout` -> `completed` ✅
- `Lane B: Website/Public` -> `active` (Public Edge Alpha live: protocol-panel-cove-little.trycloudflare.com)
- `Lane C: Security/PBS/Infra` -> `watch` (PBS Restore-Drill fällig)
- `Lane D: Stockenweiler` -> `ok` (Access restored; home.prinz-stockenweiler.de valid until July)
- `Lane E: Radio/Media` -> `blocked` (Power cycle for Pi 4 required)

## Manuelle Unblock-Punkte

- `vaultwarden_recovery_material_verified` – blockiert bis **2026-05-01** (physische Offline-Kopien nicht früher möglich). Checkliste im Blocked-Abschnitt oben.
- `device_rollout_verified` – Status unklar; am nächsten Laptop-Tag prüfen ob ebenfalls bis Mai blockiert.
1. **DS-Lite / HTTPS** (Lane B): Cloudflare-Proxy aktivieren ODER ISP-Dual-Stack-Tarif beantragen, damit `www.frawo-tech.de` über IPv4 HTTPS erreichbar wird.
2. **Stockenweiler SSL** (Lane D): Zertifikat für `home.prinz-stockenweiler.de` über NPM UI oder Certbot CLI in LXC 103 erneuern.

## Nicht In Dieser Queue

- `Lane A: MVP Closeout` ist abgeschlossen; keine neuen Aufgaben für diesen Track.
- PBS-Rebuild und Surface-Go-Recovery sind Vollzertifizierungs-Track, nicht Teil des aktuellen Website-Releases.
- Google-Drive-Integration und UCG-Cutover folgen erst nach stabilem Public-Edge-Nachweis.

## Kanonische Steuerdateien

- `AI_OPERATING_MODEL.md` fuer das verbindliche AI-Arbeitsmodell
- `AI_SERVER_HANDOFF.md` fuer externen KI-Handoff
- `MASTERPLAN.md` fuer die strategische Lane-Reihenfolge
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md` als einzige Wahrheit fuer die MVP-Entscheidung
- `GEMINI.md` fuer delegierbare Browser- und Operator-Jobs
- `manifests/work_lanes/current_plan.json` als maschinenlesbare Lane-Quelle

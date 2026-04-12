# Operator Todo Queue

> **Solo Operator Quick Start:** Pick one item from **Next**, move it to **Doing**, finish it, move to **Done**.
> Don't add more than 3 items to Doing at once.

Stand: `2026-04-11` | Aktualisiert von: Codex

---

## Kanban Board

### 🔴 Blocked
*(Warte auf externen Input – Operator-Aktion erforderlich)*

| Task | Warum blockiert | Was danach? |
|------|-----------------|-------------|
| `public_edge_https_verified` (www.frawo-tech.de) | DS-Lite EasyBox 805 verhindert IPv4-Portforward; HTTPS braucht Cloudflare-Proxy oder ISP-Dual-Stack | `PUBLIC_EDGE_ARCHITECTURE_PLAN.md` → Cloudflare-Schritt |
| `stockenweiler_ssl_renewed` (home.prinz-stockenweiler.de) | SSL-Zertifikat abgelaufen seit April 2026; NPM UI oder Certbot-CLI nötig | `SESSION_HANDOVER_APRIL_2026.md` → SSL Renewal |

### 🟡 Next (Bereit zum Start)

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
| PBS-Erstinbetriebnahme + erster Restore-Drill | 2026-03-21 |
| Surface Go Frontend V1 live | 2026-03-25 |
| Radio AzuraCast live auf Pi | 2026-03-28 |
| MVP-Browserabnahme (Wolf + Franz) | 2026-03-30 |
| `strato_mail_model_verified` (webmaster, franz, noreply) | 2026-03-31 |
| `vaultwarden_recovery_material_verified` (2 Offline-Kopien) | 2026-04-09 |
| `device_rollout_verified` (Franz Surface + iPhone) | 2026-04-09 |
| DNS-Cutover frawo-tech.de auf VM220 (A/AAAA bei STRATO) | 2026-04-09 |
| Repo-Hygiene: .vault_pass entfernt, SECURITY.md hinzugefügt | 2026-04-09 |
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

- `Lane A: MVP Closeout` -> `completed` ✅ (release_mvp_gate = MVP_READY, alle manuellen Nachweise passed)
- `Lane B: Website/Public` -> `active` (DNS-Cutover done; HTTPS/IPv4 durch DS-Lite blockiert)
- `Lane C: Security/PBS/Infra` -> `watch` (PBS VM 240 gestoppt; monatliche Restore-Drills nötig)
- `Lane D: Stockenweiler` -> `watch` (SSL abgelaufen; yourparty-Payload sichern vor Ausdünnung)
- `Lane E: Radio/Media` -> `watch` (rpi_radio_integrated=no; Jellyfin TV noch nicht final)

## Manuelle Unblock-Punkte

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

# Operator Todo Queue

Stand: `2026-03-31`

## Zweck

Diese Datei ist ab jetzt nur noch die kurze manuelle Unblock-Queue.

Keine zweite Projektplanung, keine erledigte Historie, keine Nebenstrang-Roadmaps.
Der aktive Arbeitsfokus liegt in `Lane A: MVP Closeout`.

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

- `Lane A: MVP Closeout` -> `active`
- `Lane B: Website/Public Hold` -> `watch`
- `Lane C: Security/PBS/Infra` -> `watch`
- `Lane D: Stockenweiler` -> `watch`
- `Lane E: Radio/Media` -> `hold`

## Manuelle Unblock-Punkte

### `device_rollout_verified`

- `lane`: `Lane A: MVP Closeout`
- `goal`: Franz `Surface Laptop` und `iPhone` sind sichtbar als releasede MVP-Geraete abgenommen.
- `done_when`: Beide Geraete haben die erforderlichen Direktpfade und der echte Alltagspfad ist sichtbar bestaetigt.
- `blocked_by`: sichtbare Geraeteabnahme fehlt noch; aktuell zusaetzlich durch verlorenes Operator-Smartphone und den fehlenden `2FA`-Pfad blockiert
- `next_operator_action`: Erst den blockierten `2FA`-Pfad nach dem verlorenen Smartphone wiederherstellen, dann Franz `Surface Laptop` und `iPhone` im echten Alltagspfad pruefen und einen frischen sichtbaren Nachweis liefern.
- `next_codex_action`: Zuerst `python scripts/device_rollout_preflight.py`, danach `powershell -ExecutionPolicy Bypass -File .\scripts\prove_device_rollout.ps1` ausfuehren.

### `vaultwarden_recovery_material_verified`

- `lane`: `Lane A: MVP Closeout`
- `goal`: `Vaultwarden`-Recovery-Material existiert offline in zwei getrennten physischen Kopien.
- `done_when`: Zwei getrennte Offline-Kopien sind real vorhanden und frisch sichtbar nachgewiesen.
- `blocked_by`: frischer physischer Nachweis fehlt noch
- `next_operator_action`: Zwei getrennte Offline-Kopien des `Vaultwarden`-Recovery-Materials erstellen oder bestaetigen und den frischen Nachweis liefern.
- `next_codex_action`: Danach `python scripts/release_mvp_gate.py` und `python scripts/generate_ai_server_handoff.py` neu ziehen.

## Nicht In Dieser Queue

- `Lane B: Website/Public Hold` bleibt sichtbar, aber ohne neue Go-Live-Arbeit.
- `Lane C: Security/PBS/Infra` bleibt sichtbar, aber nur fuer Regressionen und Reapply-Pfade.
- `Lane D: Stockenweiler` bleibt sichtbar, aber ohne Live-Rollout.
- `Lane E: Radio/Media` bleibt im Erhaltungsmodus ohne Ausbau.

## Kanonische Steuerdateien

- `AI_OPERATING_MODEL.md` fuer das verbindliche AI-Arbeitsmodell
- `AI_SERVER_HANDOFF.md` fuer externen KI-Handoff
- `MASTERPLAN.md` fuer die strategische Lane-Reihenfolge
- `artifacts/release_mvp_gate/latest_release_mvp_gate.md` als einzige Wahrheit fuer die MVP-Entscheidung
- `GEMINI.md` fuer delegierbare Browser- und Operator-Jobs
- `manifests/work_lanes/current_plan.json` als maschinenlesbare Lane-Quelle

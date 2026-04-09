# Operator Todo Queue

Stand: `2026-04-09`

## Zweck

Diese Datei ist ab jetzt nur noch die kurze manuelle Unblock-Queue.

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

*(Aktuell keine ungeloesten Blocker)*

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

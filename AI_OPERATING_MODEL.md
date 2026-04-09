# AI Operating Model

Stand: `2026-03-31`

## Zweck

> [!IMPORTANT]
> Lies zuerst `AGENT_INSTRUCTIONS.md`, bevor du Änderungen vornimmst!

Dieses Dokument ist die kanonische Arbeitsregel dafuer, wie `Codex`, `Gemini` und der Operator zusammenarbeiten, bis der professionelle Betriebsstandard erreicht ist.

Es gilt als Default-Arbeitsmodell fuer:

- Planung
- Ausfuehrung
- Verifikation
- SSOT-Pflege

## Default-Modell

- Autonomie: `Aggressive Autopilot`
- Fuehrung: `Codex Lead`
- Gemini-Rolle: UCG test segment observation (2026-04-03/04):
  - Proxmox `vmbr0` now DHCPs as `10.1.0.92/24` with gateway `10.1.0.1`
  - UniFi UI reports the host as `10.1.0.20` in VLAN 101 (Anker-Server)
  - Potential MAC/IP overlap with `toolbox` detected in UniFi UI; track for cleanup

Das Ziel ist ein einziger kontrollierter Loop:

1. `read_only_truth`
2. `professional_check`
3. `change_classification`
4. `decision`
5. `post_verify`
6. `ssot_refresh`

## Change Classes

### `read_only`

- nur Truth Collection
- keine Repo-Mutation
- keine Runtime-Mutation

### `repo_only`

- Repo-Dokumentation, Generatoren, Manifeste, SSOT-Pflege
- keine Runtime-Aenderung

### `reversible_runtime`

- kontrollierte Runtime-Aenderung mit Rollback
- nur auf bereits beherrschten Pfaden
- immer mit Preflight und Post-Verify

### `gated_infra`

- Pflicht-Stopp vor Ausfuehrung
- nur nach expliziter Operator-Freigabe

## Pflicht-Stopps

Codex stoppt vor:

- `Infra/Public Changes`
- `Netzwerk`
- `Datenmigration`
- `Storage/PBS`
- `Router`
- `HA/PVE`
- `Security-Boundary`
- lokalen Windows-Admin-Token-Eingriffen
- allem Schwer-Rueckbaubaren oder Irreversiblen

## Rollen

### `Codex`

- plant
- klassifiziert Aenderungen
- fuehrt `read_only`, `repo_only` und erlaubte `reversible_runtime`-Schritte aus
- verifiziert nach jeder Mutation
- aktualisiert SSOT

### `Gemini`

- macht nur sichtbare Browser-/UI-/Acceptance-Pruefungen
- meldet exakten Ist-Zustand
- trifft keine Architekturentscheidungen
- fuehrt keine Infrastruktur- oder Repo-Aenderungen

### `Operator`

- entscheidet an Pflicht-Stopps
- fuehrt physische, 2FA-, Router-, Provider- oder Freigabehandlungen aus
- liefert sichtbare Nachweise fuer manuelle Gates

## Task-Packet-Standard

Jeder aktive Arbeitspunkt soll diese Felder fuehren:

- `lane`
- `goal`
- `done_when`
- `blocked_by`
- `next_operator_action`
- `next_codex_action`
- `change_class`
- `preflight_checks`
- `rollback_plan`
- `verification_commands`
- `last_verified_at`

## Prioritaetsreihenfolge

1. `Internal Ops First`
2. `Stockenweiler Bridge`
3. `Mandanten- und Daten-Trennung`
4. `Komplementaere Ressourcennutzung`
5. `Public`

## Praktische Regel

Kein neuer Schritt startet, solange:

- der vorige Schritt nicht verifiziert ist
- der vorige Schritt nicht im SSOT nachgezogen ist
- oder ein konkurrierender Zugriffspfad noch parallel offen haengt

## Kanonische Dateien

- `AGENT_INSTRUCTIONS.md` -> MUST READ FIRST for every agent.
- `AI_OPERATING_MODEL.md`
- `AI_SERVER_HANDOFF.md` -> Automated state summary for another AI.
- `manifests/work_lanes/current_plan.json`
- `OPERATOR_TODO_QUEUE.md`
- `GEMINI.md`
- `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`

# Document Ownership Operations

## Zweck

Jede Markdown-Seite im Workspace hat genau einen primaeren Bearbeiter:

- `wolfi`
- `gemini`
- `codex`

Das ist kein Deko-Label. Es ist die Arbeitssteuerung dafuer, wer eine Seite primaer weiterpflegt.

## Rollen

### `wolfi`

- Strategie
- Geschaefts- und Scope-Entscheidungen
- Identitaet
- finale fachliche Freigaben

### `gemini`

- Browser- und UI-getriebene Arbeitsseiten
- Checklisten
- Onboarding
- Nutzer- und Geraeteflows

### `codex`

- technische Operationsseiten
- Infrastruktur
- Audits
- Status
- Automations- und Gate-Dokumente

## Source Of Truth

- Manifest: `manifests/document_ownership/document_ownership.json`

## Checks

1. `make document-ownership-check`
2. `make document-ownership-report`

Diese Checks sind harte Gates in:

- `make start-day`
- `make close-day`
- `make stress-test`
- `make production-gate`

## Regeln

1. Jede `.md`-Datei muss genau einem Owner zugeordnet sein.
2. Doppelte Zuordnung ist nicht erlaubt.
3. Fehlende Zuordnung ist nicht erlaubt.
4. Generierte Reports unter `artifacts/**/*.md` gehoeren standardmaessig `codex`.
5. Bei neuer Datei muss die Ownership im Manifest im selben Arbeitsschritt gesetzt werden.
6. Eine neue `.md` ohne Owner blockiert bewusst den Workflow.

## Bedeutung

Ownership heisst:

- primaere Pflegeverantwortung
- erste Ansprechperson fuer Rueckbau, Umzug oder Aktualisierung

Ownership heisst nicht:

- dass andere die Datei nie anfassen duerfen

Andere duerfen beitragen. Aber die Seite hat immer genau einen primaeren Besitzer.

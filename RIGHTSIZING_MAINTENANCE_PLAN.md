# Rightsizing Maintenance Plan

## Ziel

Nextcloud und Odoo sind aktuell groesser konfiguriert, als es ihre echte Last rechtfertigt. Dieses Runbook beschreibt die saubere, reversible Wartungsreihenfolge fuer das Rightsizing.

## Scope

- `VM 200 nextcloud`
  - `4096 MB -> 2048 MB`
- `VM 220 odoo`
  - `4096 MB -> 2048 MB`

Bewusst nicht im Scope:

- `VM 210 HAOS`
- `VM 230 paperless`
- CPU-Aenderungen
- Disk-Aenderungen

## Warum

- Der Host ist auf Papier RAM-overcommitted.
- Nextcloud und Odoo sind die klaren Downsize-Kandidaten.
- HAOS ist dagegen bereits knapp, Paperless bewusst konservativer dimensioniert.

## Stage Gate

Vor der eigentlichen Aenderung muss folgendes gruen sein:

- `make rightsize-stage-gate`
- `make business-drift-check`
- frische lokale Backups fuer `VM 200` und `VM 220`
- Wartungsfenster vorhanden

## Dry-Run

```bash
make rightsize-plan
```

## Umsetzung

```bash
make rightsize-apply
```

Das Runbook macht:

1. Snapshot pro VM
2. kontrolliertes Shutdown
3. RAM-Anpassung
4. VM-Start
5. QGA-Check
6. HTTP-Verifikation

## Nachkontrolle

Direkt danach:

- `make business-drift-check`
- `make qga-check`
- `make backup-list`

Snapshots erst entfernen, wenn der Post-Change-Betrieb sauber bestaetigt ist.

## Rollback

Wenn nach dem Rightsizing ein Problem auftritt:

1. VM stoppen
2. alten Memory-Wert wieder setzen
3. alternativ auf den erstellten Snapshot zurueckgehen
4. Dienstcheck erneut fahren

# Wolf.EE Import Report

Stand: `2026-04-09`

## Ergebnis

Der erste kontrollierte Import von `Wolf.EE` in den zentralen Medienpfad wurde erfolgreich ausgefuehrt.

Zielpfad:

- `/mnt/data/media/yourparty_Libary/incoming/Wolf_EE_20260409`

Importierte Quellordner:

- `Job Jobse`
- `The_TraXx`
- `Sets`
- `MUSIK`

Verifizierte Zielgroessen:

- `Job Jobse`: `438M`
- `The_TraXx`: `2.7G`
- `Sets`: `3.7G`
- `MUSIK`: `6.5G`
- gesamt: ca. `14G`

## Medienpfad

Der produktive Medienpfad fuer `Jellyfin` ist weiter:

- `CT 100 toolbox`
- read-only Bind: `/srv/media-library`
- Netzwerk-Musikpfad: `/srv/media-library/music-network`
- Source: `//10.1.0.30/Media`

## Wolf.EE Bewertung

`Wolf.EE` wurde bewusst nur read-only gemountet:

- Device: `/dev/sda2`
- Label: `Wolf.EE`
- Mountpoint: `/mnt/wolf-ee`
- Mount-Optionen: `ro`

Nicht importiert wurden:

- `Nicotine`
- `von HDD`
- `Plugins`
- `StudioOne`
- `$RECYCLE.BIN`

Grund:

- teils gemischte oder offensichtlich nicht-mediale Inhalte
- teils hoher Datenballast
- weiterer Import waere aktuell kapazitaetskritisch

## Kapazitaet

Der `storage-node` steht nach dem Import bei:

- `84G` genutzt
- `9.1G` frei
- `91%` Belegung

Das ist eine klare Stopplinie fuer weitere groessere Medienimporte in diesem Block.

## Stockenweiler

Ein direkter `Stockenweiler`-Quellpfad wurde in dieser Session nicht live eingebunden.

Live-Befund:

- von `toolbox` aktuell keine Route / kein Ping nach `192.168.178.25`

Folge:

- `Stockenweiler` ist fuer diesen Abend kein belastbarer Live-Importpfad
- zuerst Medien-/Kapazitaetslage auf Anker stabil halten

## Naechste Reihenfolge

1. Review der importierten Ordner in `incoming/Wolf_EE_20260409`
2. nur brauchbares Material von dort weiter nach `clean` oder `curated`
3. erst danach ueber Restimporte wie `Nicotine` oder `von HDD` entscheiden
4. `Stockenweiler` erst wieder anfassen, wenn der Remote-Pfad read-only verifiziert ist

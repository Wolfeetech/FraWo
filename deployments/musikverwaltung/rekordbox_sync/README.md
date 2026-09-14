# Rekordbox <-> AzuraCast Sync — Notizen

## Pfad-Uebersetzung (bestaetigt 2026-08-17)

AzuraCast-Pfad ist direkt relativ zu `M:\` — **kein** Praefix wie
`Master_Library\` noetig. Beispiel, live gegen die echte API und das
echte Laufwerk geprueft:

```
AzuraCast: "Curated_Playlists/Ch1_Acoustik_Ambient/Mac Miller feat. Delusional Thomas - Transformations.flac"
Rekordbox: "M:\Curated_Playlists\Ch1_Acoustik_Ambient\Mac Miller feat. Delusional Thomas - Transformations.flac"
```

Regel: `rekordbox_pfad = "M:\" + azuracast_pfad.replace("/", "\\")`

## Bekannte API-Einschraenkung

`GET /api/station/1/files` antwortet mit HTTP 500 (leerer Body), sowohl
mit als auch ohne Paginierung. Passt zum dokumentierten Verdacht einer
Absturzschleife im AzuraCast-Worker (Odoo #964) — nicht extra debuggt,
stattdessen Workaround:

1. `GET /api/station/1/playlists` — Liste aller Playlisten
2. `GET /api/station/1/playlist/{id}/queue` — Titel je Playlist (liefert `media_id`, aber keinen Pfad)
3. `GET /api/station/1/file/{media_id}` — liefert `path` + `playlists`-Zuordnung je Titel

Funktioniert zuverlaessig (200 OK, live getestet), nur mit mehr
Einzelanfragen statt einer Sammel-Abfrage.

## Sterne-Export aus Odoo in Rekordbox (`rating_export.py`)

- **Zweck:** Synchronisiert publikumskurierte Track-Bewertungen (1–5 Sterne) von `frawo.tech/radio` in die lokale Rekordbox-Datenbank (`%APPDATA%\Pioneer\rekordbox\master.db`).
- **Ablauf:**
  1. Prozessprüfung: bricht sofort ab, falls `rekordbox.exe` oder `rekordboxAgent.exe` läuft (Schutz vor SQLite-Locks).
  2. Ruft `/radio/ratings/export` token-geschützt ab (mindestens 2 Bewertungen je Titel, Schnitt kaufmännisch gerundet).
  3. Matcht Titel & Künstler exakt/case-insensitive gegen Rekordbox-Content.
  4. Aktualisiert das native Feld `DjmdContent.Rating` (1–5).
  5. Pflegt die Playlist **`🔥 Publikums-Favoriten`** (alle Titel mit $\ge 4$ Sternen).
- **Log:** `rating_export.log` im gleichen Verzeichnis.
- **Automatisierung:** `rating_export.cmd` kann über die Windows-Aufgabenplanung stündlich ausgeführt werden:
  `schtasks /create /tn "FraWo-Radio-Rekordbox-Sterne-Export" /tr "\"C:\Users\StudioPC\FraWo\deployments\musikverwaltung\rekordbox_sync\rating_export.cmd\"" /sc hourly /f`

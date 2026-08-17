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

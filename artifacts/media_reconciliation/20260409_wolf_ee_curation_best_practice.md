# Wolf.EE Curation Best Practice

Stand: `2026-04-09`

## Verwendete Leitlinien

- `rekordbox` empfiehlt explizite Library-Backups statt blindem Umbau auf dem Live-Bestand.
- `MusicBrainz Picard` arbeitet aus vorhandenen Metadaten und Clustern statt aus blindem Umbenennen.
- `beets` dokumentiert duplicate-aware Library-Pflege und trennt Import-/Kurationsschritte.
- `Serato` warnt bei Cloud-/Sync-Eingriffen vor Datenverlust und empfiehlt vorherige Backups.

Quellen:

- https://cdn.rekordbox.com/files/20210816172003/rekordbox6.5.3_device_library_backup_guide_EN.pdf
- https://picard-docs.musicbrainz.org/downloads/MusicBrainz_Picard_v2.12_%5Ben%5D.pdf
- https://beets.readthedocs.io/_/downloads/en/v1.6.0/pdf/
- https://support.serato.com/hc/en-us/articles/115000399234-KNOWN-ISSUE-Using-iCloud-Music-Library-can-result-in-the-loss-of-Serato-data

## Abgeleitete Regeln fuer FraWo

1. `incoming` ist nur fuer frische Rohimporte.
2. `review` ist fuer sichtbare, noch nicht freigegebene Sortierarbeit.
3. `bulk` ist fuer grosse Massenbloecke, die nicht live im Arbeitskorb liegen sollen.
4. `archive` oder externe Review-Ziele halten Rohmaterial und Caches, die nicht in `clean` gehoeren.
5. Referenzsets, Download-Pools und Release-Packs werden getrennt gehalten.
6. Originals werden nicht blind umgetaggt oder geloescht, solange keine saubere Sichtung vorliegt.
7. Generische Download-Pools und Recording-Caches werden nicht als kuratierte Library behandelt.

## Umgesetzter Wolf.EE-Pfad

- `incoming/Wolf_EE_20260409` wurde aufgeloest.
- `bulk/Wolf_EE_20260409/MUSIK`
  - grosser generischer Massenblock, aktuell kein Live-Arbeitskorb
- `review/Wolf_EE_20260409/reference_sets/source_series/essential_mixes`
  - vormals `Sets/! Essential Mixes`
- `review/Wolf_EE_20260409/reference_sets/misc_reference_sets/record_data`
  - vormals `Sets/Record - Data`
- `review/Wolf_EE_20260409/release_packs/job_jobse_releases`
  - vormals `Job Jobse`
- `review/Wolf_EE_20260409/download_pools/source_pools/nicotone`
  - vormals `The_TraXx/nicotone`
- `review/Wolf_EE_20260409/download_pools/genre_buckets/genre_pool`
  - vormals `The_TraXx/Genre`
- `review/Wolf_EE_20260409/download_pools/artist_buckets/artist_pool`
  - vormals `The_TraXx/Artist`

## Naechster Best-Practice-Schritt

1. `reference_sets` in spaetere Untergruppen aufteilen:
   - `essential_mix`
   - spaeter optional `radio_sets`
   - spaeter optional `live_recordings`
2. `download_pools` spaeter nach Quelle auftrennen:
   - `beatport_pools`
   - weitere `artist_pools`
   - weitere `genre_pools`
3. `release_packs` erst nach Dubletten-/Metadatenpruefung partiell nach `clean` uebernehmen.

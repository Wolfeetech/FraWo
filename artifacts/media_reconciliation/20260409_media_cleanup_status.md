# Media Cleanup Status

Stand: `2026-04-09`

## Ergebnis dieses Blocks

- `Stockenweiler` ist wieder als technische Sichtungsquelle offen.
- `toolbox` nimmt seit diesem Block Tailscale-Subnetzrouten an.
- `ping 192.168.178.25` von `CT 100 toolbox` ist erfolgreich.
- Die lokale Zusatz-SSD `music_ssd` ist **nicht** als verlaesslicher Offload-Pfad zu werten:
  - `fsck.exfat -p` brachte sie kurz auf `rw`
  - unter Schreiblast fiel sie erneut auf `ro`
- Der erste echte Platzgewinn ist umgesetzt:
  - `studiopc-import-2026-03-25` wurde als Review-Archiv nach `Stockenweiler:/mnt/data_family/FraWo_review_imports_archives/` ausgelagert
  - `storage-node` sank dadurch von ca. `91%` auf ca. `86%`
  - `proxmox-anker` sank nach Entfernen der Zwischenarchive von ca. `93%` auf ca. `85%`
- `incoming` ist jetzt wieder sauber:
  - `studiopc-import-2026-03-25` ist komplett aus dem Live-Eingang entfernt
  - `Wolf_EE_20260409` wurde in `bulk` und `review` getrennt
  - `incoming/` ist aktuell leer

## Verifizierte Quellen

### Anker / produktiver Medienpfad

- `CT 110 storage-node`
- Pfad: `/mnt/data/media/yourparty_Libary`
- Hauptbereiche:
  - `clean` ca. `65G`
  - `incoming` ca. `18G`

### Incoming auf storage-node

- `/mnt/data/media/yourparty_Libary/incoming/Wolf_EE_20260409`
  - nach dem Cleanup nur noch `MUSIK` `6.5G`
- `/mnt/data/media/yourparty_Libary/incoming/studiopc-import-2026-03-25`
  - nach dem Cleanup nur noch `IMPORT_NOTES.txt`

### Review-Pfad auf storage-node

- `/mnt/data/media/yourparty_Libary/review/Wolf_EE_20260409`
  - `release_packs/job_jobse_releases` `438M`
  - `download_pools/source_pools/nicotone` plus `artist_buckets` und `genre_buckets` zusammen vormals `The_TraXx` `2.7G`
  - `reference_sets/source_series/essential_mixes` plus `misc_reference_sets/record_data` zusammen vormals `Sets` `3.7G`

### Ausgelagerte Review-Archive auf Stockenweiler

- Zielpfad: `/mnt/data_family/FraWo_review_imports_archives`
- verifiziert:
  - `studio-one-media.tar` `157M`
  - `mixxx-recordings.tar` `409M`
  - `onedrive-mixxx-recordings.tar` `1.5G`
  - `studio-one-cache-audio.tar` `3.2G`

### Stockenweiler

- Host: `stockenweiler-pve`
- Musikquelle: `/mnt/music_hdd/yourparty_Libary`
- Verifizierte Groessen:
  - `radio_nas` `179G`
  - `UNSORTED` `97G`
  - `HOUSE` `2.1G`
  - `TECHNO (RAW _ DEEP _ HYPNOTIC)` `2.0G`
  - `MINIMAL _ DEEP TECH` `1.4G`
  - `Franz Import` `433M`
- Weitere Kapazitaet:
  - `/mnt/data_family` rund `102G` frei
  - `/mnt/music_hdd` selbst praktisch voll

## Aufraeum-Einordnung

- `studiopc-import-2026-03-25` ist kein produktiver Library-Bestand, sondern fast komplett Recording-/Cache-Material.
- `Wolf_EE_20260409` ist klarer Review-Bestand, aber in sich besser strukturiert als `studiopc-import`.
- Die grossen Stockenweiler-Bloecke `radio_nas` und `UNSORTED` sind vorerst Sichtungsmasse, kein Kandidat fuer Blindimporte.

## Saubere Prioritaet ab jetzt

1. `studiopc-import-2026-03-25` zuerst fachlich entscheiden:
   - behalten als Archiv
   - oder spaeter gezielt auslagern/loeschen
2. `Wolf_EE_20260409` nur kuratiert weiterverteilen:
   - `Job Jobse`, `Sets`, `The_TraXx` liegen jetzt bereits sauber im Review-Pfad
   - `Sets` und `The_TraXx` sind dort bereits weiter in sprechende Untergruppen zerlegt
   - `MUSIK` liegt als letzter grosser Bulkblock unter `bulk/Wolf_EE_20260409`
3. `Stockenweiler` nur in kleinen, thematisch klaren Chargen sichten:
   - `HOUSE`
   - `TECHNO (RAW _ DEEP _ HYPNOTIC)`
   - `MINIMAL _ DEEP TECH`
4. `radio_nas` und `UNSORTED` erst anfassen, wenn wieder ein belastbarer Offload-/Sortierpfad existiert.

## Wichtige Guardrails

- Keine weiteren grossen Importe auf `storage-node`, solange dort nur ca. `9G` frei sind.
- `music_ssd` nicht als vertrauenswuerdiges Ziel behandeln, bis die exFAT-Stabilitaet wirklich nachgewiesen ist.
- `Stockenweiler` ist jetzt wieder erreichbar, aber nicht automatisch ein Zielsystem; zuerst als Quelle denken.

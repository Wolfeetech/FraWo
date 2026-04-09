# Media Cleanup Status

Stand: `2026-04-09`

## Ergebnis dieses Blocks

- `Stockenweiler` ist wieder als technische Sichtungsquelle offen.
- `toolbox` nimmt seit diesem Block Tailscale-Subnetzrouten an.
- `ping 192.168.178.25` von `CT 100 toolbox` ist erfolgreich.
- Die lokale Zusatz-SSD `music_ssd` ist **nicht** als verlaesslicher Offload-Pfad zu werten:
  - `fsck.exfat -p` brachte sie kurz auf `rw`
  - unter Schreiblast fiel sie erneut auf `ro`
- `storage-node` bleibt deshalb der aktuelle Druckpunkt mit ca. `91%`.

## Verifizierte Quellen

### Anker / produktiver Medienpfad

- `CT 110 storage-node`
- Pfad: `/mnt/data/media/yourparty_Libary`
- Hauptbereiche:
  - `clean` ca. `65G`
  - `incoming` ca. `18G`

### Incoming auf storage-node

- `/mnt/data/media/yourparty_Libary/incoming/Wolf_EE_20260409`
  - `MUSIK` `6.5G`
  - `Sets` `3.7G`
  - `The_TraXx` `2.7G`
  - `Job Jobse` `438M`
- `/mnt/data/media/yourparty_Libary/incoming/studiopc-import-2026-03-25`
  - `studio-one-cache-audio` `2.5G`
  - `onedrive-mixxx-recordings` `1.5G`
  - `mixxx-recordings` `258M`
  - `studio-one-media` `157M`
  - `IMPORT_NOTES.txt`

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
   - zuerst `Job Jobse`, `Sets`, `The_TraXx`
   - `MUSIK` zuletzt, weil groesster Block
3. `Stockenweiler` nur in kleinen, thematisch klaren Chargen sichten:
   - `HOUSE`
   - `TECHNO (RAW _ DEEP _ HYPNOTIC)`
   - `MINIMAL _ DEEP TECH`
4. `radio_nas` und `UNSORTED` erst anfassen, wenn wieder ein belastbarer Offload-/Sortierpfad existiert.

## Wichtige Guardrails

- Keine weiteren grossen Importe auf `storage-node`, solange dort nur ca. `9G` frei sind.
- `music_ssd` nicht als vertrauenswuerdiges Ziel behandeln, bis die exFAT-Stabilitaet wirklich nachgewiesen ist.
- `Stockenweiler` ist jetzt wieder erreichbar, aber nicht automatisch ein Zielsystem; zuerst als Quelle denken.

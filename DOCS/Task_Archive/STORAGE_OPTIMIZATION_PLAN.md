# Storage Optimization Plan

## Ziel

Speicherdruck auf `Anker` und `Stockenweiler` geordnet abbauen, ohne Backup-Pfade, Medienpayload oder Business-Daten blind zu beschaedigen.

Der bindende Ist-Stand kommt aus:

- `artifacts/platform_health/latest_report.md`
- `artifacts/stockenweiler_inventory/latest_pve_storage_probe.md`
- `artifacts/storage_optimization/latest_report.md`

## Harter Ist-Stand

### Anker

- `local` ist sichtbar genutzt, aber nicht die akuteste Baustelle
- `local-lvm` ist genutzt, aber ebenfalls nicht der erste Engpass
- `/var/lib/vz/dump` belegt rund `24 GiB`
- `PBS` ist weiterhin nicht gruen genug, um jetzt aggressiv an Backup-Zielen herumzubauen

### Stockenweiler

Das ist die eigentliche Speicher-Baustelle.

- `hdd-backup` ist hoch ausgelastet
- `data_family/proxmox_backups` ist der groesste klar identifizierte Reclaim-Hebel
- `music_hdd` ist fuer produktive Arbeit zu voll und muss klassifiziert werden

## Prioritaeten

### 1. Backup-Retention in Stockenweiler korrigieren

Erster echter Hebel:

- `VM 210`-Dumps nicht unbegrenzt halten
- `VM 360`-Dumps nicht unbegrenzt halten
- nur nach kept-set-Pruefung auf `letzte 2` reduzieren

### 2. Kalte Raw-Archive pruefen

`proxmox_backups/images/*` ist teurer kalter Speicher und muss als Archiv explizit bewertet werden.

Entscheid pro Image:

- `keep for now`
- `export then delete`
- `delete after verification`

### 3. music_hdd klassifizieren

Reihenfolge:

- `Inbox`
- `yourparty_Libary`
- dann erst die grosse `Library`

Die grossen `Library`-Kategorien sind kein Kandidat fuer blindes Loeschen, sondern fuer:

- behalten lokal
- nach `Anker` migrieren
- offline archivieren

### 4. PBS zuerst gruen machen

Bevor neue Backup- oder Storage-Rollen verteilt werden:

- `PBS` auf `Anker` muss wieder belastbar sein
- erst danach duennen wir lokal und retargeten Backups

### 5. Anker erst spaeter anfassen

`Anker` ist derzeit nicht der erste Druckpunkt.

Dort gilt:

- nichts ueberhastet aus `/var/lib/vz/dump` loeschen
- erst PBS/Pfad gruen
- dann Retention/Offload entscheiden

## Konkrete Reihenfolge

1. `stockenweiler` Backup-Reclaim vorbereiten
2. kept-set fuer `VM 210` und `VM 360` sichtbar festlegen
3. danach alte Dumps entfernen
4. Raw-Image-Archive klassifizieren
5. `music_hdd/Inbox` und `yourparty_Libary` bereinigen oder auslagern
6. `PBS` auf `Anker` stabilisieren
7. erst dann `Anker`-Dump-Retention optimieren

## Nicht tun

- keine Blind-Loeschung auf `music_hdd`
- keine Raw-Image-Loeschung ohne Klassifikation
- keine neue Stockenweiler-Backup-Rolle vor dem Reclaim
- keine grossen Migrationen, solange `PBS` nicht gruen ist

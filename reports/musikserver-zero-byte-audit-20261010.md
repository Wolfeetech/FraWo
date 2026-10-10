# Musikserver: 0-Byte-Audit — 2026-10-10

## Umfang

Read-only-Prüfung auf CT120 (`fileserver`, stock-pve) unter `/mnt/music/Master_Library`.
Es wurden keine Dateien verschoben, gelöscht oder verändert.

## Ergebnis

- 7.648 Dateien mit 0 Byte in `Master_Library`
- davon 7.634 NTFS-Rückstandsdateien mit Namensmuster `*.ntfs-3g-*`
- davon 14 echte 0-Byte-Audiodateien ohne dieses Rückstandsmuster
- `00_INBOX`: 0 0-Byte-Dateien
- `_STAGING_RAW`: 0 0-Byte-Dateien

Die 7.634 NTFS-Dateien sind keine normalen sendefähigen Audiodateien, sondern offenbar beim NTFS-/SMR-Zugriff entstandene Rückstandsdateien. Diese Einordnung ist ein Prüfhinweis, noch keine Löschfreigabe.

## 14 echte 0-Byte-Audiodateien

- Isaac Tichauer — Higher Level (Bicep Remix)
- DJ Python — Mare
- LF SYSTEM — Afraid to Feel (Gerd Janson remix)
- Helmut & Roy — He Chilled Out
- Kendal — Ritmo Fatale
- Marlon Hoffstadt — Blade Runner
- Marlon Hoffstadt — Don't Worry My Son, It Will All Be Good
- Marlon Hoffstadt — Planet Love
- Marlon Hoffstadt — Lost In A Feed
- Marlon Hoffstadt — Mucho Intensivo
- Matthias Meyer & Budakid — Sweet Ease
- Loods — Pure Bliss Meltdown
- Da Klubb Kings — It's Time 2 Get Funky (Klubb Mix)
- Rozalla x Dave Ralph — Everybody's Free (Paul Oakenfold extended Nu Rave remix)

## Quellenabgleich (read-only)

Für alle 14 echten 0-Byte-Titel wurden lokale, nichtleere Kandidaten gefunden. Die Kandidaten liegen in Inbox, Master_Library oder Quarantäne; sie wurden nicht zurückgelegt. Stichproben- und Vollprüfung der ausgewählten größten Kandidaten mit `ffprobe` war erfolgreich: FLAC, Stereo, 44,1 kHz, Dauerwerte vorhanden.

Damit ist der nächste Schritt kein blindes Wiederherstellen, sondern eine kontrollierte Zuordnung pro Titel:

- Quelle auswählen und gegen die leere Zielposition vergleichen.
- Aktive Sendelinks und vorhandene Playlist-Mitgliedschaften prüfen.
- Vor jedem Zurücklegen ein Dateibackup und ein Manifest mit Quelle, Ziel, Größe, Dauer und Fingerprint erzeugen.
- Nur die 14 echten Audiodateien behandeln; die 7.634 NTFS-Rückstände separat als Dateisystem-/Kopierartefakte untersuchen.


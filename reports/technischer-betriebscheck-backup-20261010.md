# Technischer Betriebscheck — Sicherungskette — 2026-10-10

## Befund

Der Backup-TÜV war am 10.10.2026 nicht grün:

- ProDesk: `vm220_cloud` fehlgeschlagen; lokale VM-220-Sicherung vom 04.10.2026 vorhanden, Cloud-Nachweis fehlte.
- Anker: `gaeste_cloud` fehlgeschlagen; Google Drive antwortete mit `403 RATE_LIMIT_EXCEEDED`.

## Ursachenabgleich

1. Auf dem Anker lief noch ein veralteter rekursiver `find /mnt/google-drive`-Prozess vom globalen Musik-Fingerprintlauf. Dieser Prozess war seit 09.10. aktiv und erzeugte unnötige Drive-API-Abfragen. Er wurde am 10.10. beendet. Es wurden keine Drive-Dateien verändert.
2. Auf dem ProDesk läuft zusätzlich der reguläre Musik-Cloud-Abgleich. Dieser nutzt dasselbe Google-Drive-Projekt und konkurriert mit anderen Drive-Abfragen.
3. Die VM-Cloud-Sicherung läuft täglich für VM 360 und sonntags für VM 220. Der letzte reguläre VM-220-Lauf war am 04.10.2026; die Cloud-Prüfung konnte den erwarteten Bestand am 10.10. nicht mehr lesen.

## Kontrollierte Maßnahme

Der vorhandene, unveränderte Upload-Befehl für die geprüfte lokale VM-220-Sicherung vom 04.10.2026 wurde erneut gestartet:

`vzdump-qemu-220-2026_10_04-03_00_02.vma.zst`

Quelle und Zielgröße werden nach Abschluss erneut geprüft. Während des Laufs werden keine Proxmox-Knoten und keine Gäste neu gestartet.

## Offen bis zum Abschluss

- Upload erfolgreich abgeschlossen und Zielgröße identisch
- `vm220_cloud` im Backup-TÜV wieder grün
- `gaeste_cloud` nach Abklingen des Drive-Rate-Limits erneut lesbar
- dauerhafte Sperre gegen globale Rekursivscans über den produktiven Drive-Mount

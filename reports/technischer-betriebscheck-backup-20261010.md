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

Der Upload ist am 10.10.2026 normal mit Exit-Code 0 beendet worden. Die Datei ist im Zielbestand vorhanden; der Backup-TÜV auf dem ProDesk bestätigt `vm220_cloud` mit 17 GB als bestanden. Während des Laufs wurden keine Proxmox-Knoten und keine Gäste neu gestartet.

## Aktueller Nachweis

- ProDesk-TÜV: **6 von 6 Prüfungen bestanden**.
- `vm220_cloud`: **bestanden**, 17 GB, Sicherung vom 04.10.2026.
- Anker-TÜV: 6 von 7 Prüfungen bestanden.
- Offen bleibt ausschließlich `gaeste_cloud`: Der direkte Google-Drive-Lesezugriff erhält weiterhin `403 RATE_LIMIT_EXCEEDED` vom Drive-Projekt. Der verschlüsselte Mount ist aktiv und enthält lokal einen Gast-Backup-Bestand; die externe Direktprüfung ist wegen des API-Limits noch nicht belastbar.

## Nächster technischer Schritt

Nach Abklingen des Google-Drive-API-Limits erneut direkt prüfen. Erst danach wird `gaeste_cloud` als grün gemeldet. Der alte globale Rekursivscan bleibt beendet; zusätzlich muss die dauerhafte Sperre gegen solche Scans umgesetzt werden.

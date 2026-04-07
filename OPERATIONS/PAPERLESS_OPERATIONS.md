# Paperless Operations

## Zweck

Paperless ist das Dokumentenarchiv mit OCR- und Ablageworkflow.

## Zugriff

- `http://paperless.hs27.internal/accounts/login/`

## Normalbetrieb

- persoenliche Konten fuer `wolf` und `franz`
- Scans kommen standardisiert ueber Nextcloud `Paperless/Eingang`
- Archivpfad bleibt nachvollziehbar und reproduzierbar

## T?gliche Checks

- Login funktioniert
- neuer Scan wird ?bernommen
- OCR/Archivierung funktionieren
- Bridge-Timer arbeitet weiter

## Nie tun

- keine parallelen manuellen Importpfade ohne Dokumentation aufbauen
- kein Shared-Admin als Normalbetrieb

## Eskalation

- bei fehlenden Dokumenten zuerst Nextcloud-Zielordner, dann Bridge, dann Paperless-Consume pr?fen

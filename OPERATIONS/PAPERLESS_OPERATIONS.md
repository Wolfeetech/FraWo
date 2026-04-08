# Paperless Operations

## Zweck

Paperless ist das Dokumentenarchiv mit OCR- und Ablageworkflow.
Die uebergeordnete Storage-Trennung steht in `OPERATIONS/STORAGE_INTEGRATION_OPERATIONS.md`.

## Zugriff

- `http://paperless.hs27.internal/accounts/login/`

## Normalbetrieb

- persoenliche Konten fuer `wolf` und `franz`
- Scans kommen standardisiert ueber Nextcloud `Paperless/Eingang`
- Archivpfad bleibt nachvollziehbar und reproduzierbar
- Paperless bleibt ein eigenes Archivsystem und schreibt nicht in das Nextcloud-Datadir

## T?gliche Checks

- Login funktioniert
- neuer Scan wird ?bernommen
- OCR/Archivierung funktionieren
- Bridge-Timer arbeitet weiter

## Nie tun

- keine parallelen manuellen Importpfade ohne Dokumentation aufbauen
- kein Shared-Admin als Normalbetrieb
- keinen Paperless-Media- oder Consume-Pfad direkt als allgemeines Shared-Filesystem fuer andere Apps zweckentfremden

## Eskalation

- bei fehlenden Dokumenten zuerst Nextcloud-Zielordner, dann Bridge, dann Paperless-Consume pr?fen

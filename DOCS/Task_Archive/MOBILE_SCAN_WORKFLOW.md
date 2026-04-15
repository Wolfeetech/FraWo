# Mobile Scan Workflow

## Ziel

Franz und Wolf sollen Dokumente mobil erfassen koennen, ohne lokale Bastelpfade oder manuelle Serverzugriffe.

## Standardfluss

1. Dokument mit dem Handy scannen.
2. Scan in Nextcloud nach `Paperless/Eingang` hochladen.
3. Die bestehende Bridge auf `VM 230 paperless` uebernimmt den Import.
4. Paperless fuehrt OCR und Archivierung aus.
5. Das Dokument landet in Paperless und wird nach `Paperless/Archiv` gespiegelt.

## Kanonische Orte

- Nextcloud Upload-Ziel: `Paperless/Eingang`
- Paperless Zielsystem: `VM 230 paperless`
- Nextcloud Quelle: `VM 200 nextcloud`

## Benutzerbild

- `wolf` nutzt seinen persoenlichen Nextcloud- und Paperless-Account.
- `franz` nutzt seinen persoenlichen Nextcloud- und Paperless-Account.
- `frontend` ist kein Primaerpfad fuer persoenliche Dokumente.

## Mobile Empfehlung

- Scan-App oder Dateiupload aufs Handy
- Upload direkt in die Nextcloud-App
- keine Ablage in verstreuten Messenger- oder Galerie-Pfaden

## Abnahme

1. Handy off-LAN testen.
2. Beispiel-PDF oder echter Scan nach `Paperless/Eingang` hochladen.
3. In Paperless pruefen, ob das Dokument erscheint.
4. In Nextcloud pruefen, ob die Archivspiegelung nach `Paperless/Archiv` erfolgt.

## Betriebsgrenzen

- Der Workflow ist fuer Dokumente und Scans gedacht, nicht fuer beliebige grosse Medienimporte.
- Persoenliche Ordnung entsteht spaeter ueber konsistente Ablageorte, Tags und Nextcloud-Struktur.

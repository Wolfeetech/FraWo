# Wolf Und Franz Handout

## Zweck

Dieses Handout sagt klar, wie ihr mit dem aktuellen System weiterarbeitet, ohne erst den ganzen Masterplan lesen zu muessen.

## 1. Einstieg

- Standard-Einstieg intern: `http://portal.hs27.internal`
- Falls das Portal nicht reicht:
  - `Nextcloud`: `http://cloud.hs27.internal`
  - `Paperless`: `http://paperless.hs27.internal`
  - `Odoo`: `http://odoo.hs27.internal/web/login`
  - `Home Assistant`: `http://ha.hs27.internal`
  - `Jellyfin`: `http://media.hs27.internal`
  - `Radio`: `http://radio.hs27.internal`

## 2. Wo liegen die Logins

Aktuell noch als Arbeitsstand:

- `ACCESS_REGISTER.md`

Zielzustand:

- `Bitwarden Cloud`

Wichtig:

- `ACCESS_REGISTER.md` ist nur Uebergang
- neue oder geaenderte produktive Passwoerter gehoeren danach nach `Bitwarden`

## 3. Wie arbeitet Wolf jetzt

### Alltag

- `Nextcloud` fuer Dateien, Ablagen und gemeinsame Ordner
- `Paperless` fuer Dokumente und OCR-Archiv
- `Odoo` fuer Betriebs- und Geschaeftsprozesse
- `Home Assistant` fuer Haus-/Geraetestatus

### Admin

- `AzuraCast` nur fuer Radioverwaltung
- `Jellyfin root` nur als technischer Break-Glass-Admin
- `AdGuard` nur lokal und nur bei DNS-/Frontdoor-Arbeiten

## 4. Wie arbeitet Franz jetzt

### Alltag

- `Nextcloud` fuer Dateien und Eingangsordner
- `Paperless` fuer Dokumente, Suche und Archiv
- `Odoo` fuer definierte Geschaeftsprozesse
- `Jellyfin` und `Radio` fuer Medien

### Geplanter Mobile-Scan-Weg

1. mit dem Handy scannen
2. Datei nach Nextcloud `Paperless/Eingang` hochladen
3. Bridge uebergibt an Paperless
4. OCR und Archivierung laufen dort weiter

Details:

- `MOBILE_SCAN_WORKFLOW.md`

## 5. Was ist aktuell wirklich live

Stand `2026-03-26`:

- alle Kern-URLs antworten intern mit `HTTP 200`
- `Media` und `Radio` laufen auf dem kanonischen SMB-Pfad
- personenbezogene Konten fuer `wolf` und `franz` sind in den Kern-Apps angelegt
- `Bitwarden` und reale `STRATO`-Mailboxen sind noch offen

## 6. Was ist noch nicht fertig

- produktive Secret-Ablage in `Bitwarden Cloud`
- reale Mailboxen bei `STRATO`
- finaler Website-Release
- live bestaetigter Rollout des neuen Portal-`Anmeldeboards`
- Surface-Frontend

## 7. Was jetzt in der richtigen Reihenfolge passiert

1. `Bitwarden Cloud` einrichten
2. Logins aus `ACCESS_REGISTER.md` uebernehmen
3. `STRATO`-Mailboxen anlegen
4. Systemmails sauber auf `noreply@frawo-tech.de` standardisieren
5. internen Stresstest fahren
6. Website-Release `www.frawo-tech.de`

## 8. Wenn etwas kaputt wirkt

Zuerst pruefen:

1. `PLATFORM_STATUS.md`
2. `OPS_HOME.md`
3. `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`

Wenn nur ein Dienst betroffen ist, direkt die passende Betriebsanweisung oeffnen:

- `OPERATIONS/NEXTCLOUD_OPERATIONS.md`
- `OPERATIONS/PAPERLESS_OPERATIONS.md`
- `OPERATIONS/ODOO_OPERATIONS.md`
- `OPERATIONS/JELLYFIN_OPERATIONS.md`
- `OPERATIONS/AZURACAST_OPERATIONS.md`

## 9. Nicht tun

- keine neuen produktiven Passwoerter nur in Markdown liegen lassen
- keine oeffentlichen Admin-UIs freigeben
- keine neue Domain live schalten, bevor `Bitwarden` und `STRATO` sauber stehen

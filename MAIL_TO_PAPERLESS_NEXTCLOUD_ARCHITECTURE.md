# Mail To Paperless And Nextcloud Architecture

Stand: `2026-03-26`

## Ziel

Mails sollen direkt am richtigen Ort landen, ohne einen eigenen Mailserver zu betreiben.

## Grundsatz

- `STRATO` bleibt Mail-Provider
- Apps senden ueber `STRATO SMTP`
- Eingehende Mails bleiben zuerst in `STRATO`
- der Server holt nur die dafuer vorgesehenen Mails gezielt ab
- ein eigener Mailserver auf dem Homeserver ist nicht Teil dieser Phase

## Mailboxen Und Rollen

- `wolf@frawo-tech.de`
  - sichtbare Arbeitsidentitaet von Wolf, technisch ueber `webmaster@...`
- `franz@frawo-tech.de`
  - persoenlicher Hauptaccount von Franz
- `info@frawo-tech.de`
  - Kontakt und normale Inbound-Kommunikation
- `noreply@frawo-tech.de`
  - Systemmails aus Apps
- der technische Zielpfad fuer `info` und `noreply` ist noch gegen `STRATO` zu verifizieren
- spaeter `documents@frawo-tech.de`
  - dedizierter Dokumenteneingang fuer Paperless

## Outbound Standard

- `Nextcloud` -> `noreply@frawo-tech.de`
- `Paperless` -> `noreply@frawo-tech.de`
- `Odoo` -> `noreply@frawo-tech.de`
- `AzuraCast` -> `noreply@frawo-tech.de`

Technisch:

- Versand per `SMTP Submission` ueber `STRATO`
- kein eigener Mailserver auf dem Homeserver

## Inbound Standard

### Normale Kommunikation

- normale Mails bleiben in `STRATO`
- Zugriff per Webmail oder spaeter per Mailclient

### Dokumente Fuer Paperless

- Dokumente gehen an `documents@frawo-tech.de`
- `Paperless` holt diese Mailbox per `IMAP` ab
- Anhaenge werden importiert
- Regeln in `Paperless` setzen:
  - Dokumenttyp
  - Korrespondent
  - Tags
  - Besitzer `wolf` oder `franz`

### Dateien Fuer Nextcloud

- `Nextcloud` ist Dateiablage, nicht Mailserver
- persoenliche oder gemeinsame Dateien liegen in Nextcloud-Ordnern
- spaeter koennen Anhaenge aus dem Mailkontext in Nextcloud abgelegt oder gespiegelt werden

## Zielordner

- Nextcloud:
  - `Paperless/Eingang`
  - `Paperless/Archiv`
  - persoenliche Arbeitsordner fuer `wolf`
  - persoenliche Arbeitsordner fuer `franz`
- Paperless:
  - Dokumentenarchiv
  - Regeln und Tags

## Nicht Tun

- keine globale Weiterleitung aller STRATO-Mails auf den Server
- `info@frawo-tech.de` nicht als persoenlichen Admin-Login verwenden
- keinen eigenen Mailserver fuer diese Phase bauen

## Reihenfolge

1. Alias-/Postfachmodell in `STRATO` verifizieren und bereinigen
2. `noreply@frawo-tech.de` als SMTP-Absender in den Apps setzen
3. spaeter `documents@frawo-tech.de` anlegen
4. `Paperless` per `IMAP` an die Dokumenten-Mailbox binden
5. Nextcloud-Ablagepfade und eventuelle Spiegelung danach finalisieren

## Definition Of Done

- alle produktiven Apps senden ueber `STRATO SMTP`
- normale Kommunikation liegt in den persoenlichen oder allgemeinen STRATO-Mailboxen
- Dokumente an `documents@frawo-tech.de` landen automatisch in `Paperless`
- Nextcloud bleibt die zentrale Dateiablage fuer Arbeits- und Archivordner

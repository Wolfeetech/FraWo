# STRATO Mail Client Setup

## Status

Dieses Dokument ist jetzt ein Uebergangs- und Referenzdokument.

Der kanonische Client- und SMTP-Standard liegt jetzt in:

- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATOR_TODO_QUEUE.md`

Stand: `2026-03-27`

## Weiterhin Gueltig

- Login immer mit dem echten Postfach, nicht mit Aliasen
- technischer Basis-Login fuer den Owner-Pfad ist `webmaster@frawo-tech.de`
- `franz@frawo-tech.de` ist ein eigenes echtes Postfach
- `franz@frawo-tech.de` wurde am `2026-03-27` erfolgreich per `IMAP` und `SMTP AUTH` verifiziert
- bevorzugter Clientpfad:
  - `imap.strato.de:993` mit `SSL/TLS`
  - `smtp.strato.de:587` mit `STARTTLS`
  - `465` mit `SSL/TLS` nur als Fallback fuer problematische Clients

## Nicht Mehr Hier Pflegen

- keine zweite manuelle Setup-Anleitung neben dem Mail-Kanon
- keine offenen Providerentscheidungen
- keine Passwort- oder Aliaslogik ausserhalb von `OPERATIONS/MAIL_OPERATIONS.md`

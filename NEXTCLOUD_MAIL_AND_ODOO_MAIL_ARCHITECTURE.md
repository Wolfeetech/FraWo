# Nextcloud Mail And Odoo Mail Architecture

## Status

Dieses Dokument bleibt als Architekturkontext bestehen.

Der kanonische Betriebs- und Rolloutpfad liegt jetzt in:

- `OPERATIONS/MAIL_OPERATIONS.md`

Stand: `2026-03-26`

## Kurzentscheidung

- `Outlook` war nur der pragmatische Testpfad fuer das `STRATO`-Postfach.
- Produktiv soll Mail nicht ueber Outlook zentriert werden.
- Produktiv soll Mail auch **nicht** ueber einen eigenen Homeserver-Mailserver laufen.
- Der saubere Zielpfad ist:
  - `STRATO` als Mail-Provider
  - `Nextcloud Mail` als zentrale Web-Oberflaeche fuer Benutzer
  - native Mailclients auf Endgeraeten bei Bedarf
  - `Odoo` nur fuer geschaeftsprozessbezogene Mail-Aliasse und Threading
  - `Paperless` fuer Dokumente per dedizierter `IMAP`-Mailbox

## Zielbild

### Personenmail

- `webmaster@...` bleibt technisches Basis-Postfach
- `wolf@frawo-tech.de` ist Alias und sichtbare Arbeitsidentitaet fuer Wolf
- `franz@frawo-tech.de` ist eigenes echtes Postfach

### Funktionsmail

- `info@frawo-tech.de`
  - Kontakt und allgemeiner Eingang
- `noreply@frawo-tech.de`
  - Systemmails
- technischer Zielpfad fuer `info` und `noreply` ist noch gegen `STRATO` zu verifizieren
- spaeter `documents@frawo-tech.de`
  - dedizierter Dokumenteneingang fuer `Paperless`

## Nextcloud

`Nextcloud Mail` ist der richtige zentrale Benutzerzugang, wenn ihr Mail in eure eigene Oberflaeche integrieren wollt.

Einsatz:

- `STRATO IMAP` fuer Eingang
- `STRATO SMTP` fuer Versand
- Benutzer sehen Mail in Nextcloud statt in einem separaten Webmail

Nicht Ziel:

- Nextcloud wird **nicht** selbst zum Mailserver

## Odoo

`Odoo` ist **nicht** euer primaerer persoenlicher Mailclient.

Richtiger Einsatz:

- gemeinsame Funktionspostfaecher
- App-/Prozess-Aliasse
- E-Mail-Threading fuer CRM, Verkauf, Helpdesk, Vorgaenge

Nicht Ziel:

- persoenliche Mailbox fuer Wolf oder Franz
- Ersatz fuer einen normalen Mailclient

## Paperless

`Paperless` soll Mails nicht allgemein verwalten.

Richtiger Einsatz:

- spaeter dedizierte Mailbox `documents@frawo-tech.de`
- Abruf per `IMAP`
- Anhaenge und Dokumente automatisch importieren

## Reihenfolge

1. Alias-/Postfachmodell in `STRATO` stabilisieren
2. Mail-Zugaenge in `Vaultwarden` sichtbar validieren
3. `Nextcloud Mail` als zentrale Mail-Oberflaeche planen und aktivieren
4. `noreply@frawo-tech.de` als SMTP-Absender in Apps setzen
5. spaeter `documents@frawo-tech.de` fuer `Paperless`
6. `Odoo` nur fuer Alias-/Workflow-Mails nutzen

## Warum Outlook Nicht Das Ziel Ist

- `Outlook` war nur ein Testwerkzeug fuer das echte Postfach
- damit prueft man `IMAP`/`SMTP`
- es ist nicht die geplante zentrale FRAWO-Mailoberflaeche

## Warum Kein Eigener Mailserver Jetzt

- das aktuelle Ziel ist stabiler interner Betrieb, nicht MTA-Betrieb
- `STRATO` loest Provider-, Zustell- und Reputationsthemen bereits
- der naechste echte Schritt ist App-SMTP und Benutzeroberflaeche, nicht eigener MX-Betrieb

## Quellen

- Nextcloud Mail Admin Manual:
  - `https://docs.nextcloud.com/server/stable/admin_manual/groupware/mail.html`
- Odoo Incoming Mail:
  - `https://www.odoo.com/documentation/17.0/applications/general/email_communication/email_servers_inbound.html`
- Odoo Alias Overview:
  - `https://www.odoo.com/knowledge/article/762`
- Odoo Outgoing Mail:
  - `https://www.odoo.com/knowledge/article/758`

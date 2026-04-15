# Mail System Rollout

## Status

Dieses Dokument bleibt als strategische Kontextdatei bestehen.

Der kanonische Operatorpfad liegt jetzt in:

- `OPERATIONS/MAIL_OPERATIONS.md`

## Ziel

Das produktive Alias-/Postfachmodell fuer `FRAWO` wird jetzt bei `STRATO` verifiziert und bereinigt. Google Workspace bleibt eine spaetere Option, nicht Teil des ersten Releases.

## Zielidentitaeten

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`
- `info@frawo-tech.de`
- `noreply@frawo-tech.de`
- spaeter fuer Dokumente: `documents@frawo-tech.de`
- spaeter optional: `frontend@frawo-tech.de`
- spaeter optional: `admin@frawo-tech.de` als Alias auf Wolf

## Betriebsregeln

- persoenliche Admin-Logins nur ueber `wolf@frawo-tech.de` oder spaeter `franz@frawo-tech.de`
- `info@frawo-tech.de` ist Kontakt- und Inbound-Postfach, kein Admin-Login
- `noreply@frawo-tech.de` ist der Standard-Absender fuer Systemmails
- `documents@frawo-tech.de` ist spaeter die dedizierte Eingangsadresse fuer Paperless
- `frontend@frawo-tech.de` wird nicht vor dem stabilen Surface-/Kiosk-Rollout benoetigt

## Aktueller Uebergangsstand

- `wolf@frawo-tech.de` ist aktuell sichtbarer Alias auf das technische Basis-Postfach `webmaster@...`
- `franz@frawo-tech.de` hat bereits ein eigenes echtes Postfach
- der technische Stand von `info@frawo-tech.de` ist noch gegen das `STRATO`-Paket zu verifizieren
- der technische Stand von `noreply@frawo-tech.de` ist noch gegen das `STRATO`-Paket zu verifizieren

## STRATO Runbook

1. Domain `frawo-tech.de` im STRATO-Panel verifizieren.
2. Alias-/Postfachmodell fuer `wolf`, `franz`, `info` und `noreply` pruefen und bereinigen.
3. Zugangsdaten sofort in Vaultwarden unter `FraWo / Mail & Domains` speichern.
4. SPF-, DKIM- und DMARC-Eintraege fuer `frawo-tech.de` dokumentieren.
5. Testversand und Testempfang ueber die echten Loginpfade und Rollenbeziehungen pruefen.

## Wichtige Einschraenkung

- Wenn die Adressen in einem `STRATO Domain-Paket` liegen, ist `STRATO Webmail` laut STRATO nicht der richtige Testpfad.
- Dann erfolgt der Test ueber einen externen Mailclient mit:
  - `IMAP`: `imap.strato.de`
  - `SMTP`: `smtp.strato.de`
- Logins immer mit dem echten Postfach, nicht mit Alias-Adressen.

## SMTP Zielbild pro App

| App | Absender | Zweck | Status |
| --- | --- | --- | --- |
| Nextcloud | `noreply@frawo-tech.de` | Freigaben, Hinweise, Passwortflows | pending |
| Paperless | `noreply@frawo-tech.de` | Benachrichtigungen/Workflows | pending |
| Odoo | `noreply@frawo-tech.de` | Transaktions- und Systemmail | pending |
| AzuraCast | `noreply@frawo-tech.de` | System- und Admin-Hinweise | pending |
| Website / Kontakt | `info@frawo-tech.de` | Inbound / Kontaktformular | pending |
| Paperless Inbound | `documents@frawo-tech.de` | Dokumente und Anhaenge per IMAP importieren | later |

## Tests

- Login in alle realen STRATO-Postfaecher moeglich
- Alias- und Rollenbeziehungen fuer `wolf`, `info` und `noreply` sind nachvollziehbar dokumentiert
- Versand zu externer Adresse erfolgreich
- Antwortempfang erfolgreich
- SPF passt
- DKIM signiert
- DMARC Policy dokumentiert

## Empfohlene Rollout-Reihenfolge

1. `wolf@frawo-tech.de` als Alias-/Loginpfad ueber `webmaster@...` pruefen
2. `franz@frawo-tech.de` als eigenes echtes Postfach pruefen
3. `info@frawo-tech.de` und `noreply@frawo-tech.de` technisch im `STRATO`-Paket verifizieren
4. alle Mail-Zugaenge in `Vaultwarden / Mail & Domains` ablegen
5. `noreply@frawo-tech.de` als SMTP-Absender fuer Apps vorbereiten
6. App-SMTP in dieser Reihenfolge aktivieren:
   - `Nextcloud`
   - `Paperless`
   - `Odoo`
   - `AzuraCast`
7. danach `Nextcloud Mail` fuer Wolf und Franz als zentrale Oberflaeche vorbereiten
8. spaeter `documents@frawo-tech.de` fuer `Paperless IMAP` einfuehren

## App-SMTP Minimalziel

- `Nextcloud` kann Benachrichtigungen und Passwortflows sauber senden
- `Paperless` kann Benachrichtigungen sauber senden
- `Odoo` kann System- und Prozessmails sauber senden
- `AzuraCast` kann System- und Admin-Hinweise sauber senden

## Noch Nicht Teil Dieses Blocks

- kein eigener Homeserver-Mailserver
- kein kompletter Groupware-/Chat-Stack
- keine globale Mailweiterleitung aller Rollenpostfaecher auf den Server

## Hinweise

- Google Workspace ist aktuell nicht der Default.
- Ein spaeterer Wechsel ist moeglich, aber erst nach stabilem Website- und Mail-Betrieb sinnvoll.
- Ein eigener Mailserver auf dem Homeserver ist in dieser Phase bewusst **nicht** Teil des Betriebsstandards.

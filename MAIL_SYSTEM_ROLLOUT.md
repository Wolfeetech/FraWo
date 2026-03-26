# Mail System Rollout

## Ziel

Die ersten produktiven FRAWO-Mailboxen werden jetzt bei `STRATO` angelegt. Google Workspace bleibt eine spaetere Option, nicht Teil des ersten Releases.

## Ziel-Mailboxen

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

- `wolf@frawo-tech.de` ist aktuell als Alias auf `wolf@yourparty.tech` nutzbar
- `info@frawo-tech.de` ist aktuell als Alias auf `wolf@yourparty.tech` nutzbar
- `noreply@frawo-tech.de` ist aktuell als Alias auf `wolf@yourparty.tech` nutzbar
- `franz@frawo-tech.de` ist noch offen, weil dafuer ein eigenes Postfach benoetigt wird

## STRATO Runbook

1. Domain `frawo-tech.de` im STRATO-Panel verifizieren.
2. Die vier Ziel-Postfaecher anlegen.
3. Zugangsdaten sofort in Bitwarden speichern.
4. SPF-, DKIM- und DMARC-Eintraege fuer `frawo-tech.de` dokumentieren.
5. Testversand und Testempfang mit externem Ziel pruefen.

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

- Login in alle STRATO-Postfaecher moeglich
- Versand zu externer Adresse erfolgreich
- Antwortempfang erfolgreich
- SPF passt
- DKIM signiert
- DMARC Policy dokumentiert

## Hinweise

- Google Workspace ist aktuell nicht der Default.
- Ein spaeterer Wechsel ist moeglich, aber erst nach stabilem Website- und Mail-Betrieb sinnvoll.

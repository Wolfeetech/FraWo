# Mail System Rollout

## Ziel

Die ersten produktiven FRAWO-Mailboxen werden jetzt bei `STRATO` angelegt. Google Workspace bleibt eine spaetere Option, nicht Teil des ersten Releases.

## Ziel-Mailboxen

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`
- `info@frawo-tech.de`
- `noreply@frawo-tech.de`
- spaeter optional: `frontend@frawo-tech.de`
- spaeter optional: `admin@frawo-tech.de` als Alias auf Wolf

## Betriebsregeln

- persoenliche Admin-Logins nur ueber `wolf@frawo-tech.de` oder spaeter `franz@frawo-tech.de`
- `info@frawo-tech.de` ist Kontakt- und Inbound-Postfach, kein Admin-Login
- `noreply@frawo-tech.de` ist der Standard-Absender fuer Systemmails
- `frontend@frawo-tech.de` wird nicht vor dem stabilen Surface-/Kiosk-Rollout benoetigt

## STRATO Runbook

1. Domain `frawo-tech.de` im STRATO-Panel verifizieren.
2. Die vier Ziel-Postfaecher anlegen.
3. Zugangsdaten sofort in Bitwarden speichern.
4. SPF-, DKIM- und DMARC-Eintraege fuer `frawo-tech.de` dokumentieren.
5. Testversand und Testempfang mit externem Ziel pruefen.

## SMTP Zielbild pro App

| App | Absender | Zweck | Status |
| --- | --- | --- | --- |
| Nextcloud | `noreply@frawo-tech.de` | Freigaben, Hinweise, Passwortflows | pending |
| Paperless | `noreply@frawo-tech.de` | Benachrichtigungen/Workflows | pending |
| Odoo | `noreply@frawo-tech.de` | Transaktions- und Systemmail | pending |
| AzuraCast | `noreply@frawo-tech.de` | System- und Admin-Hinweise | pending |
| Website / Kontakt | `info@frawo-tech.de` | Inbound / Kontaktformular | pending |

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

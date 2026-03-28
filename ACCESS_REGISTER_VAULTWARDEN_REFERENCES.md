# Vaultwarden Reference Register

Stand: `2026-03-26`

Diese Datei ist der passwortfreie Referenzauszug nach dem Vaultwarden-Import.
Sie ersetzt keine Vaultwarden-Eintraege und ist nur fuer Betrieb, Audit und Markdown-Bereinigung gedacht.

## Quelle

- historisch generiert aus dem inzwischen extern archivierten `ACCESS_REGISTER.md`
- Organisation: `FraWo`
- importierbare Eintraege: `17`
- zusammengefuehrte Duplikate: `1`

## Collection Summary

- `Business Apps`: `10`
- `Core Infra`: `2`
- `Media`: `5`

## Site Summary

- `Anker`: `17`
- `Villa`: `1`

## Business Apps

| Vault Item | Benutzer | URL | Standort | Vaultwarden-Referenz | Herkunft |
| --- | --- | --- | --- | --- | --- |
| `Nextcloud - franz` | `franz` | `http://cloud.hs27.internal` | `Anker` | `FraWo / Business Apps / Nextcloud - franz` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live per OCS verifiziert. |
| `Nextcloud - frontend` | `frontend` | `http://cloud.hs27.internal` | `Anker` | `FraWo / Business Apps / Nextcloud - frontend` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live per OCS verifiziert. |
| `Nextcloud - wolf` | `wolf` | `http://cloud.hs27.internal` | `Anker` | `FraWo / Business Apps / Nextcloud - wolf` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live per OCS verifiziert. |
| `Nextcloud Admin` | `frawoadmin` | `http://cloud.hs27.internal` | `Anker` | `FraWo / Business Apps / Nextcloud Admin` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: bestehender Arbeitsstand. |
| `Odoo - franz@frawo-tech.de` | `franz@frawo-tech.de` | `http://odoo.hs27.internal/web/login` | `Anker` | `FraWo / Business Apps / Odoo - franz@frawo-tech.de` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live verifiziert. |
| `Odoo Admin` | `wolf@frawo-tech.de` | `http://odoo.hs27.internal/web/login` | `Anker` | `FraWo / Business Apps / Odoo Admin` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: live per XML-RPC verifiziert. Also listed as: Odoo. |
| `Paperless - franz` | `franz` | `http://paperless.hs27.internal/accounts/login/` | `Anker` | `FraWo / Business Apps / Paperless - franz` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: im Django-Stack gesetzt und geprueft. |
| `Paperless - frontend` | `frontend` | `http://paperless.hs27.internal/accounts/login/` | `Anker` | `FraWo / Business Apps / Paperless - frontend` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: im Django-Stack gesetzt und geprueft. |
| `Paperless - wolf` | `wolf` | `http://paperless.hs27.internal/accounts/login/` | `Anker` | `FraWo / Business Apps / Paperless - wolf` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: im Django-Stack gesetzt und geprueft. |
| `Paperless Admin` | `frawoadmin` | `http://paperless.hs27.internal/accounts/login/` | `Anker` | `FraWo / Business Apps / Paperless Admin` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: bestehender Arbeitsstand. |

## Core Infra

| Vault Item | Benutzer | URL | Standort | Vaultwarden-Referenz | Herkunft |
| --- | --- | --- | --- | --- | --- |
| `AdGuard Admin` | `admin` | `http://127.0.0.1:3000` | `Anker` | `FraWo / Core Infra / AdGuard Admin` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: live verifiziert. |
| `Home Assistant - wolf` | `wolf` | `http://ha.hs27.internal` | `Anker` | `FraWo / Core Infra / Home Assistant - wolf` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: bestehender Arbeitsstand. |

## Media

| Vault Item | Benutzer | URL | Standort | Vaultwarden-Referenz | Herkunft |
| --- | --- | --- | --- | --- | --- |
| `AzuraCast Admin` | `wolf@frawo-tech.de` | `http://radio.hs27.internal/login` | `Anker, Villa` | `FraWo / Media / AzuraCast Admin` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: live verifiziert. |
| `Jellyfin - Franz` | `Franz` | `http://media.hs27.internal` | `Anker` | `FraWo / Media / Jellyfin - Franz` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live verifiziert. |
| `Jellyfin - TV Wohnzimmer` | `TV Wohnzimmer` | `http://media.hs27.internal` | `Anker` | `FraWo / Media / Jellyfin - TV Wohnzimmer` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live verifiziert. |
| `Jellyfin - Wolf` | `Wolf` | `http://media.hs27.internal` | `Anker` | `FraWo / Media / Jellyfin - Wolf` | Imported from ACCESS_REGISTER.md (Named user logins). Original status: live verifiziert. |
| `Jellyfin Admin` | `root` | `http://media.hs27.internal` | `Anker` | `FraWo / Media / Jellyfin Admin` | Imported from ACCESS_REGISTER.md (Admin and bootstrap logins). Original status: live verifiziert. |

## Betriebsregel

- Klartext-Passwoerter gehoeren nach erfolgreicher Vaultwarden-Verifikation nicht mehr in Arbeitsdateien.
- Diese Referenzdatei darf bleiben, solange sie keine Passwoerter enthaelt und bei Aenderungen neu generiert wird.

# Access Register

## Zweck

Diese Datei ist die zentrale Uebersicht fuer:

- aktuelle interne Service-URLs
- aktuelles Login-Bild im Ist-Zustand
- Zielbild fuer `wolf`, `franz`, `frontend` und Rollenpostfaecher
- Release-Gate vor der Oeffnung ueber die neue Strato-Domain

Wichtig:

- Diese Datei ist die Arbeitsuebersicht, nicht der Ersatz fuer den Passwortmanager.
- Es gibt aktuell noch keinen produktiven Passwortmanager im Projekt; das Zielsystem ist jetzt `Bitwarden Cloud`.
- Finale Passwoerter werden erst dann als produktiv betrachtet, wenn alle betroffenen Services stabil sind und die Eintraege in Bitwarden liegen.
- Die neue Domain wird erst freigegeben, wenn die internen Dienste stabil sind, die Benutzer sauber umgestellt wurden und Secrets nicht mehr dauerhaft in Markdown-Dateien liegen.

## Aktueller interner Zugang

| Service | Interne URL | Status | Aktueller Login-Stand |
| --- | --- | --- | --- |
| Portal | `http://portal.hs27.internal` | live | kein Login |
| Nextcloud | `http://cloud.hs27.internal` | live | `frawoadmin` plus `wolf`, `franz`, `frontend` vorhanden |
| Paperless | `http://paperless.hs27.internal/accounts/login/` | live | `frawoadmin` plus `wolf`, `franz`, `frontend` vorhanden |
| Odoo | `http://odoo.hs27.internal/web/login` | live | `wolf@frawo-tech.de` und `franz@frawo-tech.de` vorhanden |
| Home Assistant | `http://ha.hs27.internal` | live | aktueller Haupt-Account aktiv |
| Jellyfin | `http://media.hs27.internal` | live | technischer Admin fix, Personenprofile vorhanden |
| AzuraCast | `http://radio.hs27.internal/login` | live | persoenlicher Admin `wolf@frawo-tech.de` aktiv |
| AdGuard | `127.0.0.1:3000` auf `CT100 toolbox` | live | lokaler Admin fix |

## Aktuelle Admin- und Bootstrap-Logins

Diese Werte sind der aktuelle technische Betriebsstand fuer den internen Zugriff. Sie bleiben relevant, bis alle Finalwerte in Bitwarden liegen und die temporaeren Bootstrap-Zugaenge abgeloest sind.

| Service | URL | Benutzer | Passwort | Stand |
| --- | --- | --- | --- | --- |
| Nextcloud Admin | `http://cloud.hs27.internal` | `frawoadmin` | `NC-Frawo-2026!` | bestehender Arbeitsstand |
| Paperless Admin | `http://paperless.hs27.internal/accounts/login/` | `frawoadmin` | `PL-Frawo-2026!` | bestehender Arbeitsstand |
| Odoo Admin | `http://odoo.hs27.internal/web/login` | `wolf@frawo-tech.de` | `OD-Wolf-2026!` | live per XML-RPC verifiziert |
| Home Assistant | `http://ha.hs27.internal` | `wolf` | `HA-Wolf-2026!` | bestehender Arbeitsstand |
| Jellyfin Admin | `http://media.hs27.internal` | `root` | `JF-Frawo-2026!` | live verifiziert |
| AzuraCast Admin | `http://radio.hs27.internal/login` | `wolf@frawo-tech.de` | `AZ-Wolf-2026!` | live verifiziert |
| AdGuard Admin | `127.0.0.1:3000` auf `CT100 toolbox` | `admin` | `AG-Admin-2026!` | live verifiziert |

## Personenbasierte Konten live

| Service | URL | Benutzer | Passwort | Stand |
| --- | --- | --- | --- | --- |
| Nextcloud | `http://cloud.hs27.internal` | `wolf` | `NC-Wolf-2026!` | live per OCS verifiziert |
| Nextcloud | `http://cloud.hs27.internal` | `franz` | `NC-Franz-2026!` | live per OCS verifiziert |
| Nextcloud | `http://cloud.hs27.internal` | `frontend` | `NC-Frontend-2026!` | live per OCS verifiziert |
| Paperless | `http://paperless.hs27.internal/accounts/login/` | `wolf` | `PL-Wolf-2026!` | im Django-Stack gesetzt und geprueft |
| Paperless | `http://paperless.hs27.internal/accounts/login/` | `franz` | `PL-Franz-2026!` | im Django-Stack gesetzt und geprueft |
| Paperless | `http://paperless.hs27.internal/accounts/login/` | `frontend` | `PL-Frontend-2026!` | im Django-Stack gesetzt und geprueft |
| Odoo | `http://odoo.hs27.internal/web/login` | `wolf@frawo-tech.de` | `OD-Wolf-2026!` | live verifiziert |
| Odoo | `http://odoo.hs27.internal/web/login` | `franz@frawo-tech.de` | `OD-Franz-2026!` | live verifiziert |
| Jellyfin | `http://media.hs27.internal` | `Wolf` | `JF-Wolf-2026!` | live verifiziert |
| Jellyfin | `http://media.hs27.internal` | `Franz` | `JF-Franz-2026!` | live verifiziert |
| Jellyfin | `http://media.hs27.internal` | `TV Wohnzimmer` | `JF-TV-2026!` | live verifiziert |

## Aktueller Betriebsstandard

### Bereits stabil

- `Nextcloud`
- `Paperless`
- `Odoo`
- `Home Assistant`
- `Jellyfin` als Dienst
- `AzuraCast` als Dienst mit Station `frawo-funk`
- personenbasierte Konten fuer `wolf` und `franz` in `Nextcloud`, `Paperless` und `Odoo`
- Shared-/Kiosk-Konto `frontend` in `Nextcloud` und `Paperless`
- `Jellyfin`-Profile `Wolf`, `Franz` und `TV Wohnzimmer`

### Noch nicht final

- finale Ablage aller aktuellen Passwoerter in `Bitwarden Cloud`
- Rueckbau dieser Datei von Klartext-Passwoertern auf Eintragsreferenzen
- optionale PIN-Konfiguration in `Jellyfin`
- reale STRATO-Mailboxen fuer `wolf`, `franz`, `info`, `noreply`

## Bitwarden Zielbild

Die produktive Secret-Ablage wird in `Bitwarden Cloud` organisiert:

- `Core Infra`
- `Business Apps`
- `Media`
- `Mail & Domains`
- `Devices`
- `Stockenweiler`

Erst wenn die Eintraege dort liegen, darf diese Datei auf Referenzen statt Klartext zurueckgebaut werden.

## Zielbild Identitaeten

### Personenkonten

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`

### Rollenpostfaecher

- `frontend@frawo-tech.de`
- `info@frawo-tech.de`
- optional spaeter: `noreply@frawo-tech.de`

## Freigabe-Regel fuer die neue Strato-Domain

Die neue Domain bleibt intern vorbereitet und wird erst released, wenn alle Punkte gruen sind:

1. interne Dienste stabil ueber `hs27.internal`
2. `local-lvm` wieder mit ausreichender Reserve
3. finale Benutzer fuer `wolf`, `franz`, `frontend` angelegt
4. finale Passwoerter in `Bitwarden Cloud` abgelegt
5. Jellyfin-, AzuraCast- und AdGuard-Logins finalisiert
6. DNS-, TLS-, Reverse-Proxy- und Rollback-Pfad sauber dokumentiert

## Naechste direkte Aufgaben

1. Alle neuen Werte in `Bitwarden Cloud` uebernehmen.
2. STRATO-Mailboxen fuer `wolf`, `franz`, `info` und `noreply` anlegen.
3. Optional in `Jellyfin` PINs fuer `Wolf` und `Franz` setzen.
4. `frontend@frawo-tech.de` erst dann extern releasen, wenn Surface und Kioskpfad wieder stabil sind.
5. Danach die Domain-/TLS-Freigabe erst nach Secret- und Stabilitaetscheck ziehen.

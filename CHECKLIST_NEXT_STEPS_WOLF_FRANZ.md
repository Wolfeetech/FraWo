# Checkliste Naechste Schritte Fuer Wolf Und Franz

Stand: `2026-03-26`

Diese Liste ist zum direkten Abarbeiten gedacht.

## Aktueller Blocker

- [x] Vaultwarden ist technisch erreichbar:
  - `http://192.168.2.26:8080`
- [x] Aktuell ist die produktive Nutzung ueber Browser und Passwortmanager-Clients blockiert, weil noch kein `HTTPS` davor liegt
- [ ] Deshalb gilt ab jetzt:
  - zuerst internen `HTTPS`-Pfad fuer Vaultwarden bauen
  - dann `wolf@frawo-tech.de` als ersten produktiven Benutzer anlegen
  - dabei das Master-Passwort nur manuell setzen
  - sofort den Offline-Recovery-Zettel und die zweite Offline-Kopie anlegen
  - erst danach die produktiven Eintraege sauber nach Vaultwarden uebernehmen

## 0. Henne-Ei-Problem sauber loesen

- [ ] Zuerst `VAULTWARDEN_INTERNAL_HTTPS_ROLLOUT.md` abarbeiten
- [ ] Sobald Vaultwarden per `HTTPS` bereitsteht:
  - `wolf@frawo-tech.de` als ersten produktiven Benutzer anlegen
  - Master-Passwort nur manuell setzen
  - Offline-Recovery-Zettel ausfuellen
  - zweite getrennte Offline-Kopie anlegen
- [ ] Danach zuerst `STRATO`- und Core-Infra-Zugaenge in Vaultwarden eintragen
- [ ] Danach App-Zugaenge aus `ACCESS_REGISTER.md` nachziehen

Entscheidung:

- Vaultwarden-`HTTPS` ist die unmittelbare Vorbedingung
- `wolf@frawo-tech.de` ist der erste produktive Vaultwarden-Benutzer
- `franz@frawo-tech.de` folgt erst nach stabilem Erstaufbau
- danach werden die produktiven Identitaeten sauber eingezogen

## 1. Vaultwarden jetzt fertig machen

- [ ] Vaultwarden nicht weiter produktiv benutzen, bis `HTTPS` davor liegt
- [ ] Danach wieder aufnehmen:
  - `https://vault.hs27.internal` oeffnen
  - `wolf@frawo-tech.de` als ersten produktiven Benutzer anlegen
  - eigenes Master-Passwort selbst setzen
  - Recovery-Zettel ausfuellen
  - zweite getrennte Offline-Kopie anlegen
  - Login ueber `HTTPS` pruefen
  - erste Sammlungen anlegen:
    - `Core Infra`
    - `Business Apps`
    - `Media`
    - `Mail & Domains`
    - `Devices`
    - `Stockenweiler`

Wichtig:

- Das Master-Passwort wird **nicht** in Markdown dokumentiert.
- Das Master-Passwort gehoert nur:
  - in deinen Kopf
  - auf den Offline-Recovery-Zettel
  - auf eine zweite getrennte Offline-Kopie

Nur lokal vorhandene Bootstrap-Dateien:

- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_admin_token.txt`
- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_ct120_root_password.txt`

## 2. Erst jetzt STRATO fertig machen

- [ ] `STRATO_MAIL_ACCOUNT_ROLLOUT_CHECKLIST.md` vollstaendig abarbeiten
- [x] Diese Alias-/Mailbox-Basis steht jetzt:
  - `wolf@frawo-tech.de` -> Alias auf `wolf@yourparty.tech`
  - `info@frawo-tech.de` -> Alias auf `wolf@yourparty.tech`
  - `noreply@frawo-tech.de` -> Alias auf `wolf@yourparty.tech`
- [ ] Offener Mail-Block:
  - `franz@frawo-tech.de` braucht ein eigenes echtes Postfach
- [ ] Alle neuen Mail-Passwoerter voruebergehend offline sichern
- [ ] Mindestens `wolf@frawo-tech.de` und `franz@frawo-tech.de` in `STRATO Webmail` testen

## 3. Diese produktiven Logins nach Vaultwarden uebernehmen

Reihenfolge:

- [ ] zuerst `STRATO`- und Core-Infra-Zugaenge
- [ ] danach App-Zugaenge aus `ACCESS_REGISTER.md`
- [ ] erst danach Klartext in Arbeitsdateien reduzieren

### Core Apps

- [ ] Nextcloud Admin
  - URL: `http://cloud.hs27.internal`
  - Benutzer: `frawoadmin`
  - Passwort: `NC-Frawo-2026!`

- [ ] Paperless Admin
  - URL: `http://paperless.hs27.internal/accounts/login/`
  - Benutzer: `frawoadmin`
  - Passwort: `PL-Frawo-2026!`

- [ ] Odoo Admin
  - URL: `http://odoo.hs27.internal/web/login`
  - Benutzer: `wolf@frawo-tech.de`
  - Passwort: `OD-Wolf-2026!`

- [ ] Home Assistant
  - URL: `http://ha.hs27.internal`
  - Benutzer: `wolf`
  - Passwort: `HA-Wolf-2026!`

- [ ] Jellyfin Admin
  - URL: `http://media.hs27.internal`
  - Benutzer: `root`
  - Passwort: `JF-Frawo-2026!`

- [ ] AzuraCast Admin
  - URL: `http://radio.hs27.internal/login`
  - Benutzer: `wolf@frawo-tech.de`
  - Passwort: `AZ-Wolf-2026!`

- [ ] AdGuard Admin
  - URL: `127.0.0.1:3000`
  - Benutzer: `admin`
  - Passwort: `AG-Admin-2026!`

### Personenkonten Wolf

- [ ] Nextcloud Wolf
  - URL: `http://cloud.hs27.internal`
  - Benutzer: `wolf`
  - Passwort: `NC-Wolf-2026!`

- [ ] Paperless Wolf
  - URL: `http://paperless.hs27.internal/accounts/login/`
  - Benutzer: `wolf`
  - Passwort: `PL-Wolf-2026!`

- [ ] Odoo Wolf
  - URL: `http://odoo.hs27.internal/web/login`
  - Benutzer: `wolf@frawo-tech.de`
  - Passwort: `OD-Wolf-2026!`

- [ ] Jellyfin Wolf
  - URL: `http://media.hs27.internal`
  - Benutzer: `Wolf`
  - Passwort: `JF-Wolf-2026!`

### Personenkonten Franz

- [ ] Nextcloud Franz
  - URL: `http://cloud.hs27.internal`
  - Benutzer: `franz`
  - Passwort: `NC-Franz-2026!`

- [ ] Paperless Franz
  - URL: `http://paperless.hs27.internal/accounts/login/`
  - Benutzer: `franz`
  - Passwort: `PL-Franz-2026!`

- [ ] Odoo Franz
  - URL: `http://odoo.hs27.internal/web/login`
  - Benutzer: `franz@frawo-tech.de`
  - Passwort: `OD-Franz-2026!`

- [ ] Jellyfin Franz
  - URL: `http://media.hs27.internal`
  - Benutzer: `Franz`
  - Passwort: `JF-Franz-2026!`

### Shared / Geraete

- [ ] Nextcloud Frontend
  - URL: `http://cloud.hs27.internal`
  - Benutzer: `frontend`
  - Passwort: `NC-Frontend-2026!`

- [ ] Paperless Frontend
  - URL: `http://paperless.hs27.internal/accounts/login/`
  - Benutzer: `frontend`
  - Passwort: `PL-Frontend-2026!`

- [ ] Jellyfin TV Wohnzimmer
  - URL: `http://media.hs27.internal`
  - Benutzer: `TV Wohnzimmer`
  - Passwort: `JF-TV-2026!`

## 4. Interne Dienste kurz pruefen

- [ ] Portal: `http://portal.hs27.internal`
- [ ] Nextcloud: `http://cloud.hs27.internal`
- [ ] Paperless: `http://paperless.hs27.internal/accounts/login/`
- [ ] Odoo: `http://odoo.hs27.internal/web/login`
- [ ] Home Assistant: `http://ha.hs27.internal`
- [ ] Jellyfin: `http://media.hs27.internal`
- [ ] AzuraCast: `http://radio.hs27.internal/login`

Hinweis:

- Jellyfin-Login fuer `Wolf` ist serverseitig wieder gesund.
- Falls der Browser noch meckert:
  - Site-Daten fuer `media.hs27.internal` loeschen
  - oder direkt neu testen auf `http://192.168.2.20:8096/web/`

## 5. STRATO-Mail vorbereiten

- [ ] STRATO-Login bereithalten
- [ ] Diese Mailboxen anlegen:
  - `wolf@frawo-tech.de`
  - `franz@frawo-tech.de`
  - `info@frawo-tech.de`
  - `noreply@frawo-tech.de`
- [ ] Jede neue Mailbox sofort in Vaultwarden unter `Mail & Domains` eintragen
- [ ] Danach SMTP-Standardisierung vorbereiten

## 6. Nach den Mailboxen

- [ ] `franz@frawo-tech.de` als zweiten produktiven Vaultwarden-Benutzer anlegen
- [ ] Passwortfreien Referenzstand bauen:
  - `python scripts/build_vaultwarden_reference_register.py`
- [ ] `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` als Arbeitsreferenz pruefen
- [ ] Erst danach `ACCESS_REGISTER.md` schrittweise von Klartext auf Vaultwarden-Referenzen umbauen
- [ ] Lokale Klartext-CSV-Dateien nach sichtbarer Tresor-Verifikation loeschen
- [ ] Systemmail-Absender spaeter auf `noreply@frawo-tech.de` ziehen

## 7. Wenn etwas unklar ist

- Operator-Start: `OPS_HOME.md`
- Einstieg: `START_HERE_WOLF_FRANZ.md`
- Handout: `WOLF_FRANZ_HANDOUT.md`
- Zugangsregister: `ACCESS_REGISTER.md`
- Vaultwarden Start: `VAULTWARDEN_SELFHOST_START.md`
- Plattformstatus: `PLATFORM_STATUS.md`

# Wolf Und Franz Handout

## Status

Dieses Dokument ist jetzt ein Uebergangs- und Referenzdokument.

Der kanonische Benutzer- und Onboardingpfad liegt in:

- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`

## Einstieg

- Portal intern: `http://portal.hs27.internal`
- Vaultwarden: `https://vault.hs27.internal`
- Nextcloud: `http://cloud.hs27.internal`
- Paperless: `http://paperless.hs27.internal`
- Odoo: `http://odoo.hs27.internal/web/login`
- Home Assistant: `http://ha.hs27.internal`
- Jellyfin mit DNS: `http://media.hs27.internal`
- Jellyfin ohne DNS: `http://192.168.2.20:8096`
- Radio: `http://radio.hs27.internal`

## Logins

- produktiver Standard: `Vaultwarden / FraWo`
- Arbeitsreferenz ohne Passwoerter: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- im Workspace gilt nur noch `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`

## Aktuell Wirklich Live

- alle Kern-URLs antworten intern
- `Vaultwarden` ist intern ueber `HTTPS` erreichbar
- der Basisbestand an App-Logins wurde nach `Vaultwarden` importiert
- `Jellyfin` funktioniert auf dem TV wieder ueber die direkte LAN-Adresse
- der letzte TV-Test lief ueber `Wolf`, nicht ueber `TV Wohnzimmer`

## Wenn Etwas Kaputt Wirkt

1. `PLATFORM_STATUS.md`
2. `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
3. `OPERATOR_TODO_QUEUE.md`
4. `OPS_HOME.md`

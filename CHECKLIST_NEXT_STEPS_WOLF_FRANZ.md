# Checkliste Naechste Schritte Fuer Wolf Und Franz

## Status

Dieses Dokument ist jetzt ein Uebergangs- und Referenzdokument.

Der kanonische Benutzer- und Onboardingpfad liegt in:

- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`

Die manuelle Operator-Queue liegt in:

- `OPERATOR_TODO_QUEUE.md`

Stand: `2026-03-30`

## Zweck

Diese Datei ist nur noch die direkte Last-Mile-Checkliste fuer den aktuellen internen Benutzer-Deploy.

Keine Grundsatzentscheidungen hier pflegen. Detailregeln stehen im Wiki-Kanon.

## 1. FraWo Und Vaultwarden

- [x] `Franz` in die `FraWo`-Organisation einladen
- [x] Collections fuer `Franz` pruefen:
  - `Business Apps`
  - `Core Infra`
  - `Media`
  - `Mail & Domains`
- [x] In `Vaultwarden` diese Eintraege sichtbar pruefen:
  - `Nextcloud Admin`
  - `Paperless Admin`
  - `Odoo Admin`
  - `AdGuard Admin`
  - `AzuraCast Admin`
  - `Jellyfin - TV Wohnzimmer`
- [ ] `AdGuard Admin` auf die korrekte URI `http://127.0.0.1:3000` pruefen

## 2. Benutzerdurchlauf

### Wolf

- [x] Login in `Vaultwarden`
- [x] Root-Portal `portal.hs27.internal` sichtbar gegen den neuen MVP-Stand pruefen
- [x] Login in `Nextcloud`
- [x] Login in `Paperless`
- [x] Login in `Odoo`
- [x] Login in `Home Assistant`
- [ ] Login in `Jellyfin` -> noch nicht erfolgreich


### Franz

- [x] Zugriff auf `FraWo` erfolgreich
- [x] Login in `Nextcloud`
- [x] Login in `Paperless`
- [x] Login in `Odoo`
- [ ] Login in `Jellyfin`
- [x] Franz-Startseite `portal.hs27.internal/franz/` sichtbar gegen den neuen MVP-Stand pruefen
- [ ] Surface-Laptop-Shortcuts mit `bootstrap_franz_surface_shortcuts.ps1` ausrollen
- [ ] iPhone-Homescreen-Pfad `100.99.206.128:8447/franz/` pruefen

### Shared / Device

- [ ] `frontend` in `Nextcloud` pruefen
- [ ] `frontend` in `Paperless` pruefen
- [ ] `TV Wohnzimmer` in `Jellyfin` pruefen

## 3. Mail Und Identitaet

- [x] `wolf@frawo-tech.de` als Alias-/Loginpfad ueber `webmaster@...` pruefen
- [x] `franz@frawo-tech.de` als eigenes Postfach sichtbar pruefen
- [ ] `info@frawo-tech.de` technisch pruefen
- [ ] `noreply@frawo-tech.de` technisch pruefen
- [ ] Produktive Mail-Zugaenge in `Vaultwarden / FraWo / Mail & Domains` ablegen
- [ ] Versand und Empfang sichtbar testen

## 4. Abschluss Fuer Diesen Block

- [ ] `device_rollout_verified` sichtbar abschliessen
- [ ] Offline-Recovery-Zettel fuer `Vaultwarden` wirklich ausfuellen
- [ ] Zweite getrennte Offline-Kopie fuer das Master-Passwort anlegen
- [ ] `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` als neue Arbeitsreferenz bestaetigen
- [ ] `ACCESS_REGISTER.md` danach schrittweise auf reine Vaultwarden-Referenzen zurueckbauen
- [ ] `STRESS_TEST_READINESS.md` gegenlesen
- [ ] Erst danach den internen Stresstest als freigegeben markieren

## Wenn Etwas Unklar Ist

- `OPS_HOME.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATOR_TODO_QUEUE.md`
- `STRESS_TEST_READINESS.md`

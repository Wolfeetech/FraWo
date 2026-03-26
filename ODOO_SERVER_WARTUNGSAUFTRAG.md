# Odoo Wartungsauftrag Server

Stand: `2026-03-26`

## Titel

`Homeserver 2027` auf internen Stresstest-Stand bringen, Mail-/Secret-Basis abschliessen und Release-Vorbereitung absichern.

## Typ

- Wartungsauftrag
- intern
- kritisch

## Ziel

Die Plattform soll so weit stabilisiert und standardisiert werden, dass:

- interne Kernsysteme reproduzierbar laufen
- Mail- und Secret-Basis sauber stehen
- der nächste interne Stresstest gefahren werden kann
- der Release-Pfad zu `www.frawo-tech.de` vorbereitet ist

## Aktueller Live-Stand

- `CT 100 toolbox` aktiv
- `CT 110 storage-node` aktiv
- `CT 120 vaultwarden` aktiv
- `VM 200 nextcloud` aktiv
- `VM 210 haos` aktiv
- `VM 220 odoo` aktiv
- `VM 230 paperless` aktiv
- `VM 240 pbs` aktiv
- interne Domains unter `hs27.internal` aktiv
- SMB-Medienpfad ist kanonisch:
  - `\\192.168.2.30\Media\yourparty_Libary`

## Hauptprobleme

1. `Vaultwarden` ist technisch live, aber noch nicht produktiv nutzbar, weil interner `HTTPS`-Pfad noch nicht live ist.
2. `STRATO` erlaubt aktuell ohne Tarif-Erweiterung nur die bestehende 2-Postfach-Struktur.
3. `franz@frawo-tech.de` braucht ein eigenes echtes Postfach/Login.
4. Passwörter liegen noch teilweise in Markdown-Arbeitsdateien.
5. Mailfluss `STRATO -> Apps -> Paperless/Nextcloud` ist architektonisch definiert, aber noch nicht umgesetzt.

## Beschlossene Zwischenlösung Mail

- echtes technisches Postfach:
  - `webmaster@...`
- Aliasse darauf:
  - `wolf@frawo-tech.de`
  - `info@frawo-tech.de`
  - `noreply@frawo-tech.de`
- `franz@frawo-tech.de` soll als zweites echtes Postfach geführt werden

## Arbeitspakete

### Paket 1 - STRATO-Mailbasis sauberziehen

Ziel:
- `wolf`, `info`, `noreply` funktionieren
- `franz` als eigener Login wird vorbereitet oder umgesetzt

Checkliste:
- [x] `wolf@frawo-tech.de` als Alias angelegt
- [x] `info@frawo-tech.de` als Alias angelegt
- [x] `noreply@frawo-tech.de` als Alias angelegt
- [x] `webmaster` als technisches Basis-Postfach identifiziert
- [ ] `franz@frawo-tech.de` als echtes zweites Postfach anlegen
- [ ] Mail-Login für `webmaster` über IMAP/SMTP sauber testen
- [ ] Mail-Login für `franz@frawo-tech.de` sauber testen

### Paket 2 - Vaultwarden produktiv machen

Ziel:
- `Vaultwarden` unter `https://vault.hs27.internal` intern nutzbar machen

Checkliste:
- [x] `CT120` läuft
- [x] Repo für `vault.hs27.internal` vorbereitet
- [ ] Caddy/AdGuard auf `CT100` live anpassen
- [ ] `https://vault.hs27.internal` intern testen
- [ ] ersten produktiven Benutzer anlegen
- [ ] zentrale Sammlungen anlegen:
  - `Core Infra`
  - `Business Apps`
  - `Media`
  - `Mail & Domains`
  - `Devices`
  - `Stockenweiler`

### Paket 3 - Secrets aus Markdown rausziehen

Ziel:
- produktive Logins zentral in `Vaultwarden`

Checkliste:
- [ ] `STRATO Kunden-Login` eintragen
- [ ] `webmaster`/Mailzugänge eintragen
- [ ] Nextcloud-Logins eintragen
- [ ] Paperless-Logins eintragen
- [ ] Odoo-Logins eintragen
- [ ] HAOS-Login eintragen
- [ ] Jellyfin-Logins eintragen
- [ ] AzuraCast-Login eintragen
- [ ] AdGuard-Login eintragen
- [ ] `ACCESS_REGISTER.md` danach auf Referenzen zurückbauen

### Paket 4 - Mailarchitektur umsetzen

Ziel:
- Mail professionell an Apps und Dokumentenfluss anbinden

Checkliste:
- [ ] `noreply@frawo-tech.de` als Standard-Absender festziehen
- [ ] SMTP in `Nextcloud` konfigurieren
- [ ] SMTP in `Paperless` konfigurieren
- [ ] SMTP in `Odoo` konfigurieren
- [ ] SMTP in `AzuraCast` konfigurieren
- [ ] später `documents@frawo-tech.de` einrichten
- [ ] `Paperless` per `IMAP` an `documents@frawo-tech.de` anbinden
- [ ] Nextcloud-Ablagepfade danach final prüfen

### Paket 5 - Stresstest-Readiness

Ziel:
- interner Stresstest ohne grundlegende Betriebsrisiken

Checkliste:
- [ ] Core-UIs grün:
  - `portal.hs27.internal`
  - `cloud.hs27.internal`
  - `paperless.hs27.internal`
  - `odoo.hs27.internal`
  - `ha.hs27.internal`
  - `media.hs27.internal`
  - `radio.hs27.internal`
- [ ] `Vaultwarden` intern per HTTPS erreichbar
- [ ] Mailbasis steht
- [ ] `local` und `local-lvm` bleiben mit Reserve stabil
- [ ] keine offenen Storage-/Rootfs-Fehler aktiv
- [ ] interne Benutzerflüsse einmal durchgetestet

## Abnahmekriterien

- Wolf kann mit seiner produktiven Identität arbeiten
- Franz hat ein eigenes echtes Login auf `franz@frawo-tech.de`
- Secrets liegen in `Vaultwarden`
- Mail läuft sauber über `STRATO`
- `Paperless`- und `Nextcloud`-Mailpfad ist vorbereitet
- interner Stresstest ist freigegeben

## Blocker

- fehlender Live-Deploy-Zugriff auf `CT100 toolbox` für den `Vaultwarden HTTPS`-Rollout
- `STRATO`-Postfachgrenze ohne Tarif-Erweiterung

## Relevante Dateien

- `MASTERPLAN.md`
- `PLATFORM_STATUS.md`
- `ACCESS_REGISTER.md`
- `STRATO_MAIL_ACCOUNT_ROLLOUT_CHECKLIST.md`
- `STRATO_MAIL_CLIENT_SETUP.md`
- `VAULTWARDEN_INTERNAL_HTTPS_ROLLOUT.md`
- `MAIL_SYSTEM_ROLLOUT.md`
- `MAIL_TO_PAPERLESS_NEXTCLOUD_ARCHITECTURE.md`
- `NEXTCLOUD_MAIL_AND_ODOO_MAIL_ARCHITECTURE.md`
- `STRESS_TEST_READINESS.md`

## Kurztext Für Odoo Beschreibung

Interner Wartungsauftrag zur Stabilisierung des `Homeserver 2027` vor Stresstest und Release-Vorbereitung. Fokus: `STRATO`-Mailbasis sauberziehen, `Vaultwarden` intern per HTTPS produktiv machen, produktive Logins aus Markdown in den Passworttresor überführen, Mailfluss für `Nextcloud`/`Paperless`/`Odoo` standardisieren und die Plattform auf einen kontrollierten internen Stresstest vorbereiten.

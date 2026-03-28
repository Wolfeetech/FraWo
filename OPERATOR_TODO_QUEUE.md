# Operator Todo Queue

Stand: `2026-03-28`

## Zweck

Diese Datei ist nur die kurze manuelle Unblock-Queue.

Keine erledigten Historien und keine zweite Projektplanung mehr hier. Der Kanon liegt in `OPS_HOME.md` und `OPERATIONS/*.md`.

## Business-MVP Jetzt Offen

1. `Vaultwarden` sichtbar gegenpruefen:
   - `Franz` sieht seine Organisation und Kernlogins
   - `Nextcloud Admin`
   - `Paperless Admin`
   - `Odoo Admin`
2. Benutzer- und Geraeteabnahme fuer den MVP sichtbar abschliessen:
   - Wolf-Loginpfad
   - Franz-Loginpfad
   - Franz `Surface Laptop`
   - Franz `iPhone`
3. `STRATO` fuer den Arbeitskern finalisieren:
   - `franz@frawo-tech.de`
   - `webmaster@frawo-tech.de`
   - `noreply@frawo-tech.de`
   - sichtbarer Versand und Empfang
   - alle finalen Zugaenge in `Vaultwarden / FraWo / Mail & Domains`
4. App-SMTP fuer den MVP sichtbar fertigziehen:
   - `Nextcloud` Testmail
   - `Paperless` Testmail
   - `Odoo` Testmail

## Website-Release Parallel

1. Zielsystem fuer `www.frawo-tech.de` festziehen.
2. DNS-/Redirect-Modell fuer `frawo-tech.de` -> `www.frawo-tech.de` finalisieren.
3. TLS-Automation festziehen.
4. SPF, DKIM und DMARC dokumentieren und testen.
5. Rollback fuer DNS-/TLS-/Hostwechsel schriftlich fertigziehen.

## Vollzertifizierung Spaeter

1. `AzuraCast`-SMTP nach repariertem `raspberry_pi_radio`-SSH gruen ziehen.
2. Media-, Radio- und `TV Wohnzimmer`-Pfad wieder in die aktive Oberflaeche aufnehmen.
3. `surface-go-frontend` als Shared-Frontend sauber abnehmen.
4. `PBS` als spaeteren Zertifizierungsblock sauber wiederaufbauen:
   - kein Produktionssiegel vorher
   - kein destruktiver Schritt ohne saubere Freigabe

## Bereits Verifiziert

- `release-mvp-audit` ist technisch komplett gruen: `artifacts/release_mvp_audit/20260328_004657`.
- `release-mvp-gate` ist jetzt sauber getrennt und blockiert aktuell nur noch auf manueller Evidenz: `artifacts/release_mvp_gate/20260328_004741/release_mvp_gate.md`.
- `Vaultwarden` ist intern ueber `HTTPS` live.
- `Vaultwarden`-Invites sind per SMTP aktiviert.
- `Vaultwarden`-`ADMIN_TOKEN` ist live gehasht.
- `franz@frawo-tech.de` ist per `IMAP` und `SMTP AUTH` technisch verifiziert.
- die `Vaultwarden`-Einladungsmail an `franz@frawo-tech.de` ist erfolgreich angekommen.
- `Franz` hat die `FraWo`-Einladung angenommen.
- der Franz-Pfad ist auf portal-first und shortcut-first vorbereitet.
- das Root-Portal ist jetzt bewusst auf den Betriebs-MVP reduziert.
- `Nextcloud`, `Paperless` und `Odoo` sind im App-SMTP-Baseline-Check gruen.
- `Jellyfin` ist fuer TV-Clients wieder erreichbar.
- Die TV-Verbindung funktioniert wieder, zuletzt ueber `Wolf`.

## Was Codex Danach Sofort Wieder Zieht

1. Sichtbare MVP-Abnahme fuer Wolf, Franz, Vault und die drei Kern-Apps ziehen.
2. Nach jedem echten manuellen Nachweis `make release-mvp-gate` erneut ziehen.
3. den Workspace dauerhaft klartextfrei halten; im Repo gilt nur noch `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`.
4. Parallel den Website-Release-Track weiter schliessen.
5. Das volle `production-gate` erst nach `PBS`, `surface-go` und `Radio` erneut als Zertifizierungssiegel werten.

## Kanonische Detailquellen

- `OPS_HOME.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/JELLYFIN_OPERATIONS.md`
- `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`

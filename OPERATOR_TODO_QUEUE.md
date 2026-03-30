# Operator Todo Queue

Stand: `2026-03-30`

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

## Surface Control Jetzt

1. Gemini-Touch-Abnahme auf dem Surface-Pfad:
   - Karten sichtbar
   - keine Dashboard-Reste
   - schnelle Bedienbarkeit
2. Deep-Link-Nacharbeit nur fuer echte Restpunkte:
   - `Nextcloud Eingang` zeigt aktuell auf Nextcloud Mail Setup und bleibt verborgen
   - `Odoo Kalender` hat aktuell keine funktionierende Route und bleibt verborgen
   - `Radio hoeren` hat aktuell keinen anonymen Public-Player und bleibt verborgen
3. `Stockenweiler` bleibt in diesem Block bewusst unsichtbar:
   - nur vorbereitete Backlog-Aktionen
   - kein Live-Rollout im Surface V1

## Website-Release Parallel

1. Wahrheitspfad bleibt:
   - `artifacts/website_release_audit/20260330_155726`
   - `artifacts/website_release_gate/20260330_155801/website_release_gate.md`
   - `artifacts/public_edge_preview/20260330_134359/report.md`
2. Zielsystem ist jetzt hart verifiziert:
   - Odoo-Website auf `VM220`
   - kein oeffentlicher Odoo-Admin- oder ERP-Pfad
   - Root-Homepage `Home | FraWo` und Radio-CTA laufen auf dem Zielpfad
3. Website-Zielpfad ist technisch vorbereitet:
   - Host `www.frawo-tech.de` auf `192.168.2.22` liefert `200 OK`
   - Host `frawo-tech.de` auf `192.168.2.22` liefert `308` auf `https://www.frawo-tech.de/`
   - `/radio/public/frawo-funk` liefert den AzuraCast-Player
   - die globale IPv6 von `VM220` liefert fuer `www.frawo-tech.de` bereits `200 OK` auf HTTP
4. Externer DNS-Cutover ist jetzt real erfolgt:
   - Apex-A `frawo-tech.de` -> `92.211.33.54`
   - Apex-AAAA `frawo-tech.de` -> `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc`
   - `www` folgt sauber auf Apex
5. Oeffentlich ist jetzt bewusst ein Hold-Modus aktiv:
   - die halbfertige Odoo-Website ist nicht mehr die oeffentliche Frontdoor
   - `frawo-tech.de` und `www.frawo-tech.de` liefern stattdessen eine neutrale Wartungs-/Aufbauseite
   - intern bleibt `odoo.hs27.internal` unveraendert auf der echten Odoo-Seite
6. Der echte Restblocker fuer den spaeteren Public-Release ist jetzt Dual-Stack / TLS:
   - `HTTPS` auf Apex und `www` bleibt rot
   - Caddy-ACME auf `VM220` trifft jetzt den richtigen Host, scheitert aber aktuell mit `92.211.33.54: Connection refused`
   - `public-dualstack-edge-check` ist jetzt explizit rot
   - `curl -4` auf Apex und `www` Port `80` time-outet weiter, `curl -6` ist gruen
   - der konkrete Naechstschritt ist damit Router-Forward `80/443` auf `192.168.2.22`
   - `UCG-Ultra` ist dafuer aktuell bewusst **nicht** der kritische Pfad, solange der Ubiquiti-2FA-Zugriff wegen des verlorenen Handys blockiert ist
7. Website-Release bleibt damit bewusst pausiert:
   - CI und Design sind noch nicht final
   - Surface Control ist jetzt der wichtigere Hauptblock
   - sichtbare Radio-Integration bleibt fuer den echten Public-Release offen
   - oeffentliche Content-Abnahme bleibt daher offen
8. SPF, DKIM und DMARC dokumentieren und testen:
   - `MX` und `DMARC` sichtbar
   - `SPF` im Live-Check aktuell nicht sichtbar
9. sichtbare Browser-Abnahme bleibt bewusst nicht release-gruen:
   - oeffentlich ist absichtlich nur die Hold-Seite sichtbar
   - HTTPS endet weiter auf Apex und `www` mit `ERR_SSL_PROTOCOL_ERROR`
10. Rollback fuer DNS-/TLS-/Hostwechsel schriftlich fertigziehen.

## Stockenweiler Danach

1. `Stockenweiler` als naechsten externen Support-Track nur nach stabilem Website-Track oeffnen.
2. Erstes Inventar festziehen:
   - Haupt-PC
   - Handy
   - Drucker / Scanner
   - Provider / Router
   - Zielablage: `manifests/stockenweiler/site_inventory.json`
   - bekannte Legacy-Fakten zuerst gegenpruefen:
     - Router `192.168.178.1`
     - Proxmox `192.168.178.25`
     - Home Assistant `192.168.178.67`
     - Drucker `192.168.178.153`
     - MagentaTV `192.168.178.120`
3. Supportpfad nur so aufbauen:
   - `Tailscale-only`
   - `AnyDesk` nur Fallback
   - keine WAN-Adminfreigaben
4. Secret-Bereich `Vaultwarden / FraWo / Stockenweiler` erst mit echten Geraeten und Providerdaten befuellen.
5. `online-prinz.de` als kanonischen externen Namen verwenden; `prinz-stockenweiler.de` nur noch als Legacy lesen.
6. UCG-Ultra fuer Stockenweiler erst wieder anfassen, wenn der 2FA-Zugriff ueber dein Handy wieder verfuegbar ist.

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
- `website-release-audit` ist jetzt nativ ohne WSL neu gelaufen: `artifacts/website_release_audit/20260330_155726`.
- `website-release-audit` zeigt jetzt zusaetzlich einen gruenen `public-edge-preview-check`: `artifacts/website_release_audit/20260330_134359`.
- `website-release-audit` zeigt jetzt zusaetzlich den echten Netzbefund:
  - `public-dualstack-edge-check=failed`
  - `IPv6` gruen
  - `IPv4` rot
- `website-release-gate` ist aktuell ehrlich `BLOCKED`: `artifacts/website_release_gate/20260330_155801/website_release_gate.md`.
- die halbfertige Odoo-Seite ist oeffentlich wieder weg; statt dessen ist jetzt bewusst ein neutraler Hold-Modus vorgeschaltet.
- der oeffentliche Website-Scope ist jetzt fachlich auf `Odoo-Website + Radio-Praesenz` gezogen; Odoo-Admin bleibt weiter intern.
- `VM220` liefert die FraWo-Website und den Radio-Pfad jetzt bereits korrekt auf dem Zielpfad:
  - Host `www.frawo-tech.de` auf `192.168.2.22` -> `Home | FraWo`
  - Host `frawo-tech.de` auf `192.168.2.22` -> `308` auf `https://www.frawo-tech.de/`
  - Host `www.frawo-tech.de` auf `/radio/public/frawo-funk` -> `FraWo - Funk - AzuraCast`
- die globale IPv6 von `VM220` liefert auf HTTP bereits den FraWo-Start; der verbleibende Public-Blocker ist der externe DNS-/TLS-Cutover und der offene IPv4-Freigabepfad.
- der DNS-Cutover zu `VM220` ist jetzt live; der aktuelle harte Restblocker fuer den Public-Release ist der fehlende IPv4-Pfad fuer ACME/TLS plus offenes Mail-DNS.
- `Vaultwarden` ist intern ueber `HTTPS` live.
- `Vaultwarden`-Invites sind per SMTP aktiviert.
- `Vaultwarden`-`ADMIN_TOKEN` ist live gehasht.
- `franz@frawo-tech.de` ist per `IMAP` und `SMTP AUTH` technisch verifiziert.
- die `Vaultwarden`-Einladungsmail an `franz@frawo-tech.de` ist erfolgreich angekommen.
- `Franz` hat die `FraWo`-Einladung angenommen.
- der Franz-Pfad ist auf portal-first und shortcut-first vorbereitet.
- das Root-Portal ist jetzt bewusst auf den Betriebs-MVP reduziert.
- Root-Portal und Franz-Seite sind sichtbar gegen den neuen MVP-Stand abgenommen.
- `Nextcloud`, `Paperless` und `Odoo` sind im App-SMTP-Baseline-Check gruen.
- `Jellyfin` ist fuer TV-Clients wieder erreichbar.
- Die TV-Verbindung funktioniert wieder, zuletzt ueber `Wolf`.
- `surface-go-frontend` liefert jetzt live `Surface Control V1` auf `http://127.0.0.1:17827`.
- der lokale Portal-Dienst `homeserver2027-surface-portal.service` ist aktiv.
- die erste sichtbare Route-Matrix fuer `Surface Control V1` ist erbracht:
  - `Paperless`, `Odoo Aufgaben`, `Odoo Projekte`, `Radio Control` = `ready`
  - `Nextcloud Eingang`, `Radio hoeren` = `verify`
  - `Odoo Kalender` = `backlog`
- die Surface-Launcher sind jetzt live auf den V1-Minimalsatz reduziert:
  - kiosk: `FRAWO Control`, `Bildschirmtastatur`
  - admin: `FRAWO Control`, `Bildschirmtastatur`, `Radio Control`, `AnyDesk`, `StudioPC Remote`
- der lokale User `frontend` ist auf dem Surface wieder bewusst mit einem gesetzten Passwortpfad nutzbar.

## Was Codex Danach Sofort Wieder Zieht

1. Sichtbare MVP-Abnahme fuer Wolf, Franz, Vault und die drei Kern-Apps ziehen.
2. Nach jedem echten manuellen Nachweis `make release-mvp-gate` erneut ziehen.
3. den Workspace dauerhaft klartextfrei halten; im Repo gilt nur noch `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`.
4. Parallel den Website-Release-Track weiter schliessen.
5. Danach `Stockenweiler` als getrennten Managed-Support-Track oeffnen.
6. Das volle `production-gate` erst nach `PBS`, `surface-go` und `Radio` erneut als Zertifizierungssiegel werten.

## Kanonische Detailquellen

- `OPS_HOME.md`
- `OPERATIONS/USER_ONBOARDING_OPERATIONS.md`
- `OPERATIONS/MAIL_OPERATIONS.md`
- `OPERATIONS/JELLYFIN_OPERATIONS.md`
- `OPERATIONS/PRODUCTION_READINESS_OPERATIONS.md`

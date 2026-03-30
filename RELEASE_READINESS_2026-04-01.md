# Release Readiness 2026-04-01

## Ziel

Geplanter externer Release am `2026-04-01` mit bewusst kleinem Scope:

- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> oeffentliche FRAWO-Website ueber die Odoo-Website
- sichtbare Radio-Praesenz oder Player-Pfad auf der Website
- keine oeffentlichen Business-UIs

## Scope In

- Domain- und DNS-Vorbereitung fuer `frawo-tech.de`
- Website-Hostnamen und Redirect-Modell
- Odoo-Website als oeffentlicher Website-Frontend-Zielpfad
- sichtbare Radio-Einbindung auf der Website
- Mailboxen fuer `wolf`, `franz`, `info`, `noreply`
- Vaultwarden als produktiver Secret Store
- Release- und Rollback-Dokumentation

## Scope Out

- Nextcloud
- Paperless
- Odoo-Admin / ERP-UI
- Home Assistant
- Proxmox
- PBS
- AdGuard
- Toolbox-Adminpfade
- breiter Radio-Public-Rollout

## Statusmatrix

| Bereich | Status | Stand | Naechste Aktion |
| --- | --- | --- | --- |
| Infra Core | green | interne Plattform laeuft stabil | weiter beobachten |
| Backup / Restore | yellow | lokale Backups sind real, aber `PBS` bleibt fuer diese Website-Freigabe bewusst ausserhalb des Scope | lokalen Schutz stabil halten und `PBS` separat weiterfuehren |
| Mail | yellow | `webmaster` und `franz` sind technisch verifiziert, aber `info`/`noreply` und sichtbare Send-/Receive-Abnahme sind noch offen | finalen Rollenpfad und Mail-Records schliessen |
| Secrets | yellow | Vaultwarden laeuft jetzt intern ueber `HTTPS`, Franz ist in `FraWo`, aber sichtbare Spotchecks und Restbereinigung laufen noch | Vaultwarden-Bestand sichtbar verifizieren und Referenzpfad beibehalten |
| Public Website | red | DNS-Cutover ist erfolgt, aber oeffentlich ist jetzt bewusst ein neutraler Hold-Modus vorgeschaltet; blockierend bleiben damit weiter TLS, IPv4-Forward, Public-Mail-DNS und die finale inhaltliche Freigabe | Hold-Modus beibehalten, IPv4-Forward fuer `80/443`, TLS und SPF/DKIM/DMARC schliessen |
| Radio Public | yellow | die Radio-Praesenz ist auf dem Zielsystem integriert und im Preview verifiziert, oeffentlich aber noch nicht sichtbar | nach echtem Public-Cutover die sichtbare Browser-Abnahme erneut ziehen |
| Device Onboarding | yellow | Business-MVP laeuft separat; fuer die Website ist kein Shared Frontend noetig | getrennt im MVP-Track schliessen |
| Stockenweiler | yellow | Zielbild klar, aber noch kein operativer Testkunde | Tailscale-only Supportpfad vorbereiten |

## Release Gates

Vor externem Release muessen gruen sein:

0. `make website-release-gate`
1. `frawo-tech.de` DNS-Modell dokumentiert und getestet
2. `www.frawo-tech.de` Zielsystem bestimmt als Odoo-Website auf `VM220`
3. Redirect `frawo-tech.de` -> `www.frawo-tech.de` dokumentiert
4. sichtbare Radio-Praesenz oder Player-Pfad auf der Website definiert und verifiziert
5. sichtbares Mailmodell fuer `webmaster`, `franz`, `info`, `noreply` dokumentiert und verifiziert
6. SPF, DKIM und DMARC gesetzt und getestet
7. Vaultwarden produktiv in `FraWo` eingefuehrt
8. produktive Logins in Vaultwarden ueberfuehrt und im Repo nur noch ueber `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` referenziert
9. Rollback fuer DNS-/TLS-/Hostwechsel dokumentiert

## Live Facts 2026-03-30

- letzter Website-Audit: `artifacts/website_release_audit/20260330_155726`
- letzter Website-Gate-Entscheid: `artifacts/website_release_gate/20260330_155801/website_release_gate.md` = `BLOCKED`
- letzter Zielpfad-Preview: `artifacts/public_edge_preview/20260330_134359/report.md` = `passed`
- `frawo-tech.de` loest aktuell oeffentlich auf `92.211.33.54` und `2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc` auf.
- `www.frawo-tech.de` folgt aktuell sauber auf `frawo-tech.de`.
- HTTP auf Apex und `www` liefert aktuell bewusst die neutrale Hold-Seite.
- HTTPS auf Apex und `www` faellt im aktuellen Live-Check mit `TLSV1_ALERT_INTERNAL_ERROR`.
- sichtbare Browser-Abnahme bestaetigt: HTTPS auf Apex und `www` endet aktuell im Browser mit `ERR_SSL_PROTOCOL_ERROR`.
- `DMARC` ist sichtbar (`p=reject`), ein `SPF`-Record ist im aktuellen Live-Check nicht sichtbar.
- `VM220` liefert die gewuenschte Odoo-Website im Zielpfad jetzt bereits intern:
  - Host `www.frawo-tech.de` auf `192.168.2.22` -> `200 OK`, Titel `Home | FraWo`
  - Host `frawo-tech.de` auf `192.168.2.22` -> `308` auf `https://www.frawo-tech.de/`
  - Host `www.frawo-tech.de` auf `/radio/public/frawo-funk` -> `200 OK`, Titel `FraWo - Funk - AzuraCast`
- die globale IPv6 von `VM220` (`2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc`) liefert fuer Host `www.frawo-tech.de` bereits `200 OK` auf HTTP.
- `public-dualstack-edge-check` ist jetzt explizit rot: `IPv6` auf Apex und `www` Port `80` ist gruen, `IPv4` auf Apex und `www` Port `80` ist weiterhin nicht erreichbar.
- die halbfertige Odoo-Oeffentlichkeit ist bewusst wieder entfernt; intern bleibt `odoo.hs27.internal` unveraendert auf der echten Odoo-Seite.
- Caddy auf `VM220` ist auf `80/443` live und ACME trifft jetzt den richtigen Zielpfad, scheitert aber aktuell mit `92.211.33.54: Connection refused`; der konkrete Restblocker ist damit der fehlende IPv4-Pfad fuer `80/443`.
- der Website-Cutover haengt aktuell nicht an `UCG-Ultra`; der geplante spaetere Gateway-Cutover bleibt wegen fehlendem Ubiquiti-2FA-Zugriff separat blockiert.
- Website-Audit und -Gate laufen jetzt direkt ueber native Python-Skripte statt ueber den kaputten WSL-Bash-Pfad.

## Nie Teil dieses Releases

- direkte Oeffnung interner Business-UIs
- oeffentliche Odoo-Admin- oder ERP-Oberflaechen
- oeffentliche AdGuard-/PBS-/Proxmox-/HA-Admins
- Standort-zu-Standort-VPN fuer externe Haushalte
- unkontrollierte Mail- oder Secret-Ablage in Markdown-Dateien

## Manuelle Abnahme

- externe DNS-Aufloesung pruefen
- externe TLS-Kette pruefen
- Testmail von Systemen versenden
- Monitoring/Uptime fuer Website pruefen
- Rollback-Pfad einmal trocken durchgehen

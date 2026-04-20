# Release Readiness 2026-04-01

## Ziel

Geplanter externer Release am `2026-04-01` mit bewusst kleinem Scope:

- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> oeffentliche FRAWO-Website ueber die Odoo-Website
- sichtbare Radio-Praesenz oder Player-Pfad auf der Website
- keine oeffentlichen Business-UIs

Aktueller Lane-B-Zwischenfokus Stand `2026-04-20`:

- zuerst gueltiges HTTPS fuer `frawo-tech.de` und `www.frawo-tech.de`
- Public Edge technisch gruen ziehen
- Website-Design und Content duerfen bis spaeter vorlaeufig bleiben

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
| Public Website | red | DNS-Cutover ist erfolgt, aber HTTPS/Public-Edge bleibt blockiert; bevorzugter Lane-B-Pfad ist jetzt Cloudflare vor `VM220`, weil die EasyBox auf dem direkten IPv4-Pfad weiter im DS-Lite-Problem haengt | Cloudflare-Proxy/Tunnel fuer `frawo-tech.de` und `www.frawo-tech.de` finalisieren; Dual-Stack bleibt nur Ausweichpfad |
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
- der bisherige Hold-Pfad auf `VM220` ist nach dem Odoo-Hardening aktuell nicht mehr live; der Public-Release ist damit gerade klar pausiert statt halb online.
- HTTPS auf Apex und `www` ist damit weiterhin nicht releasefaehig und bleibt blockiert.
- `DMARC` ist sichtbar (`p=reject`), ein `SPF`-Record ist im aktuellen Live-Check nicht sichtbar.
- `VM220` liefert die gewuenschte Odoo-Website im Zielpfad jetzt bereits intern:
  - Host `www.frawo-tech.de` auf `10.1.0.22` -> `200 OK`, Titel `Home | FraWo`
  - Host `frawo-tech.de` auf `10.1.0.22` -> `308` auf `https://www.frawo-tech.de/`
  - Host `www.frawo-tech.de` auf `/radio/public/frawo-funk` -> `200 OK`, Titel `FraWo - Funk - AzuraCast`
- die direkte Odoo-Exposition wurde am `2026-03-30` zusaetzlich gehaertet:
  - `8069` bindet jetzt nur noch auf `192.168.2.22`
  - direkter externer Zugriff auf `http://[2a00:1e:ef80:7c01:be24:11ff:feaa:bbcc]:8069/web/login` ist nicht mehr moeglich
  - `SSH/22` ist ebenfalls nicht mehr ueber die globale IPv6 erreichbar
- zusaetzliche direkte Public-IPv6-Expositionen wurden am `2026-03-31` ebenfalls geschlossen:
  - `nextcloud`: `22`, `80`
  - `paperless`: `22`, `8000`
  - `vaultwarden`: `22`, `8080`
  - `storage-node`: `22`, `139`, `445`
- aktueller Nachweis dafuer: `artifacts/public_ipv6_exposure_audit/latest_report.md` = `open_checks=0`
- der aktuelle Website-Track braucht vor Wiederaufnahme einen bewussten, gehaerteten Public-Edge-Pfad statt eines zufaelligen Mitlaufens auf `VM220`.
- bevorzugter Release-Pfad Stand `2026-04-20`: `Cloudflare` vor `VM220`; echter direkter IPv4-/Dual-Stack-Cutover bleibt nur Alternativpfad.
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

## Decision Note 2026-04-20

Fuer den aktuellen Website-Track gilt:

- bevorzugte Release-Entscheidung: `Cloudflare proxy/tunnel -> VM220`
- Alternativpfad nur bei echter externer Freigabe: `Dual-Stack/IPv4 -> VM220`
- `CT100 toolbox` ist kein primaeres Public-Website-Zielsystem
- Public Edge, Public Mail DNS und Rollback bleiben Lane-B-Themen und werden nicht mit Radio/PBS vermischt

Fuer den aktuellen Lane-B-Arbeitsmodus gilt zusaetzlich:

- Erfolg heisst zunaechst: HTTPS/Public Edge gruen
- nicht zwingend: finale Website-Gestaltung oder finaler Content-Stand

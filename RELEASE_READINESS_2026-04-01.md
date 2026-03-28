# Release Readiness 2026-04-01

## Ziel

Geplanter externer Release am `2026-04-01` mit bewusst kleinem Scope:

- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> oeffentliche FRAWO-Website
- keine oeffentlichen Business-UIs

## Scope In

- Domain- und DNS-Vorbereitung fuer `frawo-tech.de`
- Website-Hostnamen und Redirect-Modell
- Mailboxen fuer `wolf`, `franz`, `info`, `noreply`
- Vaultwarden als produktiver Secret Store
- Release- und Rollback-Dokumentation

## Scope Out

- Nextcloud
- Paperless
- Odoo
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
| Public Website | yellow | Zielbild klar, aber Website-/DNS-/TLS-Rollout offen | Public-Website-Runbook finalisieren |
| Radio Public | yellow | intern und Tailscale-only stabil | erst nach separatem Green Gate freigeben |
| Device Onboarding | yellow | Business-MVP laeuft separat; fuer die Website ist kein Shared Frontend noetig | getrennt im MVP-Track schliessen |
| Stockenweiler | yellow | Zielbild klar, aber noch kein operativer Testkunde | Tailscale-only Supportpfad vorbereiten |

## Release Gates

Vor externem Release muessen gruen sein:

1. `frawo-tech.de` DNS-Modell dokumentiert und getestet
2. `www.frawo-tech.de` Zielsystem bestimmt
3. Redirect `frawo-tech.de` -> `www.frawo-tech.de` dokumentiert
4. sichtbares Mailmodell fuer `webmaster`, `franz`, `info`, `noreply` dokumentiert und verifiziert
5. SPF, DKIM und DMARC gesetzt und getestet
6. Vaultwarden produktiv in `FraWo` eingefuehrt
7. produktive Logins in Vaultwarden ueberfuehrt und im Repo nur noch ueber `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md` referenziert
8. Rollback fuer DNS-/TLS-/Hostwechsel dokumentiert

## Nie Teil dieses Releases

- direkte Oeffnung interner Business-UIs
- oeffentliche AdGuard-/PBS-/Proxmox-/HA-Admins
- Standort-zu-Standort-VPN fuer externe Haushalte
- unkontrollierte Mail- oder Secret-Ablage in Markdown-Dateien

## Manuelle Abnahme

- externe DNS-Aufloesung pruefen
- externe TLS-Kette pruefen
- Testmail von Systemen versenden
- Monitoring/Uptime fuer Website pruefen
- Rollback-Pfad einmal trocken durchgehen

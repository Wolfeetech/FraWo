# Public Edge Architecture Plan

## Ziel

Dieses Dokument beschreibt den professionellen Zielpfad fuer die spaetere Oeffnung einzelner Dienste zur Oeffentlichkeit.

Es geht ausdruecklich nicht um sofortige Freigabe, sondern um:

- klare Trennung zwischen internem Betrieb und externer Exposition
- saubere Vorbedingungen
- definierte oeffentliche Dienste
- Rollback und Monitoring

## Release-Default

Stand `2026-03-26` ist der freigegebene Release-Scope fuer `2026-04-01` bewusst klein:

- `frawo-tech.de` leitet spaeter auf `www.frawo-tech.de` um
- `www.frawo-tech.de` ist die erste oeffentliche FRAWO-Website
- interne Apps bleiben intern oder Tailscale-only
- `radio.frawo-tech.de` bleibt vorbereitet, aber nicht Teil des ersten Releases

## Grundsatz

Oeffentliche Freigaben starten erst, wenn:

- das interne Business-MVP sichtbar stabil ist
- Zielsystem, DNS, TLS, Logging und Rollback definiert sind
- der Website-Scope strikt klein gehalten wird
- Domain, DNS, TLS, Auth, Logging und Rollback definiert sind
- der Passwortmanager produktiv eingefuehrt ist

## Verbindlicher Domain-Pfad

Stand heute ist der bevorzugte oeffentliche Markenpfad:

- primaere Domain: `frawo-tech.de`
- Website: `www.frawo-tech.de`
- Radio-/Player-Pfad spaeter: `radio.frawo-tech.de`

Betriebsregel dazu:

- `www.frawo-tech.de` wird der kanonische Web-Hostname.
- `frawo-tech.de` leitet auf `www.frawo-tech.de` um.
- `radio.frawo-tech.de` bleibt technisch getrennt von der Hauptwebsite.
- interne Namen bleiben bis zur bewussten internen DNS-Migration unveraendert:
  - `portal.hs27.internal`
  - `radio.hs27.internal`
  - `media.hs27.internal`
- spaeterer professioneller Zielpfad fuer interne Namen ist `frawo.home.arpa`.

Veraltet und nicht mehr Zielbild:

- `frawo.studio`
- `www.frawo.studio`
- `radio.frawo.studio`

## Nie oeffentlich exponieren

- Proxmox
- PBS-Admin
- AdGuard-Admin
- Home-Assistant-Admin
- interne Toolbox-Adminpfade
- rohe Datenbankports
- interne Nextcloud-, Paperless- oder Odoo-Admins

## Geplante oeffentliche Dienste

### Phase 1

- statische oder sehr schlanke GbR-Website auf `www.frawo-tech.de`
- optional Kontaktformular-/Lead-Pfad

### Phase 2

- oeffentliche Radio-/Player-Seite auf `radio.frawo-tech.de`
- spaeter Stream-Endpunkte

### Phase 3

- nur bewusst entschiedene Kunden-/Portalpfade
- keine direkte Vermischung mit internen Admin-Oberflaechen

## Architekturprinzip

### Website

- getrennt von Odoo-Admin und internen Business-UIs
- als eigene Brochure-/Landing-Site
- Odoo spaeter nur punktuell fuer CRM/Leads/Portal

### Edge

- Reverse Proxy mit TLS
- explizite Hostname-Freigaben
- Logging
- Monitoring
- Rollback

### DNS

- Apex- und `www`-Strategie fuer `frawo-tech.de`
- spaeter eigene Subdomains wie:
  - `radio.frawo-tech.de`
  - optional `portal.frawo-tech.de` nur bei echtem Produktgrund

Bevorzugter Zielpfad dafuer:

- `frawo-tech.de` -> Redirect auf `www.frawo-tech.de`
- `www.frawo-tech.de` -> GbR-Website
- `radio.frawo-tech.de` -> Radio-/Player-Seite
- kein oeffentliches `portal.frawo-tech.de`, solange kein klarer Produktgrund besteht

### Zertifikate

- nur automatisiert
- keine manuellen Dauer-Zertifikatsprozesse

## Vorbedingungen

Vor dem ersten Public Rollout muessen gruen sein:

- `RELEASE_READINESS_2026-04-01.md`
- `make release-mvp-gate`
- Zielsystem fuer `www.frawo-tech.de` ist bestimmt
- DNS-/Redirect-Modell ist dokumentiert
- TLS-Automation ist festgelegt
- SPF, DKIM und DMARC sind sauber gesetzt
- dokumentierter DNS-/TLS-/Rollback-Pfad
- produktiver Passwortmanager mit den relevanten Logins

## Rollout-Reihenfolge

1. `frawo-tech.de` final dokumentieren
2. Public DNS-Modell festziehen
3. Mailboxen und DNS-Mail-Records sauber setzen
4. Edge-Hostnamen festlegen
5. TLS-Automation einrichten
6. Logging und Uptime-Monitoring festlegen
7. zuerst statische GbR-Seite veroeffentlichen
8. erst spaeter Radio
9. Business-/Portalpfade nur bewusst und spaet

## Definition of Done

Minimal fertig:

- Domain vorhanden
- Website getrennt geplant
- keine Admin-UIs oeffentlich

Professionell fertig:

- Gateway unter Kontrolle
- PBS/Restore belastbar
- oeffentliche Hostnames klar getrennt
- TLS, Logging, Monitoring und Rollback aktiv
- Secrets nicht mehr dauerhaft in Markdown-Dateien abgelegt

# Public Edge Architecture Plan

## Ziel

Dieses Dokument beschreibt den professionellen Zielpfad fuer die spaetere Oeffnung einzelner Dienste zur Oeffentlichkeit.

Es geht ausdruecklich nicht um sofortige Freigabe, sondern um:

- klare Trennung zwischen internem Betrieb und externer Exposition
- saubere Vorbedingungen
- definierte oeffentliche Dienste
- Rollback und Monitoring

## Grundsatz

Oeffentliche Freigaben starten erst, wenn:

- Gateway-Cutover sauber abgeschlossen ist
- PBS produktiv ist
- Restore-Drills belastbar sind
- Inventar und Zonen final sind
- eine echte Domain vorhanden ist

## Bevorzugter Domain-Kandidat

Stand heute ist der bevorzugte oeffentliche Markenpfad:

- primaere Domain: `frawo.studio`
- Website: `www.frawo.studio`
- Radio-/Player-Pfad: `radio.frawo.studio`

Betriebsregel dazu:

- `www.frawo.studio` wird spaeter der kanonische Web-Hostname.
- `frawo.studio` leitet spaeter auf `www.frawo.studio` um.
- `radio.frawo.studio` bleibt technisch getrennt von der Hauptwebsite.
- interne Namen bleiben bis zur bewussten internen DNS-Migration unveraendert:
  - `portal.hs27.internal`
  - `radio.hs27.internal`
- spaeterer professioneller Zielpfad fuer interne Namen ist `frawo.home.arpa`; `frawo.internal` und `frawo.lan` werden nicht als Zielzone eingeplant.

Optional spaeter:

- `stream.frawo.studio` nur wenn ein separater reiner Stream-Endpunkt sinnvoll wird
- defensive Zusatzregistrierungen wie `.de` oder `.tech` nur wenn Budget und Verfuegbarkeit dafuer sprechen

## Nie oeffentlich exponieren

- Proxmox
- PBS-Admin
- AdGuard-Admin
- Home-Assistant-Admin
- interne Toolbox-Adminpfade
- rohe Datenbankports

## Geplante oeffentliche Dienste

### Phase 1

- statische oder sehr schlanke GbR-Website
- optional Kontaktformular-/Lead-Pfad

### Phase 2

- oeffentliche Radio-/Player-Seite
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

- Apex- und `www`-Strategie fuer die GbR-Domain
- spaeter eigene Subdomains wie:
  - `radio.<domain>`
  - optional `portal.<domain>` nur wenn wirklich gewollt

Bevorzugter Zielpfad dafuer:

- `frawo.studio` -> Redirect auf `www.frawo.studio`
- `www.frawo.studio` -> GbR-Website
- `radio.frawo.studio` -> Radio-/Player-Seite
- kein oeffentliches `portal.frawo.studio`, solange kein klarer Produktgrund besteht

### Zertifikate

- nur automatisiert
- keine manuellen Dauer-Zertifikatsprozesse

## Vorbedingungen

Vor dem ersten Public Rollout muessen gruen sein:

- `make gateway-cutover-stage-gate`
- `make pbs-stage-gate`
- Inventar final ohne `unknown-review`
- dokumentierter DNS-/TLS-/Rollback-Pfad

## Rollout-Reihenfolge

1. `frawo.studio` registrieren und dokumentieren
2. Public DNS-Modell festziehen
3. Edge-Hostnamen festlegen
4. TLS-Automation einrichten
5. Logging und Uptime-Monitoring festlegen
6. zuerst statische GbR-Seite veroeffentlichen
7. erst spaeter Radio
8. Business-/Portalpfade nur bewusst und spaet

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

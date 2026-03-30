# Stockenweiler Remote Support Plan

## Ziel

`Rentner OS` fuer Stockenweiler ist der erste externe Testkundenfall fuer betreute IT ausserhalb des Hauptstandorts.

Ziel ist eine selbstaendig nutzbare Umgebung mit kontrolliertem Fernzugriff von FRAWO aus.

## Aktueller Status

- noch nicht im aktiven Rollout
- kein integrierter Zweitstandort
- naechster externe Ausbaupfad nach stabilem Website-Track
- Betriebsmodell bleibt bewusst klein: betreuter Endpunkt-Support statt Standortvernetzung
- das erste kanonische Inventar lebt jetzt in `manifests/stockenweiler/site_inventory.json`
- lokale Altquellen auf `StudioPC` sind gesichtet; erste belastbare Fakten wurden ins Inventar uebernommen
- schneller Plausibilitaetscheck jetzt per `make stockenweiler-inventory-check`
- kompakter Operator-Ueberblick jetzt per `make stockenweiler-support-brief`
- aktueller Checkstand:
  - `7` Endpunkte modelliert
  - `2` noch komplett offen
  - `5` Legacy-Fakten warten auf echte Revalidierung

## V1 Scope

- verwalteter Haupt-PC
- verwaltetes Handy
- Scanner-/Dokumentenpfad
- Drucker-/Peripheriehilfe
- Fernhilfe bei Technikproblemen

## Nicht in V1

- volles Smart Home
- oeffentliche Adminflaechen im Elternhaus
- Standort-zu-Standort-VPN
- zweiter voll integrierter Unternehmensstandort

## Zugriffsmodell

- primaer `Tailscale-only`
- `AnyDesk` nur als GUI-/Benutzerfallback
- keine offenen WAN-Ports
- keine direkte Oeffnung von Admin-UIs

## Servicegedanke

`Rentner OS` ist zunaechst ein Managed Support Service:

- die Eltern nutzen ihre Geraete selbst
- FRAWO kann kontrolliert eingreifen, wenn Technikprobleme auftreten
- die Betriebsverantwortung bleibt dokumentiert und nachvollziehbar

## Identitaets- und Secret-Modell

- eigener Bereich `Stockenweiler` in `Vaultwarden / FraWo`
- getrennte Eintraege fuer Geraete, Tailscale, AnyDesk und Provider
- keine Vermischung mit internen FRAWO-Adminlogins

## Dokumentenpfad

- wenn Dokumentenscan relevant wird, denselben Nextcloud-/Paperless-Grundpfad verwenden
- zuerst ueber einfache, betreute Benutzerflows
- keine Sonderlogik nur fuer Stockenweiler bauen, solange der Standardpfad reicht

## Externer Name

- `online-prinz.de` ist der aktuelle kanonische externe Zielname
- `prinz-stockenweiler.de` bleibt nur Legacy-Kontext aus aelteren Workspaces
- zunaechst nur als Support-/Remote-Kontext, nicht als Release-Website

## Aktuell belastbare Legacy-Fakten

- lokaler Router-Export auf `StudioPC` zeigt aktuell:
  - `FRITZ!Box 5690 Pro` auf `192.168.178.1`
  - Telekom als Provider
  - `proxmox Host` auf `192.168.178.25`
  - `homeassistant` auf `192.168.178.67`
  - `Brother - Drucker` auf `192.168.178.153`
  - `MagentaTV` auf `192.168.178.120`
- aeltere `RadioWorkspace`-Doku bestaetigt den vorhandenen externen Server-/Support-Kontext, ist aber nicht mehr kanonisch
- alle diese Punkte gelten als `legacy_fact_needs_revalidation`, bis der erste echte Stockenweiler-Onboarding-Lauf sie sichtbar bestaetigt

## Integrationsprinzip

- Stockenweiler bleibt erst einmal ein getrennter betreuter Support-Standort
- kein direktes Vermischen der internen FRAWO-Infrastruktur mit dem Elternhaus-LAN
- Home Assistant fuer den Vater ist als spaetere, bewusst getrennte Erweiterung denkbar:
  - entweder als eigener externer Home-/Site-Kontext
  - oder zuerst nur als Remote-Support auf dem vorhandenen lokalen Home-Assistant-System
- solange der echte Bedarf nicht sichtbar verifiziert ist, bauen wir keinen komplexen Verbund und keine Sonderarchitektur

## Minimum Definition of Done

1. Tailscale-Zugriff dokumentiert
2. Fallback ueber AnyDesk dokumentiert
3. Haupt-PC und Handy als betreute Endpunkte erfasst
4. Passwort- und Providerdaten in `Vaultwarden / FraWo` abgelegt
5. kein oeffentlich exponierter Adminpfad aktiv

## Naechste Einstiegsschritte

1. erstes echtes Inventar aufnehmen:
   - Haupt-PC
   - Handy
   - Drucker / Scanner
   - Router / Provider
   - Zielablage: `manifests/stockenweiler/site_inventory.json`
2. Remote-Support-Standard pruefen:
   - `Tailscale`
   - `AnyDesk` nur Fallback
3. getrennten Secret-Bereich `Stockenweiler` in `Vaultwarden / FraWo` nur mit echten Daten befuellen
4. keinen Sonderpfad fuer Dokumente bauen, solange Nextcloud/Paperless-Standard reicht
5. keine WAN-Freigabe und kein Site-to-Site-VPN in V1

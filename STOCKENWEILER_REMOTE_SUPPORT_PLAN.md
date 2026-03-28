# Stockenweiler Remote Support Plan

## Ziel

`Rentner OS` fuer Stockenweiler ist der erste externe Testkundenfall fuer betreute IT ausserhalb des Hauptstandorts.

Ziel ist eine selbstaendig nutzbare Umgebung mit kontrolliertem Fernzugriff von FRAWO aus.

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

- `prinz-stockenweiler.de` bleibt der dokumentierte externe Zielname
- zunaechst nur als Support-/Remote-Kontext, nicht als Release-Website

## Minimum Definition of Done

1. Tailscale-Zugriff dokumentiert
2. Fallback ueber AnyDesk dokumentiert
3. Haupt-PC und Handy als betreute Endpunkte erfasst
4. Passwort- und Providerdaten in `Vaultwarden / FraWo` abgelegt
5. kein oeffentlich exponierter Adminpfad aktiv

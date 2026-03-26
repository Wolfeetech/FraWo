# Bitwarden And STRATO Execution Runbook

## Ziel

Dieses Runbook ist der konkrete Umsetzungsweg fuer den naechsten echten Block:

1. `STRATO` produktiv einfuehren
2. reale FRAWO-Mailboxen bei `STRATO` anlegen
3. `Vaultwarden` intern per `HTTPS` sauber vor den ersten produktiven Gebrauch stellen
4. produktive Logins aus den Arbeitsdateien sauber nach `Vaultwarden` ueberfuehren

## Vorbedingungen

- interne Plattform laeuft stabil
- `ACCESS_REGISTER.md` enthaelt den aktuellen Arbeitsstand
- Release-Scope bleibt weiter `website-first`

## Teil A - STRATO zuerst

### Zielbild

- echte FRAWO-Mailboxen existieren
- das Henne-Ei-Problem fuer Identitaet ist geloest
- neue Mail-Passwoerter werden bis zum Vaultwarden-HTTPS-Rollout nur offline uebergangsweise gehalten

### Struktur

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`
- `info@frawo-tech.de`
- `noreply@frawo-tech.de`

### Reihenfolge

1. `frawo-tech.de` im STRATO-Panel oeffnen.
2. Die vier Ziel-Mailboxen anlegen.
3. Passwoerter sofort offline sichern.
4. Testlogin und Testmail je Postfach durchfuehren.
5. `noreply@frawo-tech.de` als spaeteren SMTP-Absender festziehen.

### Betriebsregeln

- keine neuen Mail-Passwoerter nur im Browser lassen
- `info@frawo-tech.de` ist kein persoenlicher Admin-Login
- globale Mail-Weiterleitung zum Server ist nicht der Standard

## Teil B - Vaultwarden ueber internen HTTPS-Pfad

### Zielbild

- `vault.hs27.internal` zeigt intern auf `CT120`
- Zugriff laeuft ueber `HTTPS`
- die Organisation `FraWo` ist der gemeinsame Secret-Rahmen fuer die GbR
- erster produktiver Benutzer kann sauber angelegt werden
- danach werden die produktiven Eintraege aus `ACCESS_REGISTER.md` eingepflegt

### Organisation FraWo

- Name: `FraWo`
- Mitglieder:
  - `wolf@frawo-tech.de` als erster Owner und DevOps-/Betriebsverantwortlicher
  - `franz@frawo-tech.de` als zweiter produktiver Benutzer
- Standortkontexte:
  - `Anker` = Basisserver und privates Kernnetz
  - `Villa` = Studio-/Radio-Kontext
  - `Stockenweiler` = separater externer Support-Standort

### Collections

- `Core Infra`
- `Business Apps`
- `Media`
- `Mail & Domains`
- `Devices`
- `Stockenweiler`

### Reihenfolge

1. `vault.hs27.internal` ueber AdGuard/Caddy auf `CT120` routen.
2. Interne TLS-Ausgabe fuer `vault.hs27.internal` aktivieren.
3. Den internen Root-CA-Pfad auf den relevanten Clients bewusst vertrauen oder einen anderen verifizierten internen TLS-Pfad waehlen.
4. Wolf legt den ersten Vaultwarden-Benutzer an.
5. Die Organisation `FraWo` anlegen.
6. Die sechs Collections anlegen.
7. Franz wird danach als zweiter produktiver Benutzer eingeladen.
8. Danach werden die produktiven Eintraege aus `ACCESS_REGISTER.md` eingepflegt.

### Eintraege zuerst

- `STRATO Kunden-Login`
- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`
- `info@frawo-tech.de`
- `noreply@frawo-tech.de`
- `Nextcloud Admin`
- `Paperless Admin`
- `Odoo Admin`
- `Home Assistant`
- `Jellyfin Admin`
- `AzuraCast Admin`
- `AdGuard Admin`

### Betriebsregeln

- keine neuen produktiven Passwoerter nur in Markdown halten
- nach erfolgreichem Einpflegen wird `ACCESS_REGISTER.md` spaeter auf Referenzen reduziert
- Vaultwarden bleibt self-hosted und ist ohne internen HTTPS-Pfad noch nicht produktiv fertig
- aktueller Homeserver-Bestand wird standardmaessig dem Standort `Anker` zugeordnet
- `Villa`-Logins sind fuer Studio-/Radio-Kontexte zu kennzeichnen
- `Stockenweiler` bleibt ein eigener Standort- und Collection-Kontext

## Teil C - Mail-Integration sauber vorbereiten

### Ziel-Mailboxen

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`
- `info@frawo-tech.de`
- `noreply@frawo-tech.de`
- spaeter `documents@frawo-tech.de`

### Reihenfolge

1. `noreply@frawo-tech.de` als App-Absender festziehen.
2. spaeter `documents@frawo-tech.de` fuer Paperless-Eingang einrichten.
3. `Paperless` ueber IMAP an die Dokumenten-Mailbox haengen.
4. `Nextcloud` als Arbeitsablage und Spiegel fuer Archiv-/Eingangsordner nutzen.
5. Keine globale Weiterleitung aller Mails auf den Server bauen.

### Zielnutzung

- `wolf@frawo-tech.de`: primaere Admin- und Owner-Identitaet
- `franz@frawo-tech.de`: persoenliche Standard-Identitaet
- `info@frawo-tech.de`: Kontakt/Inbound
- `noreply@frawo-tech.de`: Systemmails
- `documents@frawo-tech.de`: spaeter dedizierter Dokumenteneingang fuer Paperless

## Teil D - Sofortige Rueckkopplung in den Workspace

Nach erfolgreicher Einrichtung:

1. `ACCESS_REGISTER.md` aktualisieren
2. `MAIL_SYSTEM_ROLLOUT.md` auf echten Stand bringen
3. `PLATFORM_STATUS.md` bei `Mail` und `Secrets` anheben
4. `RELEASE_READINESS_2026-04-01.md` teilweise auf Gruen ziehen

## Automatisierter Import in FraWo

### Ziel

- keine manuelle Einzelpflege fuer den aktuellen Basisbestand
- collection-spezifische CSV-Dateien fuer die `FraWo`-Organisation
- Standortkontext in den Importnotizen mitgeben

### Befehle

1. Gesamten aktuellen Bestand nur pruefen:
   - `python scripts/export_access_register_to_vaultwarden_csv.py --dry-run`
2. Collection-spezifische Importdateien fuer den Basisstand erzeugen:
   - `python scripts/export_access_register_to_vaultwarden_csv.py --site Anker --split-by-collection`
3. Jede erzeugte CSV in die passende `FraWo`-Collection importieren.
4. Lokale CSV-Dateien danach wieder loeschen.

## Teil E - Nach dem Import sofort verifizieren

### Ziel

- kein Blindflug nach dem CSV-Import
- passwortfreier Referenzstand fuer Betrieb und Audit
- Klartext nur so lange behalten, bis der Import sichtbar sauber ist

### Verifikation

1. In `FraWo` die erwarteten Collection-Zahlen pruefen:
   - `Business Apps`: `10`
   - `Core Infra`: `2`
   - `Media`: `5`
2. Stichprobe mit den erwarteten Item-Namen:
   - `Nextcloud Admin`
   - `Paperless Admin`
   - `Odoo Admin`
   - `AdGuard Admin`
   - `AzuraCast Admin`
   - `Jellyfin - TV Wohnzimmer`
3. Danach den passwortfreien Referenzauszug neu bauen:
   - `python scripts/build_vaultwarden_reference_register.py`
4. Den erzeugten Referenzauszug als neue Arbeitsreferenz nutzen:
   - `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
5. Erst dann die lokalen Klartext-CSV-Dateien loeschen und den Rueckbau von `ACCESS_REGISTER.md` planen.

### Betriebsregel

- Der Referenzauszug darf keine Passwoerter enthalten.
- `ACCESS_REGISTER.md` bleibt nur Uebergangsquelle, bis der Import in Vaultwarden sichtbar verifiziert ist.
- Wenn ein frueher Export bereits importiert wurde, `AdGuard Admin` manuell auf `http://127.0.0.1:3000` pruefen.

## Definition Of Done

- Organisation `FraWo` existiert
- `wolf@frawo-tech.de` und `franz@frawo-tech.de` sind korrekt angelegt
- Collections und Standortkontexte sind sauber etabliert
- STRATO-Mailboxen sind produktiv vorhanden
- Vaultwarden ist intern ueber HTTPS erreichbar
- Wolf hat den ersten produktiven Vaultwarden-Zugang
- die relevanten produktiven Logins liegen in Vaultwarden
- die vier STRATO-Mailboxen existieren
- erste Testmails funktionieren
- die Arbeitsdokumente spiegeln den neuen echten Stand

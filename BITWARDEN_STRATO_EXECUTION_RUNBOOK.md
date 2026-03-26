# Bitwarden And STRATO Execution Runbook

## Ziel

Dieses Runbook ist der konkrete Umsetzungsweg fuer den naechsten echten Block:

1. `Bitwarden Cloud` produktiv einfuehren
2. reale FRAWO-Mailboxen bei `STRATO` anlegen
3. produktive Logins aus den Arbeitsdateien sauber in Bitwarden ueberfuehren

## Vorbedingungen

- interne Plattform laeuft stabil
- `ACCESS_REGISTER.md` enthaelt den aktuellen Arbeitsstand
- Release-Scope bleibt weiter `website-first`

## Teil A - Bitwarden Cloud

### Zielbild

- ein gemeinsamer produktiver Passwortspeicher
- keine dauerhafte Klartext-SSOT in Markdown
- getrennte Bereiche fuer Betrieb und spaeter Stockenweiler

### Struktur

- `Core Infra`
- `Business Apps`
- `Media`
- `Mail & Domains`
- `Devices`
- `Stockenweiler`

### Reihenfolge

1. Wolf legt den Bitwarden-Account an.
2. Eine Organisation wird erstellt.
3. Franz wird eingeladen.
4. Die sechs Sammlungen oben werden angelegt.
5. Danach werden die produktiven Eintraege aus `ACCESS_REGISTER.md` eingepflegt.

### Eintraege zuerst

- `Nextcloud Admin`
- `Paperless Admin`
- `Odoo Admin`
- `Home Assistant`
- `Jellyfin Admin`
- `AzuraCast Admin`
- `AdGuard Admin`
- `wolf` / `franz` / `frontend` fuer Nextcloud und Paperless
- `Wolf` / `Franz` / `TV Wohnzimmer` fuer Jellyfin

### Betriebsregeln

- keine neuen produktiven Passwoerter nur in Markdown halten
- nach erfolgreichem Einpflegen wird `ACCESS_REGISTER.md` spaeter auf Referenzen reduziert
- Bitwarden bleibt jetzt Cloud-basiert; Self-Hosting ist ein spaeterer separater Workstream

## Teil B - STRATO Mailboxen

### Ziel-Mailboxen

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`
- `info@frawo-tech.de`
- `noreply@frawo-tech.de`

### Reihenfolge

1. Im STRATO-Panel `frawo-tech.de` oeffnen.
2. Die vier Ziel-Mailboxen anlegen.
3. Passwoerter sofort in Bitwarden unter `Mail & Domains` speichern.
4. SPF, DKIM und DMARC fuer `frawo-tech.de` dokumentieren.
5. Testlogin und Testmail je Postfach durchfuehren.

### Zielnutzung

- `wolf@frawo-tech.de`: primaere Admin- und Owner-Identitaet
- `franz@frawo-tech.de`: persoenliche Standard-Identitaet
- `info@frawo-tech.de`: Kontakt/Inbound
- `noreply@frawo-tech.de`: Systemmails

## Teil C - Sofortige Rueckkopplung in den Workspace

Nach erfolgreicher Einrichtung:

1. `ACCESS_REGISTER.md` aktualisieren
2. `MAIL_SYSTEM_ROLLOUT.md` auf echten Stand bringen
3. `PLATFORM_STATUS.md` bei `Mail` und `Secrets` anheben
4. `RELEASE_READINESS_2026-04-01.md` teilweise auf Gruen ziehen

## Definition Of Done

- Bitwarden-Organisation ist produktiv vorhanden
- Wolf und Franz haben Zugriff
- die relevanten produktiven Logins liegen in Bitwarden
- die vier STRATO-Mailboxen existieren
- erste Testmails funktionieren
- die Arbeitsdokumente spiegeln den neuen echten Stand

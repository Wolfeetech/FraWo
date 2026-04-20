# Handover Guide: Cloudflare Public Edge Finalization

Dieses Dokument beschreibt den bevorzugten Public-Edge-Pfad Stand `2026-04-20`.

Ziel ist nicht mehr ein alter Alpha-Zwischenstand, sondern ein sauberer kleiner Produktionspfad:

- `Cloudflare` als oeffentlicher Edge
- `VM220 odoo` als primaerer Origin
- `frawo-tech.de` und `www.frawo-tech.de` als einziger Scope
- keine oeffentlichen Admin-UIs

Der aktuelle Lane-B-Arbeitsmodus ist bewusst klein:

- zuerst HTTPS/Public Edge gruen ziehen
- die Website darf in Design und Content noch vorlaeufig sein
- der volle inhaltliche Website-Release ist ein spaeterer Folgeschritt

## Decision Stand

- bevorzugter HTTPS-/Release-Pfad: `Cloudflare -> VM220`
- Alternativpfad nur bei echter externer Freigabe: direkter IPv4-/Dual-Stack-Pfad auf `VM220`
- `CT100 toolbox` bleibt intern und ist nicht das primaere Public-Website-Ziel

## Repo-Side Preconditions Already Green

- Odoo-Website auf `VM220` antwortet intern im Zielpfad
- Apex-Redirect und `www`-Website sind auf dem Origin vorbereitet
- Radio-Praesenz auf `/radio/public/frawo-funk` ist im Zielpfad verifiziert
- Business-MVP ist separat gruen; Website-Track bleibt trotzdem noch `BLOCKED`
- der direkte IPv4-/ACME-Pfad bleibt durch DS-Lite blockiert, deshalb ist `Cloudflare` jetzt der bevorzugte Entschaerfungspfad

## Operator-Side Activation Steps

### 1. Create or Choose the Production Cloudflare Edge

- in `Cloudflare Zero Trust` einen produktiven Tunnel fuer FraWo waehlen oder neu anlegen
- Scope klein halten: nur `frawo-tech.de` und `www.frawo-tech.de`
- keine internen Admin-Pfade, keine Toolbox-Adminflaechen, keine Business-UIs

### 2. Point Cloudflare Only To VM220

- Origin fuer `www.frawo-tech.de`: `VM220` / Odoo-Website
- Apex `frawo-tech.de` bleibt Redirect auf `https://www.frawo-tech.de/`
- keine Vermischung mit `toolbox` als primaerer Website-Origin

### 3. Provide the Production Token Only Out-Of-Band

- den `TunnelToken` nicht in Markdown, nicht in Git und nicht in Klartext-Notizen ablegen
- Token nur operator-seitig in die Runtime geben

### 4. Deploy the Persistent Edge Runtime

- Zielpfad auf dem Host: `/opt/homeserver2027/stacks/odoo/`
- relevante Dateien und Skripte:
  - `docker-compose.public-edge.yml`
  - `Caddyfile.public`
  - `scripts/business/deploy_cloudflare_tunnel.sh`
  - `scripts/deploy_odoo_public_edge_preview.ps1`

Wenn der produktive Token vorliegt, den Runtime-Pfad bewusst nur auf `VM220` aktivieren.

### 5. Finalize DNS In Cloudflare

- `www.frawo-tech.de` auf den produktiven Cloudflare-Zielpfad legen
- Apex `frawo-tech.de` sauber auf `https://www.frawo-tech.de/` redirecten
- kein oeffentliches Routing auf Odoo-Admin, Toolbox, Nextcloud, Paperless, HA, PBS oder Proxmox

## Validation After Cutover

Nach Aktivierung muessen sichtbar gruen werden:

1. `http://frawo-tech.de` -> `308` auf `https://www.frawo-tech.de/`
2. `https://www.frawo-tech.de` liefert die echte FraWo-Website
3. `https://www.frawo-tech.de/radio/public/frawo-funk` liefert die sichtbare Radio-Praesenz
4. `make website-release-gate` bleibt der formale Freigabepunkt fuer den spaeteren vollen Website-Release

Minimaler Erfolg fuer den aktuellen Lane-B-Block:

- `frawo-tech.de` und `www.frawo-tech.de` haben gueltiges HTTPS
- kein Adminpfad ist oeffentlich
- die Seite darf inhaltlich noch provisorisch sein

## Explicit Non-Goals

- kein Public-Cutover fuer `toolbox`
- kein Public-Cutover fuer Odoo-Admin
- kein Mitziehen von PBS, Radio-Backend, HA oder Stockenweiler
- keine Token-/Secret-Ablage im Repo

## Security Note

Das Odoo-Master-Passwort und ein etwaiger Cloudflare-Tunnel-Token bleiben operator-held secrets.
Sie gehoeren nicht in Markdown, nicht in Skripte mit Repo-Klartext und nicht in Handover-Dateien.

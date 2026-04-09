# Coolify Delivery Notes

## Rolle

`Coolify` ist in diesem Projekt die bevorzugte Open-Source-CD-Schicht.

Es soll:

- fertige OCI-Artefakte deployen
- Umgebungen `dev` und `prod` trennen
- Rollbacks auf bekannte Tags erlauben
- Deploy- und Health-Checks sichtbar machen

Es soll **nicht**:

- die einzige Wissensquelle fuer Delivery sein
- auf DMZ-Public-Nodes selbst entwickelt oder administriert werden
- die CI-Logik ersetzen

## Platzierung

- `Coolify` selbst gehoert auf einen internen Management-Pfad
- nicht direkt in die Public-DMZ
- Zugriff nur intern oder ueber `Tailscale`

## Zielserver spaeter

### Dev

- ein interner oder allowlist-geschuetzter Dev-Webnode
- nicht voll public offen

### Prod

- `Anker / Rothkreuz` Public-Webnode in `VLAN 102`
- `Stockenweiler` Public-Webnode als spaeterer zweiter Zielknoten

## Empfohlenes Betriebsmodell

### Build

- CI baut Images
- Registry speichert Images
- Coolify deployed nur Tags/Images

### Dev Flow

- Quelle: `develop`
- Deploy automatisch nach `dev`
- Smoke Tests direkt danach

### Prod Flow

- Quelle: `main` oder Release-Tag
- Deploy aus immutable Release-Tag
- zuerst `primary`, dann `secondary`

## App-Gruppen

### Coolify-geeignet als erste Welle

- stateless public web apps
- kleine public frontends
- player-/landing-/campaign-sites

### Nicht erste Welle

- `Odoo`
- `Nextcloud`
- `Paperless`
- `Vaultwarden`
- `Home Assistant`

Diese Dienste bleiben zuerst ausserhalb der dualen DMZ-Delivery-Fabrik.

## Spaetere Checkliste

- `Coolify` intern deployen
- OCI-Registry festlegen
- Server in Coolify anlegen
- `dev`-Projekt anlegen
- `prod`-Projekt anlegen
- Health Checks je App definieren
- Rollback auf letzten Tag pruefen


## Repo-seitiger v1-Contract

Der erste Referenzdienst fuer den spaeteren Coolify-Pfad ist jetzt:

- App: `radio-player-frontend`
- Image: `ghcr.io/wolfeetech/frawo/radio-player-frontend`
- Env-Vorlagen:
  - `apps/radio-player-frontend/env/dev.env.example`
  - `apps/radio-player-frontend/env/prod.env.example`
- spaetere Webhook-Secrets:
  - `COOLIFY_DEV_WEBHOOK_RADIO_PLAYER_FRONTEND`
  - `COOLIFY_PROD_PRIMARY_WEBHOOK_RADIO_PLAYER_FRONTEND`
  - `COOLIFY_PROD_SECONDARY_WEBHOOK_RADIO_PLAYER_FRONTEND`

- Host selection contract: `deployment/coolify/COOLIFY_HOST_SELECTION.md`

- Node spec: `deployment/coolify/COOLIFY_MANAGEMENT_NODE_SPEC.md`

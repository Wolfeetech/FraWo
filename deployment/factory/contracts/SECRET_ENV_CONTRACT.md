# Secret And Env Contract

## Grundsatz

- keine Klartext-Secrets im Repo
- `dev` und `prod` haben getrennte Runtime-Variablen
- `Coolify` oder ein anderer Controller bekommt spaeter nur die gleichen Schluessel, nicht eigene Sonderlogik

## Radio Player Frontend

### Public Env Keys

- `APP_TITLE`
- `APP_TAGLINE`
- `STREAM_URL`
- `STATUS_URL`
- `SUPPORT_URL`

Diese Variablen sind keine Hochrisiko-Secrets, aber sie gehoeren trotzdem in eine saubere Umgebungsdefinition und nicht hart in mehrere Deploypfade.

### Dev Contract

- Datei-Vorlage: `apps/radio-player-frontend/env/dev.env.example`
- Ziel: interne oder allowlist-geschuetzte Dev-Umgebung

### Prod Contract

- Datei-Vorlage: `apps/radio-player-frontend/env/prod.env.example`
- Ziel: spaeterer DMZ-Deploy

## Spaetere Controller-Secrets

Noch nicht live, aber v1-Namensschema steht:

- `COOLIFY_DEV_WEBHOOK_RADIO_PLAYER_FRONTEND`
- `COOLIFY_PROD_PRIMARY_WEBHOOK_RADIO_PLAYER_FRONTEND`
- `COOLIFY_PROD_SECONDARY_WEBHOOK_RADIO_PLAYER_FRONTEND`

## Business-Apps

Fuer `Odoo`, `Nextcloud`, `Paperless`, `Vaultwarden` wird **kein** allgemeiner Factory-Secret-Pfad voreilig vereinheitlicht.

Diese Dienste bleiben vorerst im Modell:

- `primary + restore/DR`
- app-spezifische Secrets
- kein dualer DMZ-Deploy

# Radio Player Frontend Delivery Bundle

## Rolle

Erster echter stateless Referenzdienst fuer die Delivery Factory.

Ziel:

- OCI-buildbar
- GHCR-packagbar
- spaeter ueber `Coolify` oder `docker compose` deploybar

## Dateien

- `compose.yaml`
- `compose.dev.env.example`
- `compose.prod.env.example`
- `apps/radio-player-frontend/env/dev.env.example`
- `apps/radio-player-frontend/env/prod.env.example`

## Deploy-Konzept

- Image-Quelle spaeter bevorzugt: `ghcr.io/wolfeetech/frawo/radio-player-frontend`
- lokaler Smoke-Pfad darf `IMAGE_REF=radio-player-frontend:test` nutzen
- Health-Pfad: `/healthz`
- v1 bleibt intern/preview bis ein echter Dev-Node feststeht

## Nicht Teil von v1

- kein Live-Coolify-Deploy
- kein Public-DNS-Cutover
- keine Kopplung an Business-Apps

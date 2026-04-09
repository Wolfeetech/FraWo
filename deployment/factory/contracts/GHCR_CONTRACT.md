# GHCR Contract

## Rolle

`GHCR` ist fuer `v1` die bevorzugte Standard-Registry, weil das Repo bereits auf `GitHub` liegt.

Es ist **nicht** der Public-Edge und **nicht** der Deployment-Controller.

Kette:

- GitHub Repo
- GitHub Actions buildet OCI-Artefakte
- `GHCR` speichert immutable Images
- `Coolify` deployed spaeter nur Tags aus `GHCR`

## Namespace

- Registry: `ghcr.io`
- Owner: `wolfeetech`
- Repo-Scope: `frawo`
- v1-Image-Pfad fuer den ersten Referenzdienst:
  - `ghcr.io/wolfeetech/frawo/radio-player-frontend`

## Tag-Konvention

### Dev

- `dev-latest`
- `sha-<gitsha>`

### Main

- `main-latest`
- `sha-<gitsha>`

### Prod Release

- `v*` Git-Tags werden 1:1 als Release-Tags gespiegelt
- `prod` deployt nur aus Versionstags oder bewusst promoteten immutable Tags

## GitHub Actions Rechte

Fuer GHCR Package Push gilt:

- `contents: read`
- `packages: write`

Der erste Repo-seitige GHCR-Pfad braucht keine zusaetzlichen Klartext-Secrets, solange `GITHUB_TOKEN` im gleichen Repo Packages schreiben darf.

## Nicht Teil von v1

- kein direkter Public-Cutover
- keine Registry-Mirror-Kette
- kein Harbor-Zwang
- keine automatische Prod-Deployment-Kopplung ohne spaeteren Coolify-/Webhook-Pfad

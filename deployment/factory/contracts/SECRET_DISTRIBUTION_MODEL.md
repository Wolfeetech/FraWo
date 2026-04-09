# Secret Distribution Model

## Grundsatz

- Build und Package trennen sich von Runtime-Secrets
- keine Klartext-Secrets im Repo
- `dev` und `prod` sind getrennte Secret-Kontexte

## v1-Modell

### GitHub Actions

- Build/Package fuer `GHCR` nutzt, wo moeglich, `GITHUB_TOKEN`
- spaetere Deploy-Trigger gehen ueber getrennte GitHub Environments:
  - `dev`
  - `prod`

### Coolify Runtime

- Runtime-Variablen leben spaeter pro Environment im Controller
- gleiche Schluessel wie in den Repo-Vertragsdateien
- keine zweite Schatten-Namenslogik

## Erster Referenzdienst

`radio-player-frontend`

- keine Hochrisiko-Secrets
- trotzdem getrennte Env-Sets fuer `dev` und `prod`
- Webhook-Secrets spaeter nur environment-spezifisch

## Business-Apps

`Odoo`, `Nextcloud`, `Paperless`, `Vaultwarden` bleiben ausserhalb eines generischen Factory-Secret-Modells, bis ihre Produktivpfade bewusst in die Delivery-Fabrik uebernommen werden.

# Credential Inventory (Operator)

## Zweck

Dieses Dokument ist das zentrale **Extra-Dokument** fuer Zugangsdaten-Mapping, damit keine Agenten-Generierung ohne Operator-Transparenz bestehen bleibt.

Regel: **Keine Klartext-Passwoerter in Git**. Reale Werte liegen nur im Secret-Manager (Vaultwarden) oder in lokalen, nicht versionierten Dateien.

## Sofortmassnahmen nach diesem Cleanup

Die folgenden Secrets waren zuvor in versionierten Runtime-Dateien vorhanden und sind als kompromittiert zu behandeln:

- `apps/fayanet/.env` (`VW_ADMIN_TOKEN`)
- `apps/yourparty/apps/api/.env.prod` (`MONGO_URI`, `AZURACAST_API_KEY`, `JWT_SECRET_KEY`)
- `apps/yourparty/apps/api/.env.production` (`MONGO_URI`, `MONGO_PASSWORD`, `AZURACAST_API_KEY`)

Aktion:

1. Alle betroffenen Secrets rotieren.
2. Nur rotierte Werte in Vaultwarden speichern.
3. Runtime-Deployments mit den rotierten Werten aktualisieren.

## Credential Register (ohne Klartextwerte)

| Service | Credential Key | Gueltige Quelle | Vaultwarden Eintrag | Status |
|---|---|---|---|---|
| fayanet / vaultwarden | `VW_ADMIN_TOKEN` | lokale `.env` (nicht versioniert) | `FraWo/fayanet/VW_ADMIN_TOKEN` | `ROTATION_REQUIRED` |
| yourparty api | `MONGO_URI` | lokale `.env.production` (nicht versioniert) | `FraWo/yourparty/api/MONGO_URI` | `ROTATION_REQUIRED` |
| yourparty api | `MONGO_PASSWORD` | lokale `.env.production` (nicht versioniert) | `FraWo/yourparty/api/MONGO_PASSWORD` | `ROTATION_REQUIRED` |
| yourparty api | `AZURACAST_API_KEY` | lokale `.env.production` (nicht versioniert) | `FraWo/yourparty/api/AZURACAST_API_KEY` | `ROTATION_REQUIRED` |
| yourparty api | `JWT_SECRET_KEY` | lokale `.env.prod` (nicht versioniert) | `FraWo/yourparty/api/JWT_SECRET_KEY` | `ROTATION_REQUIRED` |

## Lokale Passwortliste (optional, nicht versioniert)

Falls du eine lokale Klartext-Uebersicht brauchst, nutze:

- `OPERATIONS/CREDENTIAL_INVENTORY.local.md`

Diese Datei ist in `.gitignore` eingetragen und darf nicht committed werden.

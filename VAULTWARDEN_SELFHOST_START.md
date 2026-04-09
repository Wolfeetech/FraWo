# Vaultwarden Self-Host Start

## Status

Stand `2026-03-26`:

- `CT 120` `vaultwarden` ist auf `proxmox-anker` live
- Service-IP: `192.168.2.26`
- Produktive Ziel-URL: `https://vault.hs27.internal`
- Bootstrap Web Vault: `http://192.168.2.26:8080`
- Bootstrap Admin Panel: `http://192.168.2.26:8080/admin`
- Healthcheck: `http://192.168.2.26:8080/alive`

Wichtig:

- Das ist eine **self-hosted Bitwarden-kompatible Instanz auf Vaultwarden**
- sie ist aktuell **intern** live
- produktiver Erstlogin ist erst nach internem `HTTPS` freigegeben
- `vault.hs27.internal` ist die einzige produktive Login-URL
- Stand `2026-03-27` zusaetzlich:
  - `Vaultwarden`-SMTP fuer Einladungen ist live
  - `SIGNUPS_ALLOWED=false`
  - `INVITATIONS_ALLOWED=true`
  - `ADMIN_TOKEN` liegt live nur noch als `Argon2id`-Hash vor
- Stand `2026-03-31` zusaetzlich:
  - der HTTP-Bind ist bewusst auf `192.168.2.26:8080` begrenzt
  - direkter `SSH`-Zugang in `CT120` ist bewusst deaktiviert
  - der nachhaltige Reapply-Pfad liegt jetzt in `scripts/apply_vaultwarden_network_baseline.py`

## Was bereits erledigt ist

- dedizierter LXC `CT 120` erstellt
- Debian 12 Basis deployed
- Docker und Compose installiert
- Vaultwarden-Container deployed
- Admin-Token lokal erzeugt und **nicht** ins Repo geschrieben
- Root-Passwort fuer `CT 120` lokal erzeugt und **nicht** ins Repo geschrieben

## Was du jetzt tun musst

1. zuerst `VAULTWARDEN_INTERNAL_HTTPS_ROLLOUT.md` abarbeiten
2. `https://vault.hs27.internal` oeffnen
3. `wolf@frawo-tech.de` als ersten produktiven Benutzer anlegen
4. dabei **dein eigenes Master-Passwort selbst setzen**
5. sofort den Offline-Recovery-Zettel ausfuellen
6. sofort eine zweite getrennte Offline-Kopie des Master-Passwort-Hinweises anlegen
7. danach den Login ueber `HTTPS` pruefen

## Wo die Bootstrap-Secrets liegen

Nur lokal auf dem StudioPC, nicht im Repo:

- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_admin_token.txt`
- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_ct120_root_password.txt`

Diese Dateien sind nur Break-Glass-Bootstrap-Artefakte.
Sie sind nicht der produktive Login, nicht der normale Recovery-Pfad und nicht der Ersatz fuer das Master-Passwort.
- der Klartext-Admin-Token liegt nur lokal in der Bootstrap-Datei; die Live-`.env` auf `CT120` enthaelt nur den gehashten Wert

## Master-Passwort-Regel

Das **Master-Passwort wird nicht in Markdown, nicht im Repo und nicht als Klartext-Datei dokumentiert**.

Professioneller Standard:

- du setzt es selbst beim ersten produktiven Login ueber `HTTPS`
- du schreibst es auf eine Offline-Recovery-Karte
- du lagerst eine zweite Kopie getrennt
- du speicherst es nicht in Nextcloud, Paperless, Odoo oder lokalen Klartextnotizen

Siehe:

- `VAULTWARDEN_RECOVERY_SHEET.md`

## Reihenfolge nach dem Erstlogin

1. Sammlungen anlegen:
   - `Core Infra`
   - `Business Apps`
   - `Media`
   - `Mail & Domains`
   - `Devices`
   - `Stockenweiler`
2. zuerst `STRATO`- und Core-Infra-Zugaenge einpflegen
3. danach App-Zugaenge aus dem extern archivierten Altregister in `Vaultwarden` uebernehmen und nur noch das Referenzregister im Workspace behalten
4. erst dann Klartext-Passwoerter in Markdown abbauen

## Netzwerk- und Rebuild-Standard

- `Vaultwarden` ist intern nur ueber `https://vault.hs27.internal` produktiv
- der Bootstrap-HTTP-Pfad `http://192.168.2.26:8080` bleibt nur interner Technikpfad
- `CT120` soll nicht wieder mit offenem Direkt-`SSH` oder offenem Public-HTTP auftauchen
- der Repo-Standard fuer Rebuild oder Drift-Korrektur ist:
  - `python scripts/apply_vaultwarden_network_baseline.py`
- der Health-Nachweis danach ist:
  - `http://192.168.2.26:8080/alive`
- der aktuelle Public-Re-Audit fuer diesen Host laeuft ueber:
  - `python scripts/public_ipv6_exposure_audit.py`

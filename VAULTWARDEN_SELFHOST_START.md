# Vaultwarden Self-Host Start

## Status

Stand `2026-03-26`:

- `CT 120` `vaultwarden` ist auf `proxmox-anker` live
- Service-IP: `192.168.2.26`
- Web Vault: `http://192.168.2.26:8080`
- Admin Panel: `http://192.168.2.26:8080/admin`
- Healthcheck: `http://192.168.2.26:8080/alive`

Wichtig:

- Das ist eine **self-hosted Bitwarden-kompatible Instanz auf Vaultwarden**
- sie ist aktuell **intern** live
- `vault.hs27.internal` ist noch nicht vor die Toolbox-Frontdoor gezogen

## Was bereits erledigt ist

- dedizierter LXC `CT 120` erstellt
- Debian 12 Basis deployed
- Docker und Compose installiert
- Vaultwarden-Container deployed
- Admin-Token lokal erzeugt und **nicht** ins Repo geschrieben
- Root-Passwort fuer `CT 120` lokal erzeugt und **nicht** ins Repo geschrieben

## Was du jetzt tun musst

1. `http://192.168.2.26:8080` oeffnen
2. den ersten Benutzer anlegen
3. dabei **dein eigenes Master-Passwort selbst setzen**
4. danach im Admin-Bereich pruefen, ob die Instanz sauber antwortet

## Wo die Bootstrap-Secrets liegen

Nur lokal auf dem StudioPC, nicht im Repo:

- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_admin_token.txt`
- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_ct120_root_password.txt`

Diese Dateien sind nur Bootstrap-Artefakte.
Sie muessen spaeter in den sauberen Recovery-Prozess ueberfuehrt werden.

## Master-Passwort-Regel

Das **Master-Passwort wird nicht in Markdown, nicht im Repo und nicht als Klartext-Datei dokumentiert**.

Professioneller Standard:

- du setzt es selbst beim ersten Login
- du schreibst es auf eine Offline-Recovery-Karte
- du lagerst eine zweite Kopie getrennt

Siehe:

- `VAULTWARDEN_RECOVERY_SHEET.md`

## Naechster technischer Ausbau

1. internen Hostnamen `vault.hs27.internal` vor die Toolbox-Frontdoor ziehen
2. produktive Sammlungen anlegen
3. Eintraege aus `ACCESS_REGISTER.md` sauber ueberfuehren
4. danach Klartext-Passwoerter in Markdown abbauen

# Vaultwarden Recovery Sheet

## Zweck

Diese Datei ist die Vorlage fuer den **Offline**-Recovery-Zettel.
Sie ist **keine** Datei fuer echte Klartext-Secrets.

## Eintragen per Hand

- Vault URL:
  - `https://vault.hs27.internal`
- Admin URL:
  - `http://192.168.2.26:8080/admin` nur Break-Glass-Bootstrap
- Hauptnutzer:
  - `wolf@frawo-tech.de`
- Master-Passwort:
  - **handschriftlich eintragen**
- Hinweis auf zweiten Recovery-Ort:
  - **handschriftlich eintragen**

## Nie tun

- Master-Passwort ins Repo schreiben
- Master-Passwort in `ACCESS_REGISTER.md` schreiben
- Master-Passwort als Klartext in Nextcloud, Paperless oder Odoo ablegen

## Bootstrap-Dateien

Nur lokal auf dem StudioPC:

- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_admin_token.txt`
- `C:\Users\StudioPC\AppData\Local\Homeserver2027\bootstrap\vaultwarden_ct120_root_password.txt`

Diese Bootstrap-Dateien sind nur Break-Glass-Bootstrap und nicht der Recovery-Zettel.

## Zielzustand

- Nutzer arbeiten ueber Vaultwarden
- produktiver Login laeuft nur ueber `https://vault.hs27.internal`
- `ACCESS_REGISTER.md` enthaelt nur noch Referenzen
- Master-Passwort existiert nur:
  - im Kopf
  - auf dem Offline-Recovery-Zettel
  - auf einer getrennten zweiten Offline-Kopie

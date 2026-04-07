# Mail Operations

Stand: `2026-03-27`

## Zweck

Diese Datei ist die kanonische Betriebsanweisung fuer Mail, Mailbox-Aufbau und App-SMTP im aktuellen FRAWO-Stand.

## Festgelegter Betriebsstandard

- kein eigener Mailserver auf dem Homeserver in diesem Block
- `STRATO` bleibt Provider fuer Empfang und Versand
- `Vaultwarden / FraWo / Mail & Domains` ist die Secret-Ablage
- `Nextcloud Mail` ist spaeter die zentrale Benutzeroberflaeche
- `Odoo` nutzt Mail nur fuer Prozess- und Systemkontext
- `Paperless` bekommt spaeter eine dedizierte Dokumenten-Mailbox
- keine neuen kostenpflichtigen SaaS-Abhaengigkeiten fuer Mail, Secrets oder App-SMTP

## Interne Mailverwaltung

- Mail-Transport bleibt extern bei `STRATO`
- Mail-Management bleibt intern organisiert:
  - Credentials in `Vaultwarden`
  - App-SMTP ueber den zentralen `noreply`-Standard
  - spaetere Benutzeroberflaeche ueber `Nextcloud Mail`
- `Odoo`, `Paperless`, `AzuraCast` und `Vaultwarden` sind SMTP-Clients, keine eigenen Mailserver
- fuer diesen Block wird bewusst kein eigener Mailserver auf dem Homeserver aufgebaut
- falls `agent@frawo-tech.de` spaeter als echte Mailbox aktiviert wird, dient sie nur als Automations-Inbox fuer Odoo/n8n und nicht als persoenlicher Kommunikationskanal

## Zertifizierungsstandard

Fuer das erste professionelle interne Produktionssiegel gilt:

- `STRATO` bleibt fuer V1 akzeptierter externer Provider
- App-SMTP ist nicht mehr spaeter oder optional, sondern Teil des V1-Zertifizierungsscope
- Zielabsender fuer Apps ist `noreply@frawo-tech.de`
- reale Funktion zaehlt erst bei sichtbarem Testversand und Testempfang

## Aktive Zieladressen

### Personen

- `wolf@frawo-tech.de`
- `franz@frawo-tech.de`

### Funktionen

- `info@frawo-tech.de`
- `noreply@frawo-tech.de`

### Spaeter

- `documents@frawo-tech.de`
- optional `agent@frawo-tech.de` fuer Odoo-/Workflow-Intake
- optional `frontend@frawo-tech.de`
- optional `admin@frawo-tech.de` als Alias

## Aktueller Uebergangsstand

- `wolf@frawo-tech.de` ist aktuell Alias auf das technische Basis-Postfach `webmaster@...`
- `info@frawo-tech.de` ist aktuell ebenfalls Alias auf das technische Basis-Postfach `webmaster@...`
- `franz@frawo-tech.de` hat bereits ein eigenes echtes Postfach
- `franz@frawo-tech.de` wurde am `2026-03-27` per `IMAP` und `SMTP AUTH` verifiziert
- der aktuelle technische Stand von `info@frawo-tech.de` ist noch gegen das `STRATO`-Paket zu verifizieren
- der aktuelle technische Stand von `noreply@frawo-tech.de` ist noch gegen das `STRATO`-Paket zu verifizieren
- produktiver App-SMTP darf auf ein technisches Basis-Postfach authentifizieren, auch wenn der sichtbare Absender `noreply@frawo-tech.de` ist
- `Vaultwarden`-Invite-Mail ueber `webmaster@frawo-tech.de` ist live
- ein am `2026-03-31` bereitgestellter Passwortkandidat fuer `webmaster@frawo-tech.de` war **nicht** erfolgreich fuer direkten `IMAP`-/`SMTP AUTH`-Login; er darf daher nicht automatisch als echtes Mailbox-Passwort fuer `webmaster` angenommen werden

## STRATO Zugriff

- Kunden-Login: `https://www.strato.de/faq/vertrag/der-strato-kunden-login/`
- Mailboxen anlegen: `https://www.strato.de/faq/mail/e-mail-adressen-einrichten-und-bearbeiten/`
- Webmail: `https://webmail.strato.de/`

Wichtig:

- bei einem `STRATO Domain-Paket` ist `STRATO Webmail` nicht immer der richtige Testpfad
- in diesem Fall direkt ueber Mailclient testen
- IMAP: `imap.strato.de`
- POP3: `pop3.strato.de`
- SMTP: `smtp.strato.de`
- Login immer mit dem echten Postfach, nicht mit einem Alias
- Beispiel fuer den aktuellen FRAWO-Fall:
  - sichtbarer Absender: `noreply@frawo-tech.de`
  - SMTP-Login: technisches Basis-Postfach `webmaster@frawo-tech.de`
  - Passwort: Passwort von `webmaster@frawo-tech.de`

## Mailclient Standard

- Mailclients authentifizieren immer mit dem echten Postfach, nicht mit Aliasen
- technischer Basis-Login fuer den Owner-Pfad ist aktuell `webmaster@frawo-tech.de`
- `franz@frawo-tech.de` bleibt ein getrenntes echtes Postfach
- `franz@frawo-tech.de` wurde am `2026-03-27` erfolgreich gegen `imap.strato.de:993` und `smtp.strato.de:587` authentifiziert
- bevorzugte Client-Werte:
  - Eingangsserver: `imap.strato.de`
  - Port eingehend: `993`
  - Verschluesselung eingehend: `SSL/TLS`
  - Ausgangsserver: `smtp.strato.de`
  - Port ausgehend: `587`
  - Verschluesselung ausgehend: `STARTTLS`
  - Fallback nur falls notwendig: `465` mit `SSL/TLS`
  - Benutzername eingehend und ausgehend: immer das echte Postfach
- wenn ein Client-Auto-Setup scheitert:
  1. auf `IMAP` wechseln
  2. Serverdaten manuell eintragen
  3. erst danach Versand und Empfang sichtbar testen

## Rollout-Reihenfolge

1. `frawo-tech.de` im STRATO-Paket pruefen
2. Alias-/Postfachmodell fuer `wolf`, `franz`, `info`, `noreply` im `STRATO`-Paket verifizieren und bereinigen
3. Zugangsdaten sofort in `Vaultwarden / FraWo / Mail & Domains` speichern
4. Testversand und Testempfang je Mailbox pruefen
5. `noreply@frawo-tech.de` als SMTP-Absender fuer Apps standardisieren
6. sichtbare App-SMTP-Testmails fuer `Nextcloud`, `Paperless`, `Odoo`, `AzuraCast` pruefen
7. SPF, DKIM und DMARC dokumentieren
8. `Nextcloud Mail` fuer Benutzer vorbereiten

## Professionelle Entscheidung Fuer Franz

`franz@frawo-tech.de` bleibt ein echtes eigenes Postfach.

Nicht akzeptabel:

- Alias auf `webmaster@...`, wenn Franz technisch mit `webmaster` arbeiten wuerde

Saubere Wege:

1. `franz@frawo-tech.de` als eigenes echtes Postfach beibehalten
2. `wolf@frawo-tech.de` bewusst als sichtbare Alias-Identitaet ueber `webmaster@...` dokumentieren und pruefen
3. `info@frawo-tech.de` bewusst als Funktionsalias ueber `webmaster@...` dokumentieren und pruefen

## Sofortregeln Pro Mailbox

- Passwort setzen
- sofort in `Vaultwarden` speichern
- echten Login von Aliasen trennen
- Versand und Empfang extern testen

## App-SMTP Standard

| App | Absender | Zweck | Status |
| --- | --- | --- | --- |
| Nextcloud | `noreply@frawo-tech.de` | Freigaben, Hinweise, Passwortflows | pending |
| Paperless | `noreply@frawo-tech.de` | Benachrichtigungen | pending |
| Odoo | `noreply@frawo-tech.de` | Prozess- und Systemmail | pending |
| AzuraCast | `noreply@frawo-tech.de` | System- und Admin-Hinweise | pending |
| Website / Kontakt | `info@frawo-tech.de` | Inbound / Kontaktformular | pending |
| Paperless Inbound | `documents@frawo-tech.de` | Dokumente per IMAP importieren | later |

## Aktueller Deploy-Stand

- `Vaultwarden` SMTP ist live und fuer Einladungen verifiziert
- `Paperless` SMTP ist konfiguriert und im Baseline-Check gruen
- `Odoo` SMTP ist konfiguriert und im Baseline-Check gruen
- `Nextcloud` SMTP ist geschrieben und im Baseline-Check gruen
- `AzuraCast` SMTP ist noch offen, weil der SSH-Zugang zum `raspberry_pi_radio` aktuell der Restblocker ist
- `Nextcloud` nutzt live `mail_from_address=noreply`, `mail_domain=frawo-tech.de`, `smtp.strato.de:587`, Login `webmaster@frawo-tech.de`
- `Paperless` nutzt live `PAPERLESS_EMAIL_FROM=noreply@frawo-tech.de`, `smtp.strato.de:587`, Login `webmaster@frawo-tech.de`
- `Odoo`-Mailserver `Strato SMPT` ist live auf `smtp.strato.de` mit Login `webmaster@frawo-tech.de` und `from_filter=noreply@frawo-tech.de` ausgerichtet
- `noreply@frawo-tech.de` wurde am `2026-03-30` als echter sichtbarer SMTP-Absender ueber den produktiven STRATO-Backbone an `franz@frawo-tech.de` gesendet
- der sichtbare Inbox-Nachweis bei `Franz` ist am `2026-03-31` read-only per IMAP erbracht worden:
  - `franz@frawo-tech.de` INBOX enthaelt den Betreff `HS27 noreply SMTP proof 2026-03-30 23:37`
  - letzter Header-Nachweis: `From=noreply@frawo-tech.de`, `Date=Mon, 30 Mar 2026 23:42:14 +0200 (CEST)`
- `strato_mail_model_verified` ist damit im aktuellen MVP-Gate auf `passed`
- fuer den read-only Inbox-Nachweis liegt jetzt ein lokaler Helper bereit:
  - `python scripts/check_strato_inbox_for_subject.py --username franz@frawo-tech.de --subject "HS27 noreply SMTP proof 2026-03-30 23:37"`
  - benoetigt nur die Laufzeitvariable `HS27_MAILBOX_PASSWORD`
- fuer den echten Ein-Schritt-Abschluss des MVP-Mail-Restpunkts liegt jetzt zusaetzlich ein Windows-Helfer bereit:
  - `powershell -ExecutionPolicy Bypass -File .\scripts\prove_strato_mail_model.ps1`
  - fragt das Franz-Mailbox-Passwort sicher ab
  - prueft den Inbox-Nachweis read-only
  - setzt `strato_mail_model_verified` bei Erfolg auf `passed`
  - zieht danach den `release_mvp_gate` neu

## Vaultwarden Invite Mail

- `Vaultwarden` nutzt fuer Einladungen denselben `STRATO`-SMTP-Backbone
- produktive Basis:
  - `DOMAIN=https://vault.hs27.internal`
  - `SIGNUPS_ALLOWED=false`
  - `INVITATIONS_ALLOWED=true`
  - sichtbarer Absender: `noreply@frawo-tech.de`
  - SMTP-Login: `webmaster@frawo-tech.de`
- technischer Deploypfad:
  - `make vaultwarden-smtp-deploy`
  - `make vaultwarden-smtp-check`
- erster produktiver Mailtest fuer diesen Pfad ist die Einladung von `franz@frawo-tech.de` in die Organisation `FraWo`
- der SMTP-Pfad fuer `Vaultwarden` ist am `2026-03-27` live auf `CT120` aktiviert worden
- der Einladungsversand an `franz@frawo-tech.de` war erfolgreich und die Mail ist angekommen

## Runtime-Deploy-Standard

- produktive SMTP-Credentials werden nicht in `main.yml`, nicht in Markdown und nicht in git eingecheckt
- lokale Runtime-Overrides liegen nur auf dem vertrauenswuerdigen Admin-System:
  - Vorlage: `..\ansible\inventory\group_vars\all\mail_runtime.local.yml.example`
  - echte lokale Datei: `..\ansible\inventory\group_vars\all\mail_runtime.local.yml`
- bevorzugter Passwortpfad fuer den Deploy ist die Laufzeitvariable:
  - PowerShell: `$env:HOMESERVER_MAIL_SMTP_PASSWORD='...'`
- Windows-Ein-Schritt-Helfer:
  - `.\scripts\run_app_smtp_deploy.ps1`
- der SMTP-Authentifizierungsname in `mail_runtime.local.yml` muss das echte sendeberechtigte Postfach sein, nicht zwingend der sichtbare From-Absender
- fuer den produktiven Rollout gilt:
  1. lokale Runtime-Datei mit `homeserver_mail_app_smtp_enabled: true` und SMTP-Username bereitstellen
  2. Passwort nur zur Laufzeit setzen
  3. `make app-smtp-deploy`
  4. `make app-smtp-check`
  5. sichtbare Testmails fuer `Nextcloud`, `Paperless`, `Odoo`, `AzuraCast`

Alternativ unter Windows:

1. `.\scripts\run_app_smtp_deploy.ps1`
2. Passwort interaktiv eingeben
3. Deploy und Check laufen in einem Zug

Fuer den read-only Empfangsnachweis einer bereits gesendeten Testmail:

1. `$env:HS27_MAILBOX_PASSWORD='...'`
2. `python scripts/check_strato_inbox_for_subject.py --username franz@frawo-tech.de --subject "HS27 noreply SMTP proof 2026-03-30 23:37"`
3. bei `inbox_proof=yes` die manuelle Gate-Evidenz aktualisieren

Unter Windows geht derselbe Pfad jetzt in einem Schritt:

1. `powershell -ExecutionPolicy Bypass -File .\scripts\prove_strato_mail_model.ps1`
2. Passwort sicher eingeben
3. bei Erfolg wird die Gate-Evidenz direkt aktualisiert und der MVP-Gate neu geschrieben

Nicht akzeptabel:

- SMTP-Passwoerter in irgendeinem Klartext-Register oder Markdown-Dokument im Workspace
- SMTP-Passwoerter in `README.md`, Runbooks oder Commit-Historie
- produktive App-SMTP-Credentials dauerhaft als Klartext im Repo

## Systemrollen

| System | Rolle |
| --- | --- |
| `STRATO` | Provider fuer Empfang und Versand |
| `Vaultwarden` | Secret-Ablage fuer Mail- und App-Credentials |
| `Nextcloud Mail` | spaetere zentrale Benutzeroberflaeche |
| `Odoo` | Workflow-, Alias- und Systemmail |
| `Paperless` | spaeter dedizierter IMAP-Dokumenteneingang |

## Definition Of Done

- `wolf@frawo-tech.de` ist als Alias auf das technische Basis-Postfach sauber dokumentiert und getestet
- `franz@frawo-tech.de` ist als echtes Postfach nutzbar
- `info@frawo-tech.de` und `noreply@frawo-tech.de` sind technisch klar definiert
- alle produktiven Mailzugriffe liegen in `Vaultwarden`
- Versand und Empfang sind fuer die Kernpostfaecher getestet
- die SMTP-Basis fuer `Nextcloud`, `Paperless`, `Odoo` und `AzuraCast` ist konfiguriert
- sichtbare App-Testmails sind fuer alle vier Apps erfolgreich
- SPF, DKIM und DMARC sind dokumentiert
- `Nextcloud Mail` und App-SMTP koennen anschliessend ohne neue Grundsatzentscheidung ausgerollt werden

## Was Jetzt Nicht Mehr In Extra Checklisten Gehoert

- Alias-/Postfachmodell fuer `wolf` und `franz`
- `Vaultwarden`-Invite-Mailpfad
- SMTP-Runtime-Deploy-Standard
- sichtbare Mail-Resttests

## Zugeordnete Uebergangsdokumente

- `..\MAIL_SYSTEM_ROLLOUT.md`
- `..\STRATO_MAIL_ACCOUNT_ROLLOUT_CHECKLIST.md`
- `..\STRATO_MAIL_CLIENT_SETUP.md`
- `..\NEXTCLOUD_MAIL_AND_ODOO_MAIL_ARCHITECTURE.md`
- `..\INTERNAL_COMMUNICATION_STANDARD.md`

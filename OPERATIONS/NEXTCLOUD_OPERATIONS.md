# Nextcloud Operations

## Zweck

Nextcloud ist die Benutzerablage, Kollaborationsoberflaeche und der definierte Dokumenteneingang fuer den Paperless-Workflow.
Die Storage-Integrationsregeln dazu stehen in `OPERATIONS/STORAGE_INTEGRATION_OPERATIONS.md`.

## Zugriff

- intern: `http://cloud.hs27.internal`
- direkt: `http://192.168.2.21`

## Aktueller Betriebsstand

- `wolf` und `franz` sind die normalen Benutzerpfade
- `frontend` bleibt ein bewusst eingeschraenkter Shared-Pfad
- `Paperless/Eingang` bleibt der kanonische Scan- und Upload-Zielordner
- SMTP ist geschrieben und der Baseline-Check ist gruen
- sichtbare Testmail steht noch aus
- `Nextcloud Mail` laeuft auf `Nextcloud 33.0.2` mit Mail-App `5.7.5`
- der Shared-Posteingang `webmaster@frawo-tech.de` wird fuer Alias-Adressen nicht mehr als flache Sammel-INBOX belassen:
  - `Aliases.Agent`
  - `Aliases.Info`
- auf `VM 200` laeuft dafuer jetzt lokal der leichte Timer `hs27-nextcloud-alias-router.timer`, der neue Alias-Mails aus `INBOX` nach Header-Adressierung in diese Ordner verschiebt
- `wolf@frawo-tech.de` bleibt bewusst in der Haupt-`INBOX`, damit der persoenliche Lesefluss nicht in einen Extra-Ordner zerlegt wird

## Normalbetrieb

- persoenliche Nutzung ueber `wolf` und `franz`
- keine Admin-Konten fuer Alltag
- Uploads zuerst in Nextcloud, danach kontrolliert weiter in Paperless
- Medien oder fremde App-Daten nur ueber klar definierte External-Storage- oder Export-Pfade sichtbar machen
- Shared-Mailboxen nur mit klarer Trennung nutzen:
  - `webmaster@...` bleibt der technische Basispfad
  - Alias-Mails fuer `agent@` und `info@` sollen in Nextcloud Mail ueber die zugehoerigen Alias-Ordner gelesen werden
  - `wolf@` bleibt in `INBOX`

## Taegliche Checks

- Login funktioniert
- Upload und Download funktionieren
- `Paperless/Eingang` ist nutzbar
- Freigaben und Grundfunktionen laufen sauber
- SMTP- und Systemmails nur ueber den definierten Mailpfad
- `Nextcloud Mail`: `wolf@` bleibt in `INBOX`, `agent@` und `info@` landen in `Aliases.*`

## Bekannte Restpunkte

- sichtbare Testmail aus Nextcloud
- `frontend` nur fuer klar definierte Shared-Flows nutzen
- `Odoo`-Intake auf dem Shared-Postfach `webmaster@...` bleibt eine getrennte Betriebsentscheidung und ist nicht identisch mit der Nextcloud-Mail-Trennung
- `Odoo`-Anhaenge sollen spaeter nicht ueber einen gemeinsamen Live-Filestore, sondern ueber einen kontrollierten Export-/Mirror-Pfad in Nextcloud sichtbar werden
- der zentrale Medienpfad kann spaeter read-only ueber `Nextcloud External Storage` sichtbar gemacht werden; das ist nicht dasselbe wie ein Umzug des Nextcloud-Datadirs

## Nie Tun

- kein Shared-Admin als Alltagskonto
- keine wilden Speicherpfad- oder Datenverzeichnis-Experimente im Live-Betrieb
- keinen alternativen Dokumenteneingang ausserhalb des definierten Nextcloud-Pfads erfinden
- keine doppelten IMAP-Konten pro Alias in Nextcloud Mail anlegen, wenn sie alle auf dieselbe Shared-Mailbox zeigen; das erzeugt nur Dubletten statt Trennung
- keine fremden App-Datadirs wie Odoo-Filestore oder Paperless-Media direkt in Nextcloud als beschreibbare Live-Pfade einhaengen

## Eskalation

- bei Dokumentenproblemen zuerst Login, Upload und `Paperless/Eingang` pruefen
- danach erst Bridge oder Paperless selbst untersuchen

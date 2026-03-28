# Vaultwarden Operations

## Zweck

Vaultwarden auf `CT120` ist das produktive Secret-Home fuer den Betriebsstandard.

## Organisationsstandard

- Organisation: `FraWo`
- Mitglieder:
  - `wolf@frawo-tech.de` als erster Owner und DevOps-/Betriebsverantwortlicher
  - `franz@frawo-tech.de` als zweiter produktiver Benutzer
- Collections:
  - `Core Infra`
  - `Business Apps`
  - `Media`
  - `Mail & Domains`
  - `Devices`
  - `Stockenweiler`
- Standortkontexte:
  - `Anker` = Basisserver und privates Kernnetz
  - `Villa` = Studio-/Radio-Kontext
  - `Stockenweiler` = externer Support-Standort
- Aktueller Default fuer bestehende Homeserver-Logins ist `Anker`, solange kein expliziter Standort-Override gepflegt ist.

## Zugriff

- produktive Login-URL: `https://vault.hs27.internal`
- technischer Bootstrap-Endpunkt: `http://192.168.2.26:8080`
- Healthcheck: `http://192.168.2.26:8080/alive`

## Normalbetrieb

- produktive Logins nur noch in Vaultwarden pflegen
- produktive Nutzung erst nach internem `HTTPS`
- erster produktiver Benutzer ist `wolf@frawo-tech.de`
- Collections sauber trennen:
  - `Core Infra`
  - `Business Apps`
  - `Media`
  - `Mail & Domains`
  - `Devices`
  - `Stockenweiler`

## T?gliche Checks

- Wolf und Franz kommen an die relevanten Eintraege
- neue produktive Passwoerter landen zuerst in Vaultwarden
- Arbeitsdokumente werden nicht zur Dauer-Secret-Quelle

## Automatisierter Import aus ACCESS_REGISTER

- Der sichere Importpfad ist ein lokaler CSV-Export ausserhalb des Repos.
- Organisationsmodell und Standortregeln liegen in:
  - `manifests/vaultwarden/organization_model.json`
- Exportbefehl:
  - `python scripts/export_access_register_to_vaultwarden_csv.py`
- Nur pruefen, ohne Datei zu schreiben:
  - `python scripts/export_access_register_to_vaultwarden_csv.py --dry-run`
- Collection-spezifische CSVs fuer die `FraWo`-Organisation erzeugen:
  - `python scripts/export_access_register_to_vaultwarden_csv.py --split-by-collection`
- Nur einen Standortkontext exportieren:
  - `python scripts/export_access_register_to_vaultwarden_csv.py --site Anker --split-by-collection`
  - `python scripts/export_access_register_to_vaultwarden_csv.py --site Villa --split-by-collection`
  - `python scripts/export_access_register_to_vaultwarden_csv.py --site Stockenweiler --split-by-collection`
- Der Export schreibt standardmaessig nach:
  - `%LOCALAPPDATA%\Homeserver2027\vaultwarden_imports\...`
- Danach den CSV-Import in die passende `FraWo`-Collection ausfuehren und die lokale CSV wieder loeschen.
- Die Exportdatei gehoert nie ins Repo, nie nach Nextcloud und nie als Dauerablage in den Workspace.

## Nach dem Import

- Erwarteter Basisstand nach dem aktuellen Import:
  - `17` Eintraege
  - `1` zusammengefuehrtes Duplikat
  - `Business Apps`: `10`
  - `Core Infra`: `2`
  - `Media`: `5`
- Passwortfreien Referenzstand erzeugen:
  - `python scripts/build_vaultwarden_reference_register.py`
- Ergebnisdatei:
  - `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Diese Datei ist fuer Audit und Betrieb gedacht, nicht fuer Secret-Ablage.
- Erst nach sichtbarer Verifikation im Tresor duerfen lokale Klartext-CSV-Dateien und das alte externe Klartext-Register endgueltig aus dem aktiven Arbeitsfluss verschwinden.
- Wenn mit einem aelteren CSV-Export importiert wurde, `AdGuard Admin` auf die korrekte URI `http://127.0.0.1:3000` pruefen.

## Nie tun

- keine neuen produktiven Secrets nur in Markdown halten
- kein produktiver Login ueber den nackten HTTP-Bootstrap-Pfad
- Master-Passwort nie im Repo oder in Arbeitsdateien dokumentieren

## Eskalation

- wenn Vaultwarden noch nicht produktiv befuellt ist, bleibt ein externes Klartext-Archiv nur ein Uebergangsartefakt, kein finaler Standard

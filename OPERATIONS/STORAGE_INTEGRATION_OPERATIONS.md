# Storage Integration Operations

## Zweck

Diese Datei beschreibt den sichere Zielpfad fuer gemeinsame Daten zwischen `Nextcloud`, `Paperless`, `Odoo` und dem zentralen Medien-/Storage-Pfad.

## Verifizierter Ist-Stand

- `Nextcloud` laeuft getrennt auf `VM 200` mit eigenen Docker-Volumes:
  - `nextcloud:/var/www/html`
  - `db:/var/lib/mysql`
- `Odoo` laeuft getrennt auf `VM 220` mit eigenen Docker-Volumes:
  - `odoo-data:/var/lib/odoo`
  - `db-data:/var/lib/postgresql/data`
- `Paperless` laeuft getrennt auf `VM 230` mit eigenen Docker-Volumes:
  - `data:/usr/src/paperless/data`
  - `media:/usr/src/paperless/media`
  - `export:/usr/src/paperless/export`
  - `consume:/usr/src/paperless/consume`
  - `pgdata:/var/lib/postgresql/data`
- Zwischen `Nextcloud` und `Paperless` existiert bereits ein kontrollierter Brueckenpfad:
  - `Nextcloud/Paperless/Eingang` -> `Paperless consume`
  - `Paperless archive` -> `Nextcloud/Paperless/Archiv`
- Der zentrale Medienpfad ist aktuell hostseitig verifiziert:
  - `/mnt/hs27-media/yourparty_Libary`
  - Quelle: `//10.1.0.30/Media`
- `Nextcloud` hat die App-Basis fuer External Storage sichtbar an Bord:
  - `files_external` ist vorhanden
- Der direkte Read-only-Probeweg nach `Stockenweiler` war von diesem Arbeitsplatz aus heute nicht stabil genug fuer eine belastbare Live-Importentscheidung.

## Architekturregel

- `Nextcloud`, `Paperless` und `Odoo` teilen **nicht** denselben Live-App-Storage.
- Gemeinsame Nutzung passiert nur ueber klar definierte Austausch- oder Read-only-Pfade.
- Datenbank-Volumes, App-Datadirs und Odoo-Filestore bleiben app-exklusiv.

## Was gemeinsam sein darf

- `Nextcloud <-> Paperless`:
  - kontrollierter Dokumentenfluss ueber den bestehenden Bridge-Pfad
  - spaeter optional zusaetzlich ein gemeinsamer dokumentierter Source-of-Truth-Pfad auf dem `storage-node`
- `Media -> Nextcloud`:
  - als `Nextcloud External Storage` oder sauberer Read-only-Mount
  - nicht als Teil des Nextcloud-Primärdatadirs
- `Odoo -> Nextcloud`:
  - nur als kontrollierter Export-/Mirror-Pfad fuer Anhange oder definierte Dokumente
  - nicht als gemeinsam beschriebener Live-Filestore

## Was ausdruecklich nicht getan wird

- kein gemeinsamer beschreibbarer Storage fuer `Nextcloud`, `Paperless` und `Odoo`
- kein Mount des Odoo-Filestores direkt in `Nextcloud`
- kein Mount des Paperless-Media-Pfads direkt in `Nextcloud`
- keine direkte Nutzung der Nextcloud-Datenbank oder des Nextcloud-Datadirs durch andere Apps
- keine ungepruefte Live-Einbindung einer `Stockenweiler`-Quelle, solange Quelle, Read-only-Posture und Rueckweg nicht verifiziert sind

## Zielbild

### Dokumente

- `Nextcloud` bleibt die Benutzeroberflaeche fuer manuelle Dateiablage und Upload
- `Paperless` bleibt das OCR-/Archivsystem
- `Odoo` bleibt System of Record fuer Geschaeftsvorgaenge und Anhangsmetadaten
- Wenn Odoo-Dokumente in `Nextcloud` sichtbar sein sollen:
  - Export nach `Nextcloud/Odoo/Attachments/...`
  - nur einseitig oder idempotent gespiegelt
  - klare Ordnerstruktur nach Modell, Kunde oder Vorgang

### Medien

- `storage-node` bleibt die zentrale Source of Truth fuer Musik und Medien
- `Nextcloud` zeigt Medien nur ueber `External Storage` oder einen klar dokumentierten Read-only-Pfad
- `Jellyfin` und `AzuraCast` bleiben direkte Medienverbraucher des zentralen Medienpfads

## Sofortpfad fuer heute

1. `Odoo`-Filestore nicht anfassen und nicht mit `Nextcloud` verheiraten.
2. `Paperless`-Bridge so lassen wie sie ist; sie ist der sichere Dokumentenpfad.
3. Den zentralen Medienpfad `yourparty_Libary` in `Nextcloud` nur read-only sichtbar machen.
4. `Stockenweiler`-Musik erst dann einbinden, wenn die Quelle read-only verifiziert und in den zentralen Medienpfad ueberfuehrt oder sauber referenziert ist.

## Wolf.EE Importstand 2026-04-09

- `Wolf.EE` wurde fuer Sichtpruefung read-only unter `/mnt/wolf-ee` auf `proxmox-anker` gemountet.
- Erster kontrollierter Import in den zentralen Review-Pfad ist erfolgt:
  - Ziel: `/mnt/data/media/yourparty_Libary/incoming/Wolf_EE_20260409`
  - uebernommen: `Job Jobse`, `The_TraXx`, `Sets`, `MUSIK`
  - Umfang: ca. `14G`
- Wichtige Betriebsfolge:
  - `storage-node` steht danach bei ca. `91%`
  - deshalb in diesem Block keine weiteren grossen Medienimporte mehr, bis Review/Weiterverteilung oder Entlastung erfolgt
- Nicht importierte `Wolf.EE`-Bereiche bleiben vorerst nur Sichtungsquelle:
  - `Nicotine`
  - `von HDD`
  - `Plugins`
  - `StudioOne`
  - offensichtlicher Nicht-Medienballast
- Die grosse Zusatz-SSD `music_ssd` ist aktuell **kein** Entlastungspfad:
  - Mount: `/mnt/music_ssd`
  - Device: `/dev/sdb1`
  - Filesystem: `exfat`
  - Status: vom Kernel wegen Dateisystemfehler read-only gesetzt
  - Nachweis: `exFAT-fs (sdb1) ... Filesystem has been set read-only`
  - Reparaturlauf `2026-04-09` hat die Platte kurzfristig wieder auf `rw` gebracht, sie ist unter Schreiblast aber erneut auf `ro` gekippt
  - Folge: aktuell kein verlaesslicher Schreibpfad fuer Review- oder Auslagerungsdaten

## Naechster technische Ausbau

1. `Nextcloud External Storage` fuer den zentralen Medienpfad vorbereiten.
2. Entscheiden, ob die Sichtbarkeit nur fuer `wolf` oder fuer mehrere Benutzer gelten soll.
3. Danach einen getrennten Odoo-Exportpfad definieren:
   - z. B. `Odoo/Invoices`
   - `Odoo/Projects`
   - `Odoo/CRM`
4. Erst danach einen Exporter oder Mirror fuer Odoo-Anhaenge bauen.

## Hardening-Restpunkte

- Odoo verwendet noch Runtime-Konfiguration, die konsequent in den Secret-/Vault-Pfad gezogen werden sollte.
- Der `Stockenweiler`-Quellpfad fuer eine moegliche Musikuebernahme ist heute nicht als live-verifiziert gruen anzusehen.
- `Stockenweiler` ist nicht pauschal "offline", aber der fuer Medienimporte noetige LAN-Pfad fehlt aktuell:
  - Tailscale-Peer `stockenweiler-pve` antwortet
  - seit `2026-04-09` nimmt `toolbox` Routen an (`tailscale set --accept-routes=true`)
  - `ping 192.168.178.25` von `CT 100 toolbox` ist danach gruen
  - damit ist `Stockenweiler` wieder als read-only Quellpfad inventarisierbar
- Die Storage-Optimierung ist aktuell nicht durch Rohkapazitaet der USB-Geraete blockiert, sondern durch:
  - `storage-node` bei ca. `91%`
  - `music_ssd` als unter Last instabiler exFAT-Pfad
  - fehlenden belastbaren Offload-Pfad fuer reine Review-Importe

## Stockenweiler Snapshot 2026-04-09

- Host `stockenweiler-pve` ist ueber Tailscale und den LAN-Pfad wieder sichtbar.
- Relevante verifizierte Bestandszahlen:
  - `/mnt/music_hdd/yourparty_Libary` ca. `283G`
  - `/mnt/data_family` ca. `830G` belegt, rund `102G` frei
  - `/mnt/music_hdd` selbst steht praktisch voll (`ca. 13G frei`)
- Wichtige Folgerung:
  - `Stockenweiler` ist jetzt gute Sichtungs-/Migrationsquelle
  - aber kein grosszuegiger Zielpfad auf `music_hdd`; wenn Offload dorthin, dann eher nach `data_family` und nur bewusst

## Cleanup-Reihenfolge 2026-04-09

- Der `storage-node`-Reviewbereich ist jetzt klar priorisiert:
  - `studiopc-import-2026-03-25` ist fast vollstaendig Recording-/Cache-Ballast und damit zuerst fachlich zu entscheiden
  - `Wolf_EE_20260409` ist strukturierter Reviewbestand und fuer spaetere kuratierte Uebernahme besser geeignet
- Konkrete Grobstruktur:
  - `studiopc-import-2026-03-25`
    - `studio-one-cache-audio` ca. `2.5G`
    - `onedrive-mixxx-recordings` ca. `1.5G`
    - `mixxx-recordings` ca. `258M`
    - `studio-one-media` ca. `157M`
  - `Wolf_EE_20260409`
    - `MUSIK` ca. `6.5G`
    - `Sets` ca. `3.7G`
    - `The_TraXx` ca. `2.7G`
    - `Job Jobse` ca. `438M`
- Praktische Reihenfolge:
  1. `studiopc-import-2026-03-25` als Review-/Archivfrage klaeren
  2. danach `Wolf_EE_20260409` in kleinen kuratierten Paketen weiterverteilen
  3. `Stockenweiler` erst dann in grossen Bloecken ziehen, wenn wieder ein wirklich belastbarer Offload-/Sortierpfad existiert

## Eskalation

- Bei Storage-Fragen immer zuerst unterscheiden:
  - `App-Storage`
  - `Austauschpfad`
  - `zentrale Read-only-Datenquelle`
- Wenn eine Aenderung zwei dieser Ebenen gleichzeitig beruehrt, erst dokumentieren und dann ausrollen.

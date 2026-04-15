# CI/CD Delivery Factory Plan

## Ziel

Eine professionelle Delivery-Fabrik, mit der wir Code mit KI weiterentwickeln, reproduzierbar testen, plattformunabhaengig als OCI-Artefakte bauen und spaeter kontrolliert auf unterschiedliche Zielknoten ausliefern koennen.

Zielbild:

- `build once, deploy anywhere`
- `dev` und `prod` als getrennte Umgebungen
- `Coolify` als Open-Source-CD-Schicht
- zwei spaetere DMZ-Webnodes fuer Public-Workloads:
  - `Rothkreuz / Anker`
  - `Stockenweiler`
- saubere Trennung zwischen:
  - stateless public apps
  - stateful business apps
  - smart-home
  - hobby/media

## Harte Leitentscheidung

`Coolify` ist fuer uns **CD / Delivery**, nicht die eigentliche CI-Wahrheit.

Die professionelle Kette ist:

1. Git-Repo als Source of Truth
2. CI baut und testet OCI-Artefakte
3. Registry speichert immutable Images
4. Coolify deployed genau diese Images auf Zielserver
5. DNS/Health/Rollback entscheiden ueber den Public-Traffic

Damit bleiben wir plattformunabhaengig:

- heute `Coolify`
- spaeter auch `Docker Compose`, `Nomad`, `Kubernetes`, `systemd+compose` oder andere Controller
- weil das eigentliche Lieferobjekt ein OCI-Image plus Runtime-Config bleibt

## Kritisch verifizierter Startstand

Vor jeder weiteren Factory-Umsetzung gilt der Preflight aus `artifacts/cicd_delivery_factory/latest_preflight.md` als bindend.

Aktuell verifizierte Tatsachen:

- Git-Remote ist `GitHub`, daher ist ein duennes `GitHub Actions`-Validierungs-Workflow repo-seitig legitim
- das UCG-DMZ-Zielbild ist bereits kanonisch:
  - `VLAN 102` -> `10.2.0.0/24`
  - `VLAN 103` -> `10.3.0.0/24`
- das Repo enthaelt aktuell `6` Runtime-Compose-Templates
- das Repo enthaelt aktuell `1` verifiziertes `Dockerfile`-Artefakt fuer den ersten Factory-App-Build
- der App-Katalog enthaelt aktuell `1` wirklich `factory_deploy_ready_now`-Kandidaten: `radio_player_frontend`

Abgeleitete harte Grenze:

- v1-Umsetzung ist **repo-side factory only**
- also erlaubt:
  - Plan
  - Manifest
  - Preflight
  - Report
  - CI-Validierung
  - App-Katalog
- nicht erlaubt ohne neue Fakten und Gated Stop:
  - echte `Coolify`-Inbetriebnahme
  - Registry-Livebetrieb
  - DMZ-Node-Provisioning
  - Public-Cutover
  - Deployment eines noch gar nicht extrahierten App-Artefakts

## Was wir **nicht** tun sollten

- nicht auf Prod-Nodes bauen
- nicht pro Umgebung unterschiedliche Images basteln
- nicht `Odoo`, `Nextcloud`, `Paperless`, `Vaultwarden` sofort active-active ueber zwei Standorte ziehen
- nicht Dev oeffentlich ohne Schutz ins gleiche Exposure wie Prod haengen
- nicht den Public-Edge mit internen Adminpfaden vermischen

## Service-Klassen

### Klasse A - Stateless Public

Geeignet fuer duale DMZ-Deployments und spaeteres Active-Active:

- Marketing-/Landing-Seiten
- kleine Frontends
- oeffentliche API-Gateways ohne lokalen Zustand
- oeffentliche Radio-/Player-Frontends

### Klasse B - Stateful Public

Nur mit externer Datenhaltung oder bewusstem Primary/Replica-Modell:

- WordPress-artige Sites
- headless CMS
- kleinere Public-Apps mit DB

### Klasse C - Internal Business

Nicht v1-active-active ueber beide Standorte:

- `Odoo`
- `Nextcloud`
- `Paperless`
- `Vaultwarden`

Diese Dienste bleiben zuerst `primary + restore/DR`, nicht dual schreibend.

### Klasse D - Smart Home / Haushalt

- `Home Assistant Rothkreuz`
- `Home Assistant Stockenweiler`

Getrennt halten. Spaeter selektiv koppeln, nicht fusionieren.

### Klasse E - Hobby / Media

- `AzuraCast`
- Radio-/Player-Zusatzpfade
- spaetere Community-/Supporter-Funktionen

Hier darf spaeter mehr experimentiert werden, aber nicht auf Kosten der Business-Stabilitaet.

## Zielarchitektur

### Management Plane

- `Coolify` laeuft **nicht** in der DMZ, sondern im internen Management-Pfad
- Zugriff nur intern/Tailscale
- Coolify steuert Zielserver ueber SSH

### Build Plane

- CI baut OCI-Images aus dem Repo
- Artefakte landen in einer OCI-Registry
- bevorzugt ein registry-kompatibler Standard statt Controller-Spezialformaten

Empfohlene Registry-Reihenfolge:

1. `GHCR` oder `Forgejo/Gitea Registry`, wenn schnell und stabil
2. spaeter `Harbor`, wenn wir striktere interne Registry-Kontrolle brauchen

### Registry-Entscheidung v1

Der erste konkrete repo-seitige Standard ist jetzt:

- Registry: `GHCR`
- Namespace: `ghcr.io/wolfeetech/frawo`
- erster Referenzdienst: `ghcr.io/wolfeetech/frawo/radio-player-frontend`

Das ist aktuell die professionellste Low-Friction-Wahl, weil der Git-Remote bereits `GitHub` ist und damit Build + Package-Push ohne zusaetzliche Registry-Infrastruktur definierbar sind.

### Env-/Secret-Contract v1

Der erste Referenzdienst hat jetzt saubere Vorlagen:

- `apps/radio-player-frontend/env/dev.env.example`
- `apps/radio-player-frontend/env/prod.env.example`
- `deployment/factory/contracts/GHCR_CONTRACT.md`
- `deployment/factory/contracts/SECRET_ENV_CONTRACT.md`

Wichtig:

- nur der stateless Referenzdienst bekommt jetzt einen generischen Factory-Contract
- Business-Apps bleiben weiter ausserhalb eines vorschnellen gemeinsamen Factory-Secret-Modells

### Runtime Plane

#### Dev

- `dev` ist standardmaessig **nicht public-first**
- Zugriff vorzugsweise intern, per Tailscale oder via Allowlist
- auto deploy auf jede gruen gemergte `develop`-Aenderung

#### Prod

- `prod` deployt auf dedizierte DMZ-Webnodes
- v1 bevorzugt `active-passive` oder DNS-failover statt sofortigem Active-Active-Mythos
- echtes `active-active` nur fuer `Klasse A`

### DMZ-Topologie

#### Rothkreuz / Anker

- bestehendes Zielmodell: `VLAN 102 Anker-DMZ` fuer Public Web
- bestehendes Zielmodell: `VLAN 103 Anker-DMZ-Radio` fuer radio-nahe Public-Pfade

#### Stockenweiler

- zweiter DMZ-Webnode ist sinnvoll, aber erst nach sauberem Management- und Storage-Pfad
- exakte DMZ-Subnetzdefinition dort bleibt vorerst `TBD`

## Dev-/Prod-Modell

### Branching

- `feature/*` = KI-/Arbeitszweige, nur CI
- `develop` = integrierter Tagesstand, auto deploy auf `dev`
- `main` = produktionsnaher Branch, nur durch Promotion
- `tag v*` = produktive immutable Releases

### Promotion

Best Practice fuer euren Wunsch "tagsueber dev, einmal taeglich stabil nach prod":

1. Tagsueber wird auf `develop` gearbeitet
2. Jede Merge nach `develop` baut ein immutable Image und deployed nach `dev`
3. Ein taeglicher Release-Job markiert den **letzten gruenen** `develop`-Stand als `prod-candidate`
4. `prod` deployt nur aus einem immutable Tag oder Release-Candidate

Das ist professioneller als direkt `develop -> prod` blind durchzuschieben.

## Deployment-Trigger

### Dev

- Trigger: Merge/Pusch nach `develop`
- Schritte:
  - lint/tests
  - build image
  - push registry
  - spaeter Coolify deploy `dev`
  - smoke tests

Aktueller repo-seitiger Ist-Stand:

- `radio-player-frontend-build` validiert den OCI-Build
- `radio-player-frontend-package` definiert den `GHCR`-Push-Pfad
- ein echter `Coolify`-Deploy bleibt weiter `gated_infra`

### Prod

- Trigger: taegliche Promotion oder bewusster Release-Tag
- Schritte:
  - nutze genau das bereits getestete Image
  - deploy zuerst `prod-primary`
  - smoke tests
  - dann `prod-secondary`
  - DNS/Failover pruefen

## Backup-Strategie

### Grundsatz

Backup trennt sich in drei Klassen:

1. `Git + IaC + CI/CD Config`
2. `Immutable Build-Artefakte`
3. `Stateful Runtime-Daten`

Wir sichern nicht nur Server, sondern die ganze Lieferkette.

### 1. Repo / IaC / Delivery-Konfiguration

Muss versioniert und extern repliziert sein:

- Git-Repository
- Ansible, Manifeste, Runbooks, SSOT
- `Coolify`-App-Definitionen als exportierbare Konfiguration
- Registry-Namen, Image-Tags, Deploy-Variablenstruktur

Regel:

- keine produktionskritische Deploy-Logik nur in der UI halten
- jede relevante Runtime-Konfiguration auch repo- oder exportierbar halten

### 2. OCI-Artefakte

- jedes Release wird als immutable Image-Tag gespeichert
- `prod` deployt nur aus einem wiederverwendbaren Tag
- alte bekannte gute Releases bleiben fuer Rollback vorhanden

Retentionsregel v1:

- `dev`: letzte `20` erfolgreiche Images
- `prod`: letzte `10` stabile Releases plus letzter bekannter guter Tag

### 3. Runtime-Daten

#### Klasse A - Stateless Public

- kein klassisches Datenbackup als Primaerschutz
- Schutz besteht aus:
  - Repo
  - Image-Tag
  - Env-/Secret-Definition
  - Proxy-/DNS-/Deploy-Konfiguration

Restore = Redeploy.

#### Klasse B - Stateful Public

- DB-Dumps
- Volume-/Object-Storage-Backups
- App-Konfiguration getrennt von Nutzdaten

#### Klasse C - Internal Business

Backup erfolgt zweistufig:

1. Infrastruktur-/VM-Backup
2. app-native Konsistenzsicherung wo sinnvoll

Pfad v1:

- `PBS` ist das Zielsystem fuer konsolidierte VM/CT-Backups
- bis PBS voll gruen ist, bleibt der lokale Proxmox-Backup-Pfad sichtbar im SSOT

App-native Mindeststrategie:

- `Odoo`
  - PostgreSQL-Dump
  - Filestore/attachments
  - Compose-/Config-Stand
- `Nextcloud`
  - Datenbank
  - `config.php`
  - App-/Data-Pfad nur in konsistentem Wartungsfenster oder ueber VM-Backup
- `Paperless`
  - Datenbank
  - consume/media/export-Pfade
  - OCR-/Config-Stand
- `Vaultwarden`
  - DB/volume
  - Admin-/SMTP-Konfigurationspfad
  - Recovery-Material separat offline

#### Klasse D - Smart Home

- `Home Assistant` je Haushalt getrennt sichern
- Backup pro Instanz als vollstaendiger Snapshot/Backup
- keine gemischten household-Backups

#### Klasse E - Hobby / Media

- `AzuraCast`
  - Datenbank
  - Station-/Mount-/Automation-Konfig
  - Medienbibliothek oder mindestens deren kanonische Quelle
- `yourparty`-Legacy in Stockenweiler
  - `VM 210 azuracast-vm`
  - `CT 207 radio-wordpress-prod`
  - `CT 208 mariadb-server`
  - `CT 211 radio-api`

Diese Payload muss vor jeder Ausduennung zuerst gesichert sein.

### Offsite / Standortstrategie

Best Practice fuer euren Zwei-Standorte-Fall:

- `Rothkreuz` bleibt primaerer Produktionsstandort
- `Stockenweiler` ist zunaechst nicht gleichwertige Schreib-Prod, sondern spaeterer DR-/Failover-/Zusatzstandort
- Offsite-Backups duerfen zwischen den Standorten repliziert werden
- dual schreibende Business-Apps sind **nicht** der erste Schritt

### Retention v1

- taeglich: `7`
- woechentlich: `4`
- monatlich: `6`

## Restore-Strategie

### Grundsatz

Ein Backup ohne dokumentierten Restore ist nicht belastbar.

Darum gibt es drei Restore-Arten:

1. `Redeploy Restore`
2. `Node/VM Restore`
3. `App/Data Restore`

### 1. Redeploy Restore

Fuer stateless public apps:

- letztes gutes Image-Tag nehmen
- auf `dev` oder `prod` erneut deployen
- Health Check laufen lassen
- DNS/Traffic nur bei gruenem Zustand schalten

Das ist der Standard-Rollback fuer die spaetere Delivery-Fabrik.

### 2. Node/VM Restore

Fuer stateful interne Systeme:

- Restore ueber `PBS` oder den aktuell sichtbaren Proxmox-Backup-Pfad
- zuerst immer in isolierte Test-ID / Test-IP restaurieren
- erst nach sichtbarem Verifikationscheck auf produktive Recovery entscheiden

Das gilt besonders fuer:

- `Odoo`
- `Nextcloud`
- `Paperless`
- `Home Assistant`

### 3. App/Data Restore

Fuer selektive oder schnellere Wiederherstellung:

- DB-only Restore
- Files/attachments/media Restore
- Config Restore
- Secrets/Env aus Vault/gesichertem Config-Pfad wiederherstellen

### Restore-Drills

V1-Minimum:

- monatlich ein sichtbarer Restore-Drill fuer genau **einen** stateful Kerndienst
- rotierend zwischen `Odoo`, `Nextcloud`, `Paperless`, `Home Assistant`
- nach jeder groesseren Delivery-/Storage-Aenderung zusaetzlicher Proof-Drill

### RTO/RPO pragmatisch

#### Klasse A - Stateless Public

- `RTO`: Minuten
- `RPO`: nahe `0`, weil Repo/Image/Config die Wahrheit sind

#### Klasse C - Internal Business

- `RTO`: Stunden, nicht Minuten, in V1 realistisch
- `RPO`: letztes erfolgreiches Backup plus ggf. app-native Dump-Frequenz

#### Klasse D - Smart Home

- `RTO`: Stunden
- `RPO`: letzter HA-Backup-/Snapshot-Stand je Haushalt

### Prod-Promotion-Regel mit Restore-Bezug

Ein Release darf nur dann als professionell gelten, wenn gilt:

- letzter bekannter guter Tag existiert
- Rollback-Tag ist bekannt
- Backup-/Restore-Pfad fuer die betroffene Service-Klasse ist dokumentiert
- fuer stateful Kerndienste existiert ein frischer sichtbarer Restore-Proof im Kanon

## High Availability realistisch

### V1 realistisch

- zwei Webnodes in zwei Standorten
- gleicher stateless Web-Stack
- externer DNS-Failover oder Health-Checked Traffic Steering
- Rollback ueber Redeploy des letzten bekannten guten Images

### Nicht V1

- dual-schreibendes Odoo ueber zwei Standorte
- dual-schreibendes Nextcloud/Paperless ohne bewusstes Datenmodell
- WAN-Proxmox-Cluster als Delivery-Fundament

## Odoo im Delivery-Modell

`Odoo` wird nicht als erster dualer Public-Webnode-Kandidat behandelt.

Professioneller Pfad:

1. Odoo intern fachlich production-ready machen
2. Customer-Portal-Scope definieren
3. oeffentliche Website-/Landing-Komponenten bei Bedarf entkoppeln
4. nur klar getrennte Public-Pfade spaeter auf die Web-Delivery-Fabrik ziehen

## AzuraCast im Delivery-Modell

`AzuraCast` ist ein guter Hobby-/USP-Pfad, aber nicht der erste Kern der Delivery-Fabrik.

Sinnvolle Kopplung:

- `Odoo` = CRM, Website, Sponsoren, Newsletter, Community-/Supporter-Flows
- `AzuraCast` = Streaming, Station, Schedule, Metadata, Player

Also nicht "AzuraCast-User als Master-Identity", sondern Odoo darum herum.

## Rollout-Reihenfolge

### Phase 0 - Definition

- Delivery-Fabrik im Repo definieren
- Service-Klassen festziehen
- Branch-/Promotion-Modell festziehen

### Phase 1 - CI Standardisieren

- gemeinsame Build-/Test-Entry-Points im Repo
- OCI-Image-Standard pro deploybarer App
- Registry festlegen

### Phase 2 - Dev Umgebung

- ersten `dev`-Deploypfad bauen
- `Coolify`-Projekt fuer `dev`
- Smoke Tests nach jedem Deploy

### Phase 3 - Prod Umgebung

- `main`/Tag-basierte Promotion
- `Coolify`-Projekt fuer `prod`
- Rollback auf letztes gutes Image

### Phase 4 - Duale DMZ-Webnodes

- `Rothkreuz` Prod-Webnode
- `Stockenweiler` Prod-Webnode
- Health-Checked Failover

### Phase 5 - Oeffentliche Services

- zuerst stateless public apps
- danach bewusst ausgewertete public-facing Sonderpfade
- stateful Business-Dienste spaeter und separat

## Definition of Done

Minimal professionell:

- `develop` auto deployt auf `dev`
- `main` oder Release-Tag deployt auf `prod`
- Images sind immutable und registry-basiert
- Rollback ist ein Redeploy des letzten guten Tags
- `Coolify` ist nur Delivery-Controller, nicht Wissensquelle

Voll professionell:

- zwei Prod-Webnodes in isolierter DMZ
- Health-Checked Traffic Steering
- Secrets/Env-Trennung zwischen `dev` und `prod`
- dokumentierte Smoke Tests und Release-Gates
- klare Trennung zwischen public stateless und internal stateful Diensten


### Erster echter Deploy-Bundle-Stand

Der erste Referenzdienst hat jetzt nicht nur Build- und Registry-Contract, sondern auch einen plattformnahen Deploy-Bundle:

- `deployment/factory/apps/radio-player-frontend/compose.yaml`
- `deployment/factory/apps/radio-player-frontend/compose.dev.env.example`
- `deployment/factory/apps/radio-player-frontend/compose.prod.env.example`
- `deployment/factory/apps/radio-player-frontend/README.md`

Damit ist der erste Dienst jetzt buildbar, packagebar und als neutraler Runtime-Bundle dokumentiert, ohne schon live in Coolify oder in eine DMZ geschoben zu werden.


### Management-Node-Realitaet

Der naechste professionelle Factory-Schritt ist **nicht** sofort ein Live-Coolify-Deploy, sondern ein dedizierter interner Management-Knoten auf `Anker`.

Der faktische Auditpfad dafuer ist jetzt:

- `scripts/coolify_management_host_audit.py`
- `artifacts/coolify_management_host/latest_report.md`
- `deployment/coolify/COOLIFY_MANAGEMENT_NODE_SPEC.md`
- `deployment/factory/contracts/SECRET_DISTRIBUTION_MODEL.md`

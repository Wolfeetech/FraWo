# GEMINI Identity & Operating Rules: Homeserver 2027

## Rolle

- Rolle: Senior System Architect fuer die GbR "FraWo"
- Auftrag: Aufbau und Pflege einer hybriden Proxmox-Infrastruktur mit klarer Trennung zwischen Business, Smart Home und Media
- Ziel: reproduzierbare, sichere und agentenfaehige Betriebsdokumentation

## Workspace Identity

- Workspace-Name: `Homeserver 2027 Ops Workspace`
- Menschlich lesbarer Alias: `~/.gemini/antigravity/brain/Homeserver_2027_Ops_Workspace`
- Desktop-Shortcut: `~/Desktop/Homeserver 2027 Workspace`
- Die UUID-basierte Antigravity-Ordnerstruktur bleibt technisch erhalten; der Alias ist die offizielle Arbeitsbezeichnung.

## Aktuelles Lane-Modell

Dieses Dokument beschreibt ab jetzt nur noch delegierbare Arbeit im aktuellen Lane-Modell:

- `Lane A: MVP Closeout` -> `active`
- `Lane B: Website/Public Hold` -> `watch`
- `Lane C: Security/PBS/Infra` -> `watch`
- `Lane D: Stockenweiler` -> `watch`
- `Lane E: Radio/Media` -> `hold`

Regeln:

- Nur `Lane A` darf aktiv auf Abschluss gezogen werden.
- `Lane B` bis `Lane E` bleiben sichtbar, aber nicht gleichrangig.
- Keine neuen spezialisierten Prompt-Dateien fuer Einzelfaelle.
- Keine zweite Parallelplanung in zufaelligen Markdown-Dateien.
- Jede delegierte Aufgabe muss genau einer Lane zugeordnet sein.

## Professional-Autopilot Boundary

- `Codex` ist `lead`
- `Gemini` ist `visible_verification_only`
- `Gemini` macht keine Architekturentscheidung
- `Gemini` macht keine Repo-Mutation
- `Gemini` macht keine Runtime-/Infra-Aenderung
- `Gemini` liefert nur sichtbaren Ist-Zustand, Browser-/UI-Abnahmen und manuelle Sichtpruefungen

Falls eine Aufgabe nach:

- Netzwerk
- Public Edge
- Router
- Storage/PBS
- HA/PVE
- Datenmigration
- Security-Boundary

riecht, bleibt sie bei `Codex` oder geht als `AKTION VON DIR ERFORDERLICH:` an den Operator.

## Aktive Delegierbare Jobs

### `device_rollout_verified`

- `lane`: `Lane A: MVP Closeout`
- `goal`: Sichtbare Endnutzerabnahme fuer Franz `Surface Laptop` und `iPhone`.
- `done_when`: Beide Geraete sind mit den erforderlichen Direktpfaden und dem echten Alltagspfad sichtbar bestaetigt.
- `blocked_by`: frischer sichtbarer Geraetenachweis fehlt
- `next_operator_action`: Die Geraete im echten Alltagspfad pruefen oder vorfuehren.
- `next_codex_action`: Vor dem Closure-Schritt `scripts/device_rollout_preflight.py` laufen lassen. Nach dem sichtbaren Nachweis `scripts/prove_device_rollout.ps1` ausfuehren, damit MVP-Gate und AI-Handoff automatisch nachziehen.

### `website_public_hold`

- `lane`: `Lane B: Website/Public Hold`
- `goal`: Wahrheitspfad und Blocker fuer die oeffentliche Website sichtbar halten, ohne aktiven Release.
- `done_when`: `Lane A` ist geschlossen und ein expliziter Public-Edge-Resume beschlossen ist.
- `blocked_by`: `Lane A` ist noch aktiv
- `next_operator_action`: Keine neue Go-Live-Arbeit.
- `next_codex_action`: Nur Wahrheitspfad, Blocker und Sicherheitslage aktuell halten.

### `stockenweiler_watch`

- `lane`: `Lane D: Stockenweiler`
- `goal`: Inventar, Supportmodell, Remote-Zugriff und den spaeteren Phase-2-Backlog sichtbar halten, aber keinen Live-Rollout oder Network Marriage starten.
- `done_when`: `Lane A` ist geschlossen und Stockenweiler wird aktiv priorisiert.
- `blocked_by`: `Lane A` ist noch aktiv; `UCG`-2FA weiter blockiert
- `next_operator_action`: Nur neue echte Geraete-, Provider- oder `FRITZ!`-/`Tailscale`-Fakten liefern; keine Live-Rollout- oder Marriage-Arbeit.
- `next_codex_action`: Inventar, Supportmodell und den spaeteren Phase-2-Backlog pflegen; read-only Wahrheitschecks wie `scripts/stockenweiler_public_truth_check.py`, `scripts/stockenweiler_remote_path_probe.py` und `scripts/stockenweiler_pve_storage_probe.py` sind erlaubt, aber kein Rollout, kein Site-to-Site-VPN und keine Service-Migration.

## Nicht Delegierbar Jetzt

### `vaultwarden_recovery_material_verified`

- `lane`: `Lane A: MVP Closeout`
- `goal`: Zwei getrennte Offline-Kopien des Recovery-Materials.
- `done_when`: Frischer physischer Nachweis liegt vor.
- `blocked_by`: physischer Nachweis ist operatorgebunden
- `next_operator_action`: Recovery-Material offline in zwei getrennten Kopien pruefen oder anlegen.
- `next_codex_action`: Danach Gate und Handoff neu ziehen.

### `security_pbs_infra_watch`

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: Hardening und Reapply-Pfade gruen halten, ohne einen neuen Zertifizierungsblock zu starten.
- `done_when`: `Lane A` ist geschlossen und PBS/Infra bewusst wieder aktiv wird.
- `blocked_by`: `Lane A` ist noch aktiv
- `next_operator_action`: Nur bei echter Regression eingreifen.
- `next_codex_action`: Nur Regressionen schliessen und Reapply-Pfade aktuell halten.

### `radio_media_hold`

- `lane`: `Lane E: Radio/Media`
- `goal`: Betrieb erhalten, aber keinen Ausbau starten.
- `done_when`: `Lane A` ist geschlossen und es gibt einen expliziten Ausbauentscheid.
- `blocked_by`: `Lane A` ist noch aktiv
- `next_operator_action`: Nur Breakage melden.
- `next_codex_action`: Betriebsfaehigkeit halten, keine Scope-Erweiterung.

## Gemeinsame Zusammenarbeit mit Codex

- Gemini und Codex arbeiten aus demselben Workspace und benutzen dieselben kanonischen Dateien.
- Vor jeder Arbeit zuerst lesen:
  1. `AI_BOOTSTRAP_CONTEXT.md`
  2. `LIVE_CONTEXT.md`
  3. `README.md`
  4. `MEMORY.md`
  5. `NETWORK_INVENTORY.md`
  6. `VM_AUDIT.md`
- Nach jeder sinnvollen Aenderung:
  - kanonische Quelldatei aktualisieren
  - keine Nebennotizen in zufaelligen Dateien hinterlassen
  - `LIVE_CONTEXT.md` per Auto-Sync aktualisieren lassen oder `make refresh-context` ausfuehren
- Secrets duerfen nur in `ansible/inventory/group_vars/all/vault.yml` liegen.
- Wenn Arbeit an einer manuellen, physischen oder accountgebundenen Abhaengigkeit haengen bleibt, muss das explizit mit dem Praefix `AKTION VON DIR ERFORDERLICH:` kommuniziert werden.
- Diese Operator-Handoffs muessen drei Dinge enthalten:
  - die exakte Aktion des Operators
  - den Grund bzw. Blocker
  - das Folgepaket, das Codex oder Gemini danach direkt uebernehmen
- Offene Operator-Schritte muessen in `MEMORY.md` unter `## Aktive Operator-Aktionen` gepflegt werden.

## Source-of-Truth-Regel

- Dieser Workspace ist ab jetzt die primaere Source of Truth fuer Homeserver 2027.
- Aeltere Session-Artefakte duerfen nur fuer konfliktfreie Fakten wiederverwendet werden.
- Bei Widerspruechen gilt immer das verifizierte Runtime-Mapping:
  - `CT 100` = Toolbox, Docker-Host, Ansible-Kontrollknoten, Caddy, Split-DNS, AdGuard Home im Opt-in-Betrieb und Tailscale-Subnet-Router
  - `VM 200` = Nextcloud, Dokumentenablage und Kollaboration, Ziel-IP `192.168.2.21`
  - `VM 210` = Home Assistant OS, Ziel-IP `192.168.2.24`, jetzt stabil auf `192.168.2.24`
  - `VM 220` = Odoo, ERP/CRM, Ziel-IP `192.168.2.22`
  - `VM 230` = Paperless-ngx, Ziel-IP `192.168.2.23`
  - `raspberry_pi_radio` = spaeter dedizierter Radio-Node fuer AzuraCast
  - `surface_go_frontend` = gemeinsamer Frontend-Knoten `surface-go-frontend` auf `192.168.2.154`, Ubuntu Desktop 24.04 LTS frisch installiert, Basis-Bootstrap angewendet, SSH-Key-Zugang aktiv, Tailnet-Zugriff aktuell verifiziert ueber `100.106.67.127`
- Aeltere Aussagen wie "Toolbox nur Admin", "Home Assistant in CT 100" oder vertauschte IDs fuer Odoo und Nextcloud gelten als ueberholt.
- Surface-Stand vom letzten echten Live-Lauf:
  - `surface-go-frontend` ist frisch installiert und basis-konfiguriert
  - SSH-Zugang steht; der lokale Admin-Pfad ist aktuell auch per Passwort wieder nutzbar
  - `frontend`-Kiosk-User und lokales Portal sind live
  - Tailnet-Zugang ist verifiziert, die Surface-Pruefroutine erkennt jetzt auch den Tailscale-Admin-Pfad
  - Akku- und AC-Schlafmodus stehen auf `nothing`
  - Root-Sleep-Haertung ist fertig, die Sleep-Targets sind maskiert und ein Remote-Reboot kam sauber zurueck
  - der robuste lokale Frontend-Pfad ist jetzt:
    - Portal-Inhalt unter `/home/frontend/homeserver2027-portal`
    - loopback-only HTTP auf `127.0.0.1:17827`
    - Launcher `FRAWO Control`
    - `epiphany-browser` als aktueller stabiler Browserpfad
  - der naechste aktive Produktpfad ist jetzt keine Dashboard-Seite mehr, sondern `Surface Control V1` als Aktionskonsole
  - `Surface Control V1` ist jetzt live auf dem Geraet installiert und lokal auf `127.0.0.1:17827` verifiziert
  - sichtbarer V1-Scope:
    - `Dokumente`
    - `Odoo`
    - `Radio`
  - erste sichtbare Route-Matrix ist jetzt vorhanden:
    - `Nextcloud Eingang`, `Paperless`, `Odoo Aufgaben`, `Odoo Projekte`, `Odoo Kalender`, `Radio hoeren`, `Radio Control` = `ready`
  - die aktuelle Touch-Abnahme ist ebenfalls gruen:
    - sichtbar `Nextcloud Eingang`, `Paperless`, `Odoo Aufgaben`, `Odoo Projekte`, `Odoo Kalender`, `Radio hoeren`, `Radio Control`
    - keine Persona-Karten
    - kein Dashboard-Rest
    - die live servierte Datei auf der Surface entspricht dem aktuellen Render-Stand
  - keine Persona-Karten
  - kein grosser Statusblock
  - keine sichtbaren `Stockenweiler`-Aktionen in V1
  - Launcher-Minimalsatz live:
    - kiosk: `FRAWO Control`, `Bildschirmtastatur`
    - admin: `FRAWO Control`, `Bildschirmtastatur`, `Radio Control`, `AnyDesk`, `StudioPC Remote`
- StudioPC-Operatorzugang vom letzten echten Live-Lauf:
  - dedizierter lokaler Ops-Key: `~/.ssh/hs27_ops_ed25519`
  - Windows-native Repair-Pfad: `scripts/repair_studiopc_operator_access.py`
  - reale Alias-Zugaenge funktionieren jetzt:
    - `hs27-proxmox`
    - `hs27-toolbox`
    - `hs27-nextcloud`
    - `hs27-odoo`
    - `hs27-paperless`
    - `hs27-surface`
  - live Browser-Zugriff auf das loopback-only Surface-Portal ist jetzt ebenfalls reproduzierbar:
    - SSH-Alias `hs27-surface-portal`
    - lokaler Zielpfad `http://127.0.0.1:27827/`
    - Helper `scripts/open_surface_portal_tunnel.ps1`
    - Verifikation `powershell -ExecutionPolicy Bypass -File .\\scripts\\open_surface_portal_tunnel.ps1 -Verify`
    - letzter echte Check: `HTTP 200`, Titel `FraWo Control`
  - die aktuelle Ursache fuer zaehe Surface-Ladevorgaenge ist ebenfalls beseitigt:
    - vorher zwei aktive Uplinks mit konkurrierendem Default/DNS:
      - Ethernet `192.168.1.194 -> 192.168.1.1`
      - WLAN `192.168.2.x -> 192.168.2.1`
    - jetzt:
      - Ethernet nur noch Subnetzpfad ohne Default und ohne DNS
      - WLAN `Frawo-Direkt` ist der einzige Default-Pfad
    - letzter echte Live-Check danach:
      - `portal` ~`0.015s`
      - `cloud` ~`0.036s`
      - `paperless` ~`0.017s`
      - `odoo` ~`0.055s`
      - `radio` ~`0.088s`
      - `vault` ~`0.039s`
  - `pbs` ist davon aktuell ausgenommen, weil `VM240` gestoppt ist
- Radio-Stand vom letzten echten Live-Lauf:
  - `make radio-ops-check` ist gruen
  - `radio.hs27.internal` und `radio.hs27.internal/login` sind intern erreichbar
  - `nowplaying` liefert Daten fuer `FraWo - Funk`
  - naechster professionelle Block: `RadioLibrary` / `RadioAssets` kuratieren, danach touchfreundliche Surface-Monitorseiten
- Medienserver-Stand vom letzten echten Live-Lauf:
  - `make toolbox-media-check` ist gruen
  - Jellyfin V1 laeuft auf `CT 100 toolbox`
  - `media.hs27.internal`, `192.168.2.20:8096` und `100.99.206.128:8449` liefern die UI
  - ein Bootstrap-Sync vom Pi in die Toolbox-Mediathek ist jetzt live:
    - Quelle `wolf@100.64.23.77:/srv/radio-library/music-usb/yourparty.radio/`
    - Ziel `/srv/media-library/music/bootstrap-radio-usb/`
    - Check `make toolbox-media-sync-check`
    - Fortschritt `make toolbox-media-bootstrap-progress`
    - Musikreport `make toolbox-music-library-report`
  - `CT 100` wurde dafuer operativ von `10G` auf effektiv `96G` Rootfs vergroessert; ohne diesen Schritt lief der Sync in `No space left on device`
  - der Startup Wizard ist abgeschlossen und die Musikbibliothek haengt bereits an `/media/music`
  - naechster Schritt ist jetzt, den Bootstrap-Sync weiterlaufen zu lassen und danach den ersten Thomson-/Google-TV-Client anzubinden
  - `make toolbox-music-scan-issues` und `make toolbox-music-curation-candidates` liefern jetzt einen echten Kurationsbefund fuer den laufenden Import
  - letzter Befund: die Problemdatei ist bereits nach `/srv/media-library/quarantine/bootstrap-review` verschoben; aktuell `0` neue Quarantaene-Kandidaten und `9` harmlose Sidecars
  - `make toolbox-music-curated-layout` zeigt jetzt die naechste saubere Ausbaustufe: Bootstrap voll, `favorites`/`curated` noch leer
  - neuer Auswahl-Workflow steht:
    - `manifests/media/favorites_paths.txt`
    - `manifests/media/curated_paths.txt`
    - `make toolbox-music-selection-seed-report`
    - `make toolbox-music-selection-sync`
  - letzter Seed-Report: `1075` Kandidaten; groesste Bloecke beginnen bei `clean/Various Artists`, `clean/Nite Fleit`, `clean/Helena Hauff`
 - heuristischer Starter wurde bereits promoted und materialisiert:
    - `12` Favorites
    - `20` Curated
  - aktueller Restpunkt im Bestand: mehrere importierte Artist-/Release-Ordner sind noch mit restriktiven Rechten sichtbar; der Report listet sie fuer spaetere Kuration
  - portabler Backup-Zwischenpfad ist jetzt ebenfalls vorbereitet:
    - `PORTABLE_BACKUP_USB_PLAN.md`
    - `make portable-backup-usb-autoprepare`
    - `make portable-backup-usb-fill`
    - `make portable-backup-usb-check`
    - `make portable-backup-usb-run`
  - der `64GB`-Stick ist nicht mehr nur Shuttle, sondern traegt jetzt das Interim-PBS-v1
  - Stand `2026-03-21`: der Stick ist bereits an Proxmox angeschlossen, als `HS27_PORTABLEBK` formatiert und in den Interim-PBS-Pfad repurposed
  - aktueller Live-Zustand:
    - `/srv/portable-backup-usb` bleibt der USB-Mount
    - `/srv/pbs-datastore` ist bind-mounted auf dieselbe USB-Flaeche
    - Proxmox-Storage `pbs-usb` ist aktiv
    - `VM 240 pbs` laeuft mit `3072 MB` RAM, `32G` Systemdisk und `40G` USB-Data-Disk
    - PBS-Gast ist installiert auf `192.168.2.25`
    - Datastore `hs27-interim` ist aktiv
    - Proxmox-Storage `pbs-interim` ist aktiv
    - taeglicher PBS-Job `hs27-pbs-interim-daily` ist angelegt
- Interim-Retention ist aktiv: `02:40`, `keep-daily=2`, `keep-weekly=1`, `keep-monthly=1`
    - erster gruener Proof-Backup-Lauf ist jetzt erbracht:
      - `VM 220`
      - Snapshot `vm/220/2026-03-21T10:04:30Z`
      - Proxmox-Taskstatus `exitstatus: OK`
    - erster gruener Restore-Drill ist jetzt ebenfalls erbracht:
      - `VM 220` -> Test-VM `920`
      - `HTTP 200` auf `http://192.168.2.240:8069/web/login`
      - Test-VM danach wieder entfernt
  - aktueller Restblock sind nun wiederkehrende Restore-Drills und spaeter groesseres PBS-Storage, nicht mehr die PBS-Erstinbetriebnahme
- Portal-Stand vom letzten echten Live-Lauf:
  - `portal.hs27.internal` liefert jetzt das reduzierte Root-Portal fuer den Business-MVP
  - direkt sichtbar sind nur noch `Nextcloud`, `Paperless`, `Odoo`, `Franz Start` und `Vault`
  - `status.json` liefert dort weiter den Live-Snapshot; `make toolbox-portal-status-check` ist aktuell gruen mit `7/7` gesunden Kernservices
  - `portal.hs27.internal/franz/` liefert den reduzierten Franz-Pfad fuer `Nextcloud`, `Paperless`, `Odoo`, `Vault`, `Nextcloud Eingang` und `Franz Mobil Start`
  - die sichtbare Browser-Abnahme fuer Root-Portal und Franz-Seite ist gruen
- Priorisierung fuer Restbudget:
  - zuerst Server-/Backup-Sicherheit, PBS-Restore-Drills und Inventar-Finalisierung
  - erst danach Surface-Browser-/Touch-Tastatur-Polish
 - HAOS-USB-Stand:
  - `VM 210` ist stabil, aber USB-Passthrough ist bewusst weiter gesperrt
  - der neue Guardrail ist `make haos-usb-audit`
  - aktuell sichtbar ist nur der PBS-Backup-Stick (`USB Disk 3.0`), kein Zigbee-/Bluetooth-/SkyConnect-Dongle
 - Fortschritts-Stand vom letzten echten Live-Lauf:
  - `make plan-progress` liefert aktuell `masterplan_progress_percent=69`
  - Band: `mid_stage`
  - naechste echte Empfehlung: `finish_inventory_and_haos_usb_then_keep_monthly_pbs_restore_drills`

## Aktive Artefakte

- `AI_BOOTSTRAP_CONTEXT.md` ist die komprimierte Read-First-Datei fuer kuenftige KI-Starts.
- `README.md` ist die Frontdoor fuer Menschen und Agenten.
- `LIVE_CONTEXT.md` ist das automatisch aktualisierte Handoff-Dokument.
- `NETWORK_INVENTORY.md` ist das kanonische menschlich lesbare LAN-Inventar.
- `ansible/inventory/hosts.yml` ist das maschinenlesbare Inventar.
- `ansible/inventory/group_vars/all/vault.yml` ist das einzige zulaessige Ziel fuer weiter benoetigte Secrets.
- `VM_AUDIT.md` haelt den pruefbaren Ist-Zustand und die erfolgten VM-Remediations fest.
- `BACKUP_RESTORE_PROOF.md` haelt den aktuell verifizierten lokalen Backup-/Restore-Nachweis fest.
- `PBS_VM_240_SETUP_PLAN.md` haelt den kontrollierten PBS-Rolloutpfad und seine Stage Gates fest.

## Infrastruktur-Kanon

- Host: ThinkCentre M920q, Proxmox VE auf NVMe
- LAN: `192.168.2.0/24`
- Aktueller Gateway: Vodafone Easy Box auf `192.168.2.1`
- Geplanter Gateway-Nachfolger: `UniFi Cloud Gateway Ultra (UCG-Ultra)`, Hardware vorhanden, aber noch nicht aktiv
- Toolbox: `CT 100` auf `192.168.2.20`
- Overlay-Zugriff: Tailscale Mesh-VPN
- Reverse Proxy: Caddy auf `CT 100`
- Aktive interne DNS-Zone: `hs27.internal`
- Spaeterer professioneller Naming-Zielpfad: `frawo.home.arpa`
- Interner DNS-/Filter-Dienst: AdGuard Home, live auf `CT 100` im Test-/Opt-in-Betrieb, Admin lokal auf `127.0.0.1:3000`
- Tailscale ist auf `CT 100` live und dem Tailnet beigetreten

## Guardrails

1. Vor jeder aendernden Arbeit an `CT 100` oder den VMs `200/210/220/230` muss per Proxmox-MCP ein Snapshot erstellt werden.
2. Lifecycle-Aktionen wie Start, Stop, Snapshot und Statusabfrage laufen primaer ueber Proxmox-MCP.
3. QEMU Guest Agent ist Zusatzfunktion fuer Gast-Infos, sauberere Shutdowns und moegliche Freeze/Thaw-Unterstuetzung; er ist keine Voraussetzung fuer Start, Stop oder Snapshot.
4. Business-Dienste laufen isoliert in eigenen VMs. Keine produktive Konsolidierung von Odoo, Nextcloud oder Paperless in `CT 100`.
5. Home Assistant laeuft als vollwertige HAOS-VM, nicht als Container oder Supervised-Installation.
6. AzuraCast ist als spaeterer dedizierter `Raspberry Pi 4`-Radio-Node geplant und nicht als strategischer Dauerdienst auf `CT 100`.
7. Keine direkte Internet-Freigabe von Admin-UIs oder Business-Diensten. Externer Zugriff erfolgt ueber Tailscale.
8. Caddy dient in v1 als interner L7-Router. Standard ist internes HTTP; die Transportverschluesselung fuer Remote-Zugriffe kommt durch Tailscale.
9. Split-DNS auf `CT 100` ergaenzt MagicDNS fuer App-Namen:
   - `odoo.hs27.internal`
   - `cloud.hs27.internal`
   - `paperless.hs27.internal`
   - `ha.hs27.internal`
   - `radio.hs27.internal`
   - Live bleibt diese Zone zunaechst unveraendert; eine spaetere bewusste Migration auf `frawo.home.arpa` ist erlaubt, aber kein Parallelbetrieb mit `frawo.internal` oder `frawo.lan`.
10. Backup-Planung geht auf eine dedizierte PBS-Instanz. Solange keine eigene Hardware bereitsteht, ist eine dedizierte PBS-VM der Standardpfad.
11. Der Gateway-Wechsel auf den `UniFi Cloud Gateway Ultra` ist ein eigener Netz-Cutover und darf nicht waehrend laufender LXC-/VM-Grundaufbauarbeiten erfolgen.
12. Der richtige Zeitpunkt fuer den UCG-Ultra-Cutover ist erst erreicht, wenn:
    - alle Ziel-LXCs und VMs gebaut und stabil sind
    - Backup und Restore fuer die Business-VMs praktisch nachgewiesen sind
    - Inventar, IP-Plan und Reservierungsstrategie feststehen
    - ein klares Rollback auf die Easy Box vorbereitet ist
13. AdGuard Home ist ein interner Infrastrukturdienst. Er wird zuerst nur als opt-in DNS fuer Trusted Clients und Admin-Systeme getestet und erst nach kontrollierter DHCP-/Gateway-Steuerung zum primaeren LAN-DNS.
14. Oeffentliche Exposition ist ein spaeter eigener Edge-Block:
    - keine oeffentliche Freigabe, solange Easy Box plus flaches LAN der aktive Netzrand sind
    - keine direkte Exposition fuer Proxmox, Toolbox, PBS, AdGuard Home oder Home-Assistant-Admin
    - wenn es soweit ist, nur ueber klar definierte App-Endpunkte, TLS, Logging, Monitoring, Auth und dokumentierten Rollback
15. Server-VMs sollen keine unnoetigen Link-Local-Namensdienste offen haben:
    - `LLMNR=no`
    - `MulticastDNS=no`
16. AdGuard-Admin auf `CT 100` bleibt loopback-only, bis spaeter ein explizit gehaerteter Management-Pfad existiert.
17. Das Surface Go ist ein Frontend-Knoten und kein Server:
    - kein lokaler Reverse Proxy
    - kein lokaler Docker-Host
    - kein lokaler KI-Node
    - `nginx` oder aehnliche Altlasten werden beim Clean-Rebuild entfernt
18. Der Standardpfad fuer das Surface Go ist:
    - `Ubuntu Desktop 24.04 LTS`
    - lokaler Admin-User `frawo`
    - separater kiosk-User ohne sudo
    - Stock-Ubuntu-Kernel zuerst, `linux-surface` nur bei echten Hardware-Luecken
    - lokales Portal enthaelt jetzt auch einen direkten `Radio Control`-Pfad fuer AzuraCast

## Betriebsmodell

- IaC-Prioritaet:
  - VMs werden primaer mit Ansible und Proxmox-MCP verwaltet.
  - Docker-Dienste in `CT 100` werden ueber Compose-Dateien und Runbooks gepflegt.
- Netzwerkmodell:
  - LAN bleibt das Primarnetz.
  - Tailscale auf `CT 100` annonciert nur `192.168.2.0/24`.
  - `--accept-routes` ist kein Default fuer den Router selbst.
  - Der UCG-Ultra ist Planungsgegenstand fuer die spaetere DHCP-/Firewall-/VLAN-Zentralisierung, aber noch nicht Teil des Live-Netzes.
  - AdGuard Home wird konzeptionell auf `CT 100` mitgefuehrt:
    - Phase 1: interner Testbetrieb fuer Trusted Clients und `hs27.internal`
    - Phase 2: primaerer DNS erst nach kontrollierter DHCP-Fuehrung
- Adressierungsmodell:
  - MagicDNS fuer Knoten wie `toolbox` und `proxmox`
  - `hs27.internal` fuer dienstspezifische Hostnamen
- Rebuild-Regel fuer `CT 100`:
  - Rebuild ist erlaubt, wenn Docker, Tailscale, `/dev/net/tun` oder DNS-Dienst in der bestehenden CT nicht stabil zusammenarbeiten.
  - Rolle und Ziel-IP `192.168.2.20` bleiben dabei unveraendert.

## Aenderungsworkflow

1. Ist-Zustand verifizieren.
2. Snapshot ueber Proxmox-MCP erstellen.
3. Zielsystem aendern.
4. Fachliche Verifikation durchfuehren:
   - Dienst erreichbar
   - Logs sauber
   - Backup-/Rollback-Pfad noch intakt
5. `MEMORY.md` aktualisieren, wenn sich Zustandswissen, IPs, Rollen oder Guardrails geaendert haben.

## Aktuelle Prioritaeten

1. `NETWORK_INVENTORY.md` und `ansible/inventory/hosts.yml` ueber den Easy-Box-Abgleich finalisieren.
2. `CT 100` als echten Tailnet-Knoten betreiben und den Opt-in-DNS-Pilot sauber weiterfuehren.
   - Tailscale-Join ist erfolgt
   - die Subnet-Route `192.168.2.0/24` ist lokal annonciert; die Tailnet-Freigabe bleibt als externer Admin-Schritt im Blick
3. Den lokalen Backup-/Restore-Proof fuer `VM 200`, `VM 220` und `VM 230` in eine saubere PBS-Zielarchitektur mit taeglichen Jobs und Retention ueberfuehren.
   - Runner und Stage-Gate-Checks fuer `VM 240` sind vorbereitet
   - die offizielle PBS-ISO ist bereits auf Proxmox staged und checksum-verifiziert
   - der reale Blocker ist jetzt nur noch fehlendes separates Backup-Storage
4. Die spaetere Public-Exposure-Architektur mit Domain, DNS, TLS, Auth, Monitoring und klarer Edge-Trennung festziehen, aber im Hold-Modus halten, bis CI und Content bewusst freigegeben sind.
5. `VM 210` als HAOS-VM im abgesicherten Betriebsstandard halten.
   - Home Assistant antwortet stabil auf `http://192.168.2.24:8123`
   - `ha.hs27.internal` ist intern live ueber Caddy
   - lokaler Backup-Bestand deckt `VM 210` bereits ab
   - USB-Passthrough bleibt bis zum Anstecken echter Adapter nur Planungsstand
6. `UniFi Cloud Gateway Ultra` im Plan halten, aber erst nach abgeschlossener Service-Basis und validierten Backups in ein eigenes Netz-Cutover ziehen.
7. Den dedizierten `Raspberry Pi 4`-Radio-Node vorbereiten und `radio.hs27.internal` erst danach produktiv schalten.
8. `make start-day` ist der kanonische Tagesbeginn fuer Codex, Gemini und den Operator.
9. Das Surface Go als `frontend-node` nicht weiter als Dashboard, sondern als kleine interne Aktionskonsole fuer `Dokumente`, `Odoo` und `Radio` ausbauen.

## Aktuelle Gemini-Jobs

- aktuell kein aktiver Pflicht-Gemini-Job im MVP-Kern
- die sichtbare MVP-Abnahme fuer `wolf_login_walkthrough` und `franz_login_walkthrough` ist am `2026-03-30` abgeschlossen
- verbleibende MVP-Blocker sind derzeit operator- oder physisch gebunden:
  - `strato_mail_model_verified`
  - `device_rollout_verified`
  - `vaultwarden_recovery_material_verified`
- oeffentliche Website bleibt im Hold-Modus
- keinen weiteren Website-Browsertrack starten, bis Codex den Hold bewusst aufhebt

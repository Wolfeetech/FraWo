# NOW — Echter Live-Stand (BITTE ZUERST LESEN)

> ## 🔴 ÜBERGABE / HANDOFF 2026-07-23 (Claude Code → Antigravity)
> Claude Code hatte Session-Limit erreicht. **Antigravity: bitte übernehmen, wie ein Angestellter, nach Best Practice.**
> 1. **Neues Projekt „IT-Abteilung / Multi-Agenten-Koordination"** (von Wolf freigegeben): Plan + nächste Schritte in [`DOCS/superpowers/plans/2026-07-23-it-department-agents.md`](DOCS/superpowers/plans/2026-07-23-it-department-agents.md). Zuerst die 2 Rückfragen an Wolf klären (siehe Plan), dann Schritt 1. Beanspruche die Arbeit sichtbar (Wolf kurz sagen „Antigravity übernimmt").
> 2. **HEUTE-Vorfall (kritisch, verifiziert):** ProDesk-Host-Kollaps durch defekte SATA-Platte (ata2 link down) → per SysRq-Reboot gerettet, ALLES wieder oben (Odoo/Website ✅, Radio-Stream ✅ auf Fallback, Host-Last 1,4). **Defekte Platte NICHT ersetzbar (Wolf: „mit dem was wir haben").**
> 3. **Radio-Musik-Wiederherstellung = SEPARATES offenes Projekt** (nicht mit #1 vermischen): AzuraCast-Bibliothek leer, weil sie vom stillgelegten Stockenweiler-Testserver (NFS 192.168.178.25, tot) kam. Master-Musik ist HEIL auf dem Fileserver. Repariert: toter NFS aus VM210-fstab raus, Samba-Creds erneuert (`//10.1.0.94/music` läuft). **Noch offen:** `//10.1.0.94/radio` weist VM210 ab (fileserver-seitig prüfen) → dann AzuraCast neu einlesen + Playlists/Dayparting neu. Details siehe Claude-Memory-Hinweis unten / dieser Block.
> 4. **StudioPC-Routing-Fix:** `tailscale set --accept-routes=false` (LAN direkt/schnell statt 500ms-Tunnel). Nie die eigene Subnetz-Route via Tailscale akzeptieren.

**Letzte Verifikation: 2026-07-16 (live, StudioPC Rothkreuz, Claude-Agent — Werkstatt-Inventur Teil 2 + Odoo-DevOps-Automatik + Repo-Sync).**

> **Odoo (CT140, 10.1.0.112:8069) = EINZIGE SSOT für ALLES** — Tasks, Infra-Entscheidungen, Roadmap. NOW.md = nur Live-Infra-State (was wirklich läuft). Alle anderen Docs (LIVE_CONTEXT, MASTERPLAN, ROADMAP, AI_BOOTSTRAP_CONTEXT, STATUS, todo) = **STALE, nicht mehr lesen**.
> Agenten: IMMER zuerst Odoo-Projekte/Tasks lesen, NICHT andere MD-Files als Planungsgrundlage verwenden.

## 🆕 Werkstatt-Inventur Teil 2 — 2026-07-16 (Claude-Agent)
- **🔴 Sicherheitsbereinigung durchgeführt (Details intern in Odoo #815):** versehentlich eingecheckte Secret-Dateien aus HEAD entfernt + `.gitignore` gehärtet (Commit dfcd9c8). Passwort-Rotation als offener Wolf-Punkt in Odoo dokumentiert. _(Betroffene Systeme/Konten bewusst NUR intern in Odoo, nicht hier im public Repo.)_
- **Repo entrümpelt (Commit 58d2684):** großes Zip-im-Repo, leere/stray Dateien, alte JSON-Dumps, gerendertes HTML gelöscht; Einmal-Skripte → `archive/scripts_2026-07-16/`. Aktiv belassen: openclaw_web_server.py+.yaml, frawo_llama3.modelfile. `todo.md` gegen Ist-Stand abgeglichen.
- **Lokaler dirty Clone `~/FraWo` gesichtet (NICHT gelöscht):** enthält unfertige, wertvolle Idee `infra/odoo/odoo_devops_task_bridge.py` (Odoo→OpenClaw Task-Bridge, CT150-Poller, env-basiert, keine Secrets) — sollte künftig sauber committet werden.

## 🆕 Tagesabschluss 2026-07-15 (verifiziert — „Werkstatt-Reinigung", Claude-Agent)

- **🔓 Anker wieder voll im LAN erreichbar — Root-Cause gefunden & behoben.** Zwei Altlasten: 1) `tailscale accept-routes` zog auf anker/openclaw/radio-node die Route `10.1.0.0/24 → tailscale0` (Policy-Tabelle 52) — Antworten an LAN-Nachbarn gingen in den VPN-Tunnel (asymmetrisch = tot, Pakete kamen laut tcpdump an, Antwort nahm falschen Weg). Fix: `tailscale set --accept-routes=false` auf **allen drei** Nodes. 2) sshd auf anker war via `/etc/ssh/sshd_config.d/listen.conf` an die tote Alt-IP `10.4.0.99` gebunden — Datei entfernt (Backup `/root/altlast_sshd-listen.conf_2026-07-15.bak`). **Lehre:** LAN-Mitglieder dürfen NIE die Route ihres eigenen Subnetzes via Tailscale akzeptieren. Ping+SSH auf 10.1.0.92 / .31 / .200 vom StudioPC: ✅.
- **Firewall anker:** `cluster.fw` um `IN ACCEPT -source 10.1.0.0/24` ergänzt — das eigene Server-VLAN fehlte komplett (nur Tailscale/10.4.0.x/Alt-LANs waren erlaubt).
- **Updates:** anker (73 Pakete) + ProDesk (140 Pakete) voll aktualisiert. ⚠️ **ProDesk: Reboot ausstehend** (neuer Kernel, 2–3 Min Downtime aller Dienste) — wartet auf Wolfs Zeitfenster. anker: kein Reboot nötig; `autoremove` −10 GB (root 32%→18%).
- **anker Thin-Pool entschärft: 94,7% → 66,1%** (fstrim aller CTs + VM240-PBS-Discard). Kein Speicheralarm mehr.
- **Backup-Hygiene:** 4 tote Jobs auf anker gelöscht (hs27-interim + 3 Legacy), 1 Legacy-Job auf ProDesk gelöscht — der wollte 9 nicht existente VMIDs sichern und war die Ursache der „job errors" vom 14.07. Stale Storages disabled: `pbs-usb`, `ssd2tb` (anker), `anker-music` (ProDesk). **Aktiv:** anker `daily-all-pbs`→GDrive 04:00 · ProDesk →pbs-frawo 04:00 + hdd-backup 05:30 (kritische Gäste).
- **Kaputte Units anker bereinigt:** `homeserver2027-local-business-backup` (Quelle wiederkehrender vzdump-200-Fehler) + `openipmi` disabled, `mnt-hs27`-Leiche weg → `systemctl --failed` = leer.
- **📻 Radio Split-Brain GELÖST:** CT130 radio-node hat kein zweites AzuraCast mehr. Verwaiste Alt-Stack-Container `radio-redis`/`radio-db` (Compose-Projekt „deployment") gestoppt, restart=no, Volumes erhalten. **VM210 (10.1.0.38) = einzige Radiostation.**
- **10.1.0.142 identifiziert:** MAC-Präfix 74:ac:b9 = **Ubiquiti** — eigenes UniFi-Gerät (AP/Switch), kein Fremdgerät. Punkt geschlossen.
- **ProDesk gesund:** Load ~2.0 (war 7.9), CT150 monitoring-stack läuft. Swap 4 GB belegt (Reboot löst das). CT109/CT130 existieren auf ProDesk nicht mehr.
- **anker:** CT100 toolbox + VM300 nextcloud laufen (wieder) — klären ob gewollt. Journals beider Nodes vakuumiert.
- **Odoo:** #779 Sissy-Rückgabe abgeschlossen (14.07. alles zurück, von Wolf bestätigt). Produktdaten-Messung 15.07.: 148 physische Produkte — SKU 87% · VK 95% · EK 55% · Lieferant 24%. **Thomann-Datei fehlt weiterhin** (als erledigt markiert, aber nie übergeben; Handeinträge haben die Metriken nicht bewegt).
- **StudioPC Werkstatt:** Desktop + „FRAWO Ops" aufgeräumt (PLAN_odoo17to19, SSOT_NOW.md, frawo-homepage.html → Archive_Outdated). ⚠️ Klartext-Credentials auf Desktop (`pw safe.txt`, `servAssi_deploy_key.txt`) → sollen in Vaultwarden, wartet auf Wolf-OK. ⚠️ Lokaler Clone `~/FraWo` ist 17 Tage stale + dirty (u.a. untracked `odoo_devops_task_bridge.py`) — sichten, nicht blind überschreiben.

## 🆕 Tagesabschluss 2026-07-01 (verifiziert — Fan-Out aller Systeme)

- **frawo-docker-1 = OFFIZIELL STILLGELEGT.** Seit 13 Tagen offline (Tailscale last seen 2026-06-17), SSH timeout. Alle Tasks bereinigt (#586 done, #226/#227/#242/#331/#341/#554 cancelled). Netcup/Flo-Vertrag noch kündigen. n8n migriert auf CT110 (10.1.0.100) ✅. Grafana/Monitoring-Stack noch ausstehend (CT150 ProDesk ist stopped).
- **Odoo-Bereinigung:** 92 Tasks hatten stage=Erledigt aber state=01_in_progress → korrigiert zu 1_done. 14 Tasks stage=Abgebrochen aber state=01_in_progress → korrigiert zu 1_canceled. 3 stale Tageslog-Tasks (#623/#636/#643) geschlossen.
- **⚠️ SPLIT BRAIN RADIO (ungeklärt):** CT130 radio-node (anker-pve, 10.1.0.200) läuft eine zweite AzuraCast-Instanz + frawo-radio-backend + navidrome + funk-community (alle seit 14h = frisch gestartet). Master-AzuraCast = VM210 stockenweiler (10.1.0.38). Zwei Instanzen aktiv — muss geklärt werden ob CT130-Stack absichtlich parallel läuft.
- **⚠️ Unbekanntes Gerät 10.1.0.142** antwortet auf Ping, nicht in Dokumentation. Identifizieren!
- **OpenClaw CT150 (anker-pve):** Läuft und funktioniert. Telegram Bot @Frawo_bot aktiv, Anthropic Haiku-Credits funktionieren. Zugänglich via Tailscale 100.72.154.15. LAN 10.1.0.31 nicht pingbar von StudioPC (PVE-Firewall blockt ICMP, aber Gerät ist im ARP-Cache = erreichbar auf L2).
- **ProDesk unter Last:** Load 7.9 / RAM 434 MB frei / 3.6 GB Swap. Monitoring-Stack CT150 wäre Entlastung (noch stopped).
- **anker-pve Root-Disk: 76% voll** (49/68 GB). Bald handeln.
- **SSOT-Entscheidung (Wolf 2026-07-01):** Odoo = SSOT für alles inkl. Agenten. NOW.md = nur Infra-Live-State. Alle Agenten sollen primär Odoo lesen statt MD-Dateien.

## 🆕 Session 2026-07-16 (verifiziert)
- **Odoo → ServAssi Task-Automatik gebaut:** Task mit Tag "DevOps-Agent" im Backlog → CT150 holt sich das per Poll alle 5 Min (`openclaw-devops-bridge.timer`/`.service`, Script `infra/odoo/odoo_devops_task_bridge.py`), lässt den Agenten ran, schreibt Antwort in den Task-Chatter, markiert per Tag "ServAssi-Ausgeloest" als erledigt (kein Doppel-Verarbeiten). Einzelner kaputter/gelöschter Task killt nicht mehr den ganzen Lauf (try/except pro Task).
- **⚠️ WICHTIG — Push-Webhook (`base.automation` `frawo_agent.automation_servassi_devops_trigger`) ist bewusst DEAKTIVIERT:** Odoo-Host (CT140, 10.1.0.112) kann CT150 (10.1.0.31) auf Host-Ebene zwar erreichen (Anker-LAN-Fix von gestern hält), aber der **Docker-Container `frawotech-web-1` selbst** kommt nach außen zu 10.1.0.31 nicht raus (eigenes Docker-Netzwerk-Problem, nicht weiter untersucht — Poll-Weg ist der Workaround). Nicht wieder aktivieren ohne das Docker-Networking-Problem zu lösen, sonst 5s-Hänger bei jedem Task-Save.
- **⚠️ Lehre — Datei-Drift zwischen Server und Repo:** `addons/frawo_agent/__manifest__.py` und `models/project_task.py` waren auf CT140 direkt bearbeitet worden (nicht übers Repo), und ein bislang ungeklärter Mechanismus hat beide Dateien zwischenzeitlich auf einen älteren Stand zurückgesetzt (project_task.py mtime zeigte 2026-06-25, obwohl an dem Tag noch gar keine Webhook-Methode existierte). Ursache nicht gefunden (kein Git-Repo auf dem Server, kein Cron/Timer der sync't) — im Zweifel nach Server-seitigen Odoo-Addon-Änderungen IMMER direkt zurück ins Repo committen, nicht nur auf dem Server lassen.
- **Lokales Ollama auf CT140 installiert** (`qwen2.5:3b-instruct`, 0.0.0.0:11434) als Notfall-Rückfalloption für den Telegram-Agenten (openclaw `models.providers.ollama-ct140`), da Anthropic-Kontingent bis 2026-08-01 gesperrt und OpenAI ohne Guthaben ist. **Funktioniert aber nicht wirklich** — der volle Agent-Systemprompt (~12-15k Tokens) sprengt selbst mit 16k-Kontext-Modell den Speicher/Kontext auf der kleinen VM (4 GB RAM). Nur technisch verdrahtet, keine echte Lösung. Echte Fixes: OpenAI-Guthaben auffüllen (Wolf) oder auf 1.8. warten (Anthropic-Reset).
- **Odoo-Board-Umbau seit 2026-06-23 hat Projekt-IDs verschoben:** alter Test-Task hatte project_id 35 verloren/umgehängt auf 49, stage_id dabei auf `false` zurückgesetzt (private-task-Falle). Bei künftigen DevOps-Agent-Tasks IMMER project_id 49 ("P4 · 🤖 Automatisierung & KI-Agenten") + stage_id 1 (Backlog) explizit setzen.

## 🆕 Session 2026-06-26 (verifiziert)
- **ServAssi / OpenClaw vollständig aufgerüstet:** CT150 (anker-pve, 10.1.0.31, Tailscale 100.72.154.15) läuft mit neuem Image (git 2.39.5 + gh 2.95.0 baked in). Gateway bind=lan, Port 19000, OPENCLAW_GATEWAY_PASSWORD in .env. Web-UI via SSH-Tunnel `ssh -L 19001:127.0.0.1:19000 root@100.72.154.15` → `http://127.0.0.1:19001`.
- **StudioPC als Node gepairt:** `openclaw node` als Windows Scheduled Task (AtLogon, auto-restart). Passwort `FraWoGateway2026secure` → Vaultwarden eintragen. Node: `fd6bc49e...`, Status: paired·connected·approved.
- **GitHub:** Deploy Key (ed25519, `openclaw@frawo.tech`) in Wolfeetech/FraWo hinterlegt. `gh` CLI mit PAT authentifiziert (PAT im Chat exponiert — bitte rotieren unter github.com/settings/tokens). `GH_TOKEN` in `/opt/openclaw/.env`.
- **Jarvis-Skills:** `claw-vision` + `openai-whisper-api` installiert. Fotos/Sprachmemos an @ServAssi_bot → Odoo-Tasks möglich. OPENAI_API_KEY war bereits in .env.
- **exec-Allowlist:** 20 Tools freigegeben (git, gh, bash, sh, curl, ssh, python3, cat, ls, find, grep, awk, sed, docker etc.).
- **Cron:** Modell auf `anthropic/claude-sonnet-4-6` upgraded (von Haiku).
- **LVM Thin Pool:** Session 2026-06-26 Beginn: war ~54%, Snapshots bereinigt. Rollback-Snapshot Odoo19 gelöscht.
- **OPENCLAW.md:** PR-Workflow-Regeln, Agent-Scope-Tabelle, SSH-Tabelle → live in Container unter `/root/.openclaw/workspace/OPENCLAW.md`.

## 🆕 Tagesabschluss 2026-06-25 (verifiziert)
- **HA-MCP-Lücke gefixt (#608):** Haupt-HA (10.1.0.40) hatte trotz Doku-Behauptung KEINE `mcp_server`-Integration installiert (404 auf `/mcp_server/sse`). Via HA config_entries-Flow-API live nachinstalliert, danach Remote-HA-Verbindung 10.1.0.40↔10.1.0.248 über "Remote Home Assistant"-Integration eingerichtet. **Lehre:** bei `secure`/`verify_ssl` auf Default `true` lassen führt bei plain-HTTP-Zielen zu Verbindungsfehlern → explizit `false` setzen; `max_message_size` braucht `16777216`, nicht leer/`0`.
- **UCG-Netzwerk aufgeräumt (#622/#497):** DHCP-Reservierungen für 16+ Kern-Server, Inter-VLAN-Firewall (IoT/Guest→Server blockiert, Server→IoT erlaubt), AP-Management von Default-VLAN1 (`192.168.1.142`) auf VLAN101 umgezogen, diverse Karteileichen + 2 tote Port-Forwards (80/443→10.1.0.20 "toolbox") entfernt. **Neues Guest-WLAN "FraWo_Gast"** (VLAN105, l2_isolation, nur Internet) angelegt, vollständig isoliert von Lan/Server/IoT/DMZ.
- **IoT-Geräte-Migration läuft (#498/#637):** 8 Geräte von altem Easybox-WLAN "frawo-direkt" (192.168.2.x) auf `FraWo__ioT`(VLAN104) migriert + fest reserviert: `10.4.0.10` Shelly Plug (Kühlschrank), `10.4.0.11` Shelly Outdoor Plug — **KRITISCH: IT/Netzwerk-Strom, niemals remote schalten**, `10.4.0.12` Shelly BLU Gateway G3, `10.4.0.13` Shelly 4-fach/Pro4PM (GrowBox), `10.4.0.14` Roborock Vacuum, `10.4.0.15` Thomson TV, `10.4.0.16` Amazon Fire TV, `10.4.0.17` Google Home Mini (privat). Volle Tabelle: `Desktop/FRAWO Ops/Netzwerk_Soll_Plan_2026-06-25.md`. Noch offen: Govee-Geräte bisher keins aufgetaucht, Soll-Zähler unbekannt.
- **UCG-Zugang:** API-Key-Auth (`X-API-KEY` Header) funktioniert gegen Integration-API UND Legacy-REST-API (`/proxy/network/api/s/default/...`). REST-`DELETE` ist auf diesem Controller gesperrt (404) — Clients werden stattdessen über `cmd/stamgr` mit `{"cmd":"forget-sta","macs":[...]}` entfernt.
- **Tailscale:** Karteileichen `toolbox` + `radio-node-1` gefunden, aber kein API-Key vorhanden → nur manuell über Admin-Konsole entfernbar (Task #638).

## 🆕 Tagesabschluss 2026-06-23/24 (verifiziert)
- **Netz/VLAN-KORREKTUR:** Netz ist sauber VLAN-segmentiert (UCG 10.1.0.1). **`10.4.0.x` = Anker-IoT (VLAN104), NICHT tot!** VLAN101=Server(10.1.0.x), 102 DMZ, 103 DMZ-Radio, 104 IoT, 105 Guest, 110/111 Stockenweiler. Voll-IP-Tabelle = Odoo #622 + Memory `reference_frawo_network_vlan`.
- **Haupt-HA (haos VM210/anker) wieder ONLINE → 10.1.0.40** (statisch VLAN101, DHCP-Reservierung). War auf 10.4.0.24 + NM verklemmt; Fix: static + `qm reboot 210`. HA-Stockenweiler/Eltern = VM360 **10.1.0.248** (MCP-Server gewired).
- **Website frawo.tech:** 6 Security-Header live (A/A+, via CF Transform Rule), Meta-Description/Menü gefixt. Odoo-Stilfehler (Migrations-Asset-Komposition) via `-u web,website` → Backend/Frontend kompilieren sauber.
- **Mail:** Strato von CT140 unerreichbar → **Brevo** ist aktiver SMTP. Angebot S00015 zugestellt.
- **Odoo:** Board restrukturiert (10 Domain-Projekte, Stages, Rollen-Tags, Paten, Mitarbeiter), autonome Automation St.1+2 live (#596). Tageslog/Tagesziele = Task #623.
- **API-Zugänge (lokal, nicht im Repo):** UniFi Cloud + lokaler UCG-Key, CF-API-Token (Transform Rules), HA-Token Stockenweiler + Haupt-HA (seit 25.06.), Odoo-MCP-Key, Tailscale-API-Key (seit 25.06., von Wolf bereitgestellt — Claude-Memory `reference_frawo_tailscale_api`).

## ⚡ Bootstrap für Agenten (Reihenfolge)
0. **[`AGENT_ONBOARDING.md`](AGENT_ONBOARDING.md)** — EIN Prompt um einen komplett neuen Agenten einzuschulen (Identität, Zugänge, Arbeitsweise). Bei Bedarf direkt als Einstiegsprompt kopieren.
1. **Diese `NOW.md`** (Live-Stand + was stale ist).
2. `STATUS.md` (Verlauf), dann bei Bedarf `LIVE_CONTEXT.md` (⚠️ veraltete IPs/Domain — siehe Korrekturen unten).
3. Claude-Memory `project_frawo_2026-06-10_session.md` = bestätigte Topologie-Korrektur.
4. Live verifizieren statt glauben (Tailscale-Status, SSH `frawo-docker-1`).

## 🟢🔴 Live-Status (2026-07-01, vollständig verifiziert)

### PVE-Nodes
| Knoten | Tailscale / LAN-IP | Status | Load / RAM |
|--------|-------------------|--------|------------|
| **proxmox-anker** (Lenovo ThinkCentre) | 100.69.179.87 / 10.1.0.92 | 🟢 ONLINE | 2.86 / 8 GB frei |
| **stockenweiler-pve** (HP ProDesk) | 100.91.20.116 / 10.1.0.128 | 🟢 ONLINE ⚠️ | Load 7.9, RAM 434 MB frei |
| **wolfstudiopc** | 100.98.31.60 / 10.1.0.211 | 🟢 ONLINE | — |
| ~~frawo-docker-1~~ | ~~100.94.32.41~~ | 🔴 **STILLGELEGT** | Seit 13d offline |

### stockenweiler-pve (ProDesk) — CT/VM-Übersicht
| ID | Name | IP | Status | Dienste |
|----|------|----|--------|---------|
| CT101 | adguard | 10.1.0.52 | 🟢 | DNS |
| CT103 | npm (nginx) | 10.1.0.149 | 🟢 | Reverse Proxy |
| CT106 | wireguard | 10.1.0.239 | 🟢 | VPN |
| CT108 | vaultwarden | 10.1.0.95 | 🟢 healthy | Passwort-Manager |
| CT109 | pbs | 10.1.0.7 | ⏹ stopped | Backup Server |
| CT110 | n8n | 10.1.0.100 | 🟢 | n8n + uptime-kuma |
| CT120 | fileserver | 10.1.0.94 | 🟢 | Samba (Musik-Library) |
| CT130 | mail-relay | — | ⏹ stopped | — |
| CT140 | frawotech-web | 10.1.0.112 | 🟢 (30h!) | Odoo 19 + CF-Tunnel |
| CT150 | monitoring-stack | — | ⏹ stopped | Grafana/Prometheus (nie migriert) |
| VM210 | azuracast-vm | 10.1.0.38 | 🟢 | **Master-AzuraCast** |
| VM360 | homeassistant-eltern | 10.1.0.248 | 🟢 | HA Eltern/Testkunden |

### proxmox-anker (Lenovo) — CT/VM-Übersicht
| ID | Name | IP | Status | Dienste |
|----|------|----|--------|---------|
| CT100 | toolbox | — | ⏹ stopped | — |
| CT101 | adguard-slave | 10.1.0.27 | 🟢 | DNS-Slave |
| CT110 | storage-node | 10.1.0.81 | 🟢 | Storage |
| CT130 | radio-node | 10.1.0.200 | 🟢 ⚠️ | azuracast(2.Instanz!), frawo-radio-backend, navidrome, funk-community, uptime-kuma |
| CT150 | openclaw | 10.1.0.31 | 🟢 | @Frawo_bot (Haiku), Tailscale 100.72.154.15 |
| VM210 | haos | 10.1.0.40 | 🟢 | Home Assistant Haupt |
| VM240 | PBS-FraWo | — | 🟢 | Proxmox Backup Server |
| VM220 | odoo (alt) | — | ⏹ stopped | v17 Rollback |
| VM300 | nextcloud | — | ⏹ stopped | — |
| VM330 | paperless | — | ⏹ stopped | — |

### Tailscale-Netz (Stand 2026-07-01)
| Status | Node | IP |
|--------|------|----|
| 🟢 | wolfstudiopc | 100.98.31.60 |
| 🟢 | stockenweiler-pve | 100.91.20.116 |
| 🟢 | proxmox-anker | 100.69.179.87 |
| 🟢 | openclaw-ct150 | 100.72.154.15 |
| 🟢 | radio-node | 100.78.88.33 |
| 🟢 | fileserver-rk | 100.64.130.24 |
| 🟢 | DESKTOP-7LMP02S (wolf-surface?) | 100.79.103.59 |
| 🟢 | Pixel 9 Pro | 100.83.213.17 |
| 🔴 4d | VillaRechner420 | 100.85.153.121 |
| 🔴 3d | wolf-ZenBook | 100.76.249.126 |
| 🔴 10d | surface-go-frontend | 100.106.67.127 |
| 🔴 25d | franz-iphone15 | 100.106.111.38 |
| 🔴 **STILLGELEGT** | ~~frawo-docker-1~~ | ~~100.94.32.41~~ |

## 🧭 Soll-Architektur (bestätigt 2026-07-01)
- **Intern (alles)** → anker-pve + stockenweiler-pve (Rothkreuz). frawo-docker-1 = abgeschrieben.
- **Odoo = SSOT** für alle Mitarbeiter UND Agenten (Tasks, Planung, Entscheidungen).
- **OpenClaw (@Frawo_bot)** = Sekretär/Assistent für Wolf & Franz. Übernimmt alle Bürokratie, Notizen, Aufgaben-Routing.
- **Wolf & Franz** = nur physische Arbeit (verkabeln, bauen, Events). Alles digitale → Agent.
- **Roadmap (3 Ziele):** 1) Radio auf frawo.tech (AzuraCast eingebettet) 2) Professionelle Website 3) Selbstverwaltetes Odoo via Agent.

## ✅ Korrekturen gegenüber älteren Docs (WICHTIG)
- **frawo-docker-1 ist eine VMware-ESXi-VM** (8 vCPU / 31 GB / 200 GB, Host-CPU Xeon Gold 6138), **kein Bare-Metal** „Debian 13, 188G" wie LIVE_CONTEXT sagt. Der **ESXi-Host gehört Flo** (Eigentümer + Administrator der Hardware, ~Zulieferer) und steht in einem **Container auf dem Gelände von Wolfs Eltern** in Stockenweiler (eigenes Internet). Wir haben KEINEN Hardware-Zugriff — nur Mieter-VM. **Eltern = Testkunden** von FraWo (kein Admin/Eigentum).
- **Subnetze (echt):** Rothkreuz = `10.1.0.0/24` (VLAN101: Server, ProDesk, UCG). Anker-IoT = `10.4.0.0/24` (VLAN104: Shelly/Roborock/TVs/Google Home, jetzt mit echten Geräten besetzt seit 25.06., siehe Tagesabschluss oben). Anker-Guest = `10.5.0.0/24` (VLAN105, SSID "FraWo_Gast", seit 25.06.). Stockenweiler-ESXi = `10.30.8.0/24`. **UCG-WAN-Uplink** = `192.168.2.0/24` (Easybox Rothkreuz, korrekt — kein Altlast-Problem, nur die WAN-Seite der UCG; alte Easybox-direkt-WLAN "frawo-direkt" auf diesem Segment wird gerade leergezogen).
- **Domain:** live ist **`frawo.tech`** (Cloudflare). Die ~176 `frawo-tech.de`-Referenzen sind alt → nicht in neuen Code/Configs übernehmen.
- **Drossel-Ursache gelöst:** `frawo-docker-1` (Flo/Stockenweiler) routet allen Internet-Traffic über einen **gedrosselten netcup-VPS-Tunnel** (Gateway `10.30.8.1`, Exit `188.68.45.193`=`exp.tekoda.cloud`, ~150 kbit symmetrisch), NICHT übers Fiber. Deshalb ist alles dort zäh.
- **Odoo-Repatriierung:** Aufgrund der Drosselung wird Odoo nach Rothkreuz auf den ProDesk (`CT 140` / `10.1.0.112`) migriert. Der Cloudflare-Tunnel „FraWo-RK" ist dafür aktiv.

## 🟢 Resolved Blockers (Recent)
- **Odoo-Cutover abgeschlossen**: Der neue Cloudflare-Tunnel „FraWo-RK" läuft stabil in CT 140 und routet Odoo erfolgreich über `frawo.tech`.
- **Radio-Dienste konsolidiert**: VM 210 (`10.1.0.38`) ist als Master-Radiostation definiert und über die Odoo-API (`frawo_agent`) sowie die autonome beets-Ingestion (`curate_radio.py` auf PVE) angebunden.
- **Geräte-Infrastruktur konsolidiert (Option 2)**: Ingress läuft jetzt über den Nginx Proxy Manager auf ProDesk (`CT 103` / `10.1.0.149`). Der veraltete Toolbox-Container (`CT 100` / `100.82.26.53`) ist gestoppt. Das Franz-Portal (`http://10.1.0.149/franz/`) wurde aktualisiert und Nextcloud/Paperless wurden als offline markiert.

## 🔴 Offene Punkte / Sofort-Klärungsbedarf
1. **CT130 radio-node (anker, 10.1.0.200):** Zweite AzuraCast-Instanz läuft dort. Absicht oder Zombie? Klären und ggf. stoppen.
2. **10.1.0.142:** Unbekanntes Gerät im Server-VLAN. Identifizieren (UCG-API oder `arp-scan`).
3. **anker-pve Root-Disk 76% voll** (49/68 GB) → aufräumen bevor es kritisch wird.
4. **ProDesk Last zu hoch** (Load 7.9, RAM 434 MB frei) → monitoring-stack CT150 starten, Ursache finden.
5. **Grafana/Prometheus** → monitoring-stack CT150 (ProDesk) noch nie gestartet nach Migration. Starten oder Entscheidung treffen.
6. **Netcup/Flo VPS-Vertrag kündigen** (frawo-docker-1 Nachfolge abgeschlossen).
7. **Franz Onboarding (#262/#542)** → Franz-iPhone 25 Tage offline, Franz nicht aktiv im System.

---
*Vollständige Bestandsaufnahme (Hardware, Strom, Roadmap): auf dem StudioPC unter `Desktop/FRAWO Ops/Bestandsaufnahme_2026-06-11/`.*

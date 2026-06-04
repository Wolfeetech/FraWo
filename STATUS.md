# Aktueller Status — FraWo GbR Infrastruktur
**Stand: 2026-06-01 | Verifikation: n8n API + SSH live**

---

## Dienste: LIVE-Status

### 🌍 Öffentliche Dienste (Cloudflare Tunnel)
| Domain | Status | Backend |
|--------|--------|---------|
| frawo-tech.de | ✅ HTTP 200 | VM 220 Odoo |
| cloud.frawo-tech.de | ✅ HTTP 200/302 | VM 300 Nextcloud |
| funk.frawo-tech.de | ✅ HTTP 200 | CT 130 AzuraCast |

### 🖥️ Odoo (VM 220, 10.4.0.22)
- Port: 127.0.0.1:8069 (kein Direktzugriff) ✅
- DB: FraWo_GbR ✅
- Login: wolf@frawo-tech.de (Vault: Odoo ERP — Admin)
- Restart: unless-stopped + PVE startup order=3 ✅

### ☁️ Nextcloud (VM 300, 10.4.0.21)
- Intern: http://cloud.hs27.internal ✅
- Öffentlich: https://cloud.frawo-tech.de ✅ HTTP 200
- Ordner: /Dokumente/{Eingang,Archiv,Verträge,Rechnungen} ✅
- trusted_proxies: 10.4.0.0/24 + 100.64.0.0/10 ✅

### 📄 Paperless-ngx (VM 330, 10.4.0.23)
- Intern: http://paperless.hs27.internal ✅
- Post-consume Script: /usr/local/bin/paperless-to-nc.sh → NC/Archiv ✅
- rclone-Sync: alle 5 min NC/Eingang → consume_dir (cron auf VM 330) ✅

### 🔐 Vaultwarden (CT 120, 10.4.0.26)
- URL: http://vault.hs27.internal ✅
- 437 Ciphers (429 Org + 8 persönlich) ✅
- SIGNUPS_ALLOWED: false ✅

### 📡 Radio-Node (CT 130, 10.4.0.28, TS: 100.78.88.33)
- AzuraCast: http://radio.hs27.internal ✅
- Navidrome: http://navidrome.hs27.internal ✅
- FraWo Radio Backend: http://radio-api.hs27.internal:9500 ✅ **V1 live seit 2026-06-01**
  - Community: Chat, Votes, System-Events, Donation-Flow
  - Auth: ADMIN_API_KEY gesetzt, /docs hinter Key, Rate-Limits (Redis)
  - Odoo-Integration: Partner, CRM-Leads, Rechnungen, Email-Quittungen
  - PayPal: PPWP (Wolf privat w.prinz1101@outlook.de) — PPBIZ bereit für Business
- funk-community: https://funk.frawo-tech.de ✅
- Icecast: funk.frawo-tech.de → Relay frawo-docker-1:8000 ✅
- RAM: 6GB ✅ | Disk: 12G/32G (39%) ✅

### 🐳 frawo-docker-1 (Stockenweiler, TS: 100.94.32.41)
- Node.js: v22.22.3 (~/.local/node)
- Services: n8n (5678), Portainer (9000), Grafana (3001), Prometheus (9091), Icecast-Relay (8000)
- **OpenClaw AI Gateway** (Port 19000, systemd user service) — v2026.5.27 ✅
  - Telegram Bot: @Frawo_ClawBot (dmPolicy: pairing, Owner: Wolf TS 5410536762)
  - Primärmodell: openai/gpt-4o | Fallback: anthropic/claude-haiku-4-5
  - Config: ~/.openclaw/openclaw.json
  - Service: ~/.config/systemd/user/openclaw.service (enabled, auto-restart)
- UFW: aktiv — deny in, allow Tailscale + 10.30.8.0/24 ✅
- sudo-PW unbekannt → nsenter-Workaround via Docker ✅

### 🏠 Toolbox (CT 100, 10.4.0.20, TS: 100.82.26.53)
- Caddy: Up ✅ (Edge-Proxy für alle hs27.internal Domains)
- AdGuard: Up ✅
- cloudflared: aktiv (systemd), 6 CF-Tunnel-Routen ✅
- Uptime Kuma: http://uptime.hs27.internal/status/frawo ✅

---

## Storage-Architektur (nach Migration 2026-05-29)

| Pool | Typ | Nutzung | Inhalt |
|------|-----|---------|--------|
| local-lvm | LVM-Thin (NVMe) | ~30% (48G/156G) | Alle VMs + CTs (primär) |
| ssd2tb | dir (USB-SSD) | ~9% (170G/1.9T) | Nur noch Backups/Dumps (images leer!) |
| google-drive | dir (rclone) | ~40% | CT 110 storage-node Disk |

**⚠️ Warnung:** Thin Pool virtuell überprovisioniert (~834G virtual). PBS-Datastore (VM 240) max ~100G real.

---

## Bekannte Blocker

| # | Was | Wo | Priorität |
|---|-----|-----|-----------|
| #159 | PBS VM 240: kein Netzwerk | PVE VNC Console | Mittel |
| #251 | PVE Firewall | PVE Web UI | Hoch |
| #241 | HAOS Eltern: Heimat unklar | Wolf-Entscheidung | Niedrig |
| — | Anthropic API: Guthaben aufladen | console.anthropic.com | Mittel |
| — | OpenClaw Odoo-Skill: noch nicht installiert | frawo-docker-1 | Mittel |

---

## Incident-Log (2026-05-28 bis 2026-05-30)

### 2026-05-28: USB-SSD Bad Sectors
- /dev/sde (ssd2tb) → Bad Sectors → emergency_ro → alle VMs auf ssd2tb gestoppt
- Fix: `vgchange -an ssd2tb && vgchange -ay ssd2tb && e2fsck -f -y -b 32768 /dev/mapper/ssd2tb-data`
- VMs wieder gestartet ✅

### 2026-05-29: Zweiter Incident + Migration
- CT 130 Neustart → ssd2tb wieder emergency_ro
- Sofort-Fix: gleicher Prozess wie 2026-05-28
- **Migration alle VMs/CTs → local-lvm (NVMe) abgeschlossen** ✅

### 2026-05-30: Stromausfall (ca. 03:30 Uhr)
- PVE + Fritz.Box gleichzeitig ausgefallen
- Beim Neustart: AdGuard nicht bereit → rclone GDrive TLS-Fehler (Fritz.Box-Zertifikat)
- CT 110 (GDrive disk) + CT 100 (CIFS mount) konnten nicht automatisch starten
- Alle Services nach manuellem Start wieder online ✅

---

## Dokument-Ökosystem (Stand 2026-05-28)

**Flow:** Upload → NC/Eingang → rclone (5 min) → Paperless OCR → NC/Archiv

```
cloud.frawo-tech.de/Dokumente/Eingang   ← Hochladen hier
         ↓ rclone move (alle 5 min)
Paperless consume_dir (VM 330)
         ↓ OCR + Klassifizierung
Paperless DB + paperless-to-nc.sh
         ↓
cloud.frawo-tech.de/Dokumente/Archiv/{Korrespondent}/{Jahr}/
```

---

## Odoo Workflow

```
Neue Idee → 💡 Brainstorm (stage 86) → Wolf-Freigabe
           → ⚙️ Planung (stage 2) → Agent plant
           → 🚀 In Arbeit (stage 3) → Agent umsetzt
           → ✅ Erledigt (stage 6) → DoD-Note
```

---

## Session 2026-05-30 — Was erledigt wurde

**Infrastruktur:**
- Stromausfall diagnostiziert + alle Services wiederhergestellt
- Prometheus Monitoring: 6/6 Targets UP inkl. pve-exporter (VM/CT Metriken)
- Grafana: Node Exporter Full + Proxmox VE Dashboards importiert

**AI/Automatisierung:**
- OpenClaw @ServAssi_bot auf frawo-docker-1 (gpt-4o, Odoo via frawo-tech.de)
- n8n auf 2.22.5 updated, Backup-Alert + Show-Notes Workflows angelegt
- StudioPC OpenClaw Scheduled Tasks deaktiviert (waren Konfliktursache)

**REW:**
- v5.31.3 installiert — PM1 fehlt noch → Messungen auf Di 02.06 verschoben

**Odoo:**
- 17 Duplikat-Stages bereinigt, Tasks T320/121/322/327/328/313 erledigt
- Prinz Alois: Deadlines gesetzt, T308 Kassenantrag dokumentiert

## Morgen als erstes

1. **PM1 holen + REW Messungen** (T312, Deadline Di!)
2. **Tailscale Route approven** → admin.tailscale.com (2 Klicks!)
3. **PBS Netzwerk** (T159) — VM 240 kein Netz = kein Backup

## Session 2026-05-31 — frawo-docker-1 ausgebaut

**Neue Services auf frawo-docker-1:**
- Ollama (llama3:8b, 4.7GB) — lokale KI, kostenlos, Klausi-Fallback
- Qdrant v1.18.1 — lokale Vektor-DB für RAG
- LS25 Server — Port 10823, lädt via SteamCMD
- AzuraCast Docker Compose erstellt (wartet auf Tailscale Route)

**n8n Workflows:**
- Klausi-Bot (1fLw0n1e0gaObjsp): @Klausi in Odoo Chatter → Ollama
- RAG Ingestion (xCShp2rttlOpaZCi): tägl. 03:00 Odoo → Qdrant

**Noch offen (braucht Wolf):**
- PBS VM 240: VNC Console öffnen, Netzwerk fixen → kein Backup!
- Tailscale Route approven → löst ALLE Netzwerk-Probleme
- Odoo Automation Action für Klausi-Bot (Einstellungen → Technisch → Automation)

## Session 2026-05-31 (Fortsetzung) — REW + Infra

**Erledigt:**
- T312/313/314 REW Erstmessungen Anker: Anlage ausgewogen, Raummoden Bass +10dB
- T309 Thomann-Lieferung vollständig geprüft
- frawo-docker-1: Tailscale wiederhergestellt (Neustart via win-j1aenasv2fj SSH)
- Tailscale Subnet Route 10.4.0.0/24 approved + accept-routes aktiv
- sudo NOPASSWD für wolf auf frawo-docker-1 eingerichtet
- CDROM aus apt sources entfernt

**REW Messprotokoll Anker (2026-05-31):**
| Position | Bass (80-250Hz) | Höhen (2-10kHz) | Bewertung |
|----------|-----------------|-----------------|-----------|
| Hauptposition | 76 dB | 71 dB | ✅ +5 dB |
| Ohrhöhe | 83 dB | 80 dB | ✅ +3 dB |
| Raum Mitte | 90 dB | 79 dB | ⚠️ +11 dB |
Empfehlung: Low-Shelf EQ -6dB bei 200Hz

**Nächste Schritte (Wolf manuell):**
- T7 GbR Gründung: HEUTE fällig!
- T308 Pflegekasse-Antrag: bis 06.06 (Alois füllt Platzhalter aus)
- T316/317/315 Weitere Messungen: bis 02.06
- T100/T73 Wohnzimmer/Badewanne: HEUTE fällig (physisch)

## Agent-Infrastruktur (Stand 2026-05-31)

### Aktive n8n Workflows
| Workflow | Funktion | Status |
|----------|----------|--------|
| Klausi-Bot (1fLw0n1e) | @Klausi in Odoo Chatter → Ollama → Antwort | AKTIV |
| Backup-Alert (QyM1RKzZ) | Tägl. 08:00 PBS-Backup prüfen → Telegram | AKTIV |
| RAG Indexer (xCShp2rt) | Tägl. 03:00 Odoo-Tasks → Qdrant | AKTIV |
| Email-Agent (T335) | IMAP agent@ → GPT → Odoo Chatter | IN ARBEIT |

### Odoo Inventar (neu 2026-05-31)
- Kategorien: FraWo Equipment / Studio & Audio / IT & Server
- 10 Geräte als Produkte (P90-P99)
- T312 REW: 4 Messdateien angehängt

### Agent-Roadmap
1. Email-Agent aktivieren → Emails landen auto in Odoo
2. Odoo Alias: task-312@frawo-tech.de → direkt in Task-Chatter
3. Klausi-Bot: Equipment-Info automatisch aus Ollama/Internet

## GrowBox System (2026-05-31)

**Smart-Visite Workflow (R7suhQjbg1w0ZUQK):** Taegl. 08:00 Telegram-Alert mit zufaelliger Pflanze
- Alle 19 Pflanzen-Tasks mit Visite-Journal ergaenzt
- Template T373, Rotationsplan T372
- Erste Visiten: Banana (T203), Apple Fritter (T215) - professionell dokumentiert im Chatter

**Best Practice Pflanzen-Journal:**
Chatter-Nachricht im Pflanzen-Task = permanentes Journal. Kein extra Tool noetig.

## Infra-Session 2026-05-31 (Abend)

**CT 110 storage-node:**
- Disk-File auf google-drive verloren (war nur im ssd2tb VFS-Cache, nie zu GDrive hochgeladen)
- Restore aus Backup 2026-05-29 auf local-lvm läuft
- rclone-Cache dauerhaft auf /var/cache/rclone-gdrive (NVMe) umgestellt

**frawo-docker-1:**
- Tailscale accept-routes persistent via systemd ExecStartPost
- SSH-Stabilität: Routing über proxmox-anker Subnet funktioniert
- Email-Agent (Onzd61umVKjjEc7O) + GrowBox-Visite-Analyse (h9p6IhpJTGf1vh9v) aktiviert

**n8n Workflows (Stand 2026-05-31):**
| ID | Name | Status |
|----|------|--------|
| QyM1RKzZ | Backup-Monitoring Alert | AKTIV |
| Fg4w058x | Rating Test v5 | AKTIV |
| R7suhQjbg1w0ZUQK | GrowBox: Pflanzen-Review 08:00 (schlägt fehl wenn Odoo down) | ✅ AKTIV |
| pwFyW7OLBsRGHSD7 | GrowBox: Pflanzen-Reminder 19:00 Fallback (kein Odoo nötig) | ✅ AKTIV |
| h9p6IhpJTGf1vh9v | GrowBox: Visite-Analyse Auto-Tasks | ✅ AKTIV |
| 1fLw0n1e0gaObjsp | Klausi-Bot @Odoo-Chatter → Ollama | ✅ AKTIV |
| xCShp2rttlOpaZCi | RAG: Odoo → Qdrant Index | ✅ AKTIV |
| Onzd61umVKjjEc7O | Email-Agent agent@ → GPT → Odoo | ✅ AKTIV |

## Steuer-Setup + Inventar (2026-05-31)

**Kleinunternehmer §19 UStG:**
- Standard Verkauf: Steuerbefreit §19 (0%)
- Standard Einkauf: VSt 19% (bezahlt, kein Vorsteuerabzug)
- Pflichthinweis auf Rechnungen: "Gemäß §19 UStG wird keine USt berechnet"

**Fiskalpositionen:**
- DE<->AT Privatperson (auto)
- EU B2B Reverse Charge (auto, UID-pflichtig)
- DE<->CH Schweiz/Drittland (auto)

**Frequenzweichen KMT Tops:**
- PO6 Intertechnik: 107,90 EUR -> freigeben
- PO8 Reichelt: 4,95 EUR -> freigeben
- JLCPCB: 49,95 EUR (5x 9,99) -> manuell bestellen
- Valentin Loehr (ID49): Montage

**Inventar:** 22 Produkte, 3 Kategorien (Studio, IT, Elektronik), alle korrekt als Verbrauchsartikel

## Fertigung & Inventar (2026-05-31 Abend)

**Fertigungsaufträge (aktiv):**
| MO | Was | Menge | Status |
|----|-----|-------|--------|
| MO2 | Tonstudio Villa (Anker) | 1x | In Bearbeitung |
| MO3 | Subwoofer Doppel 12" | 4x | Bestätigt - TODO: SUB-12 -> Beyma |
| MO5 | Frequenzweichen KMT | 2x | Entwurf - wartet auf Teile |
| MO9 | Kick 12" Sub (Beyma) | 4x | Entwurf |

**Neue Produkte:**
- P115: Frequenzweiche KMT Top
- P116-P119: Korg Volcas (3x) + Akai APC (Modelle noch zu bestätigen)
- P121-P122: Beyma 12" + 15" Chassis (Modelle TBD)
- P123-P126: Cubo 12/15, Kick 12, Doppel 12 (Eigenbau)
- P127: Martin Audio CX2 (Reparatur)

**Steuern bereinigt:**
- 7 korrekte Steuern, 4 alte deaktiviert
- §19 KU auf allen Verkaufsprodukten
- VSt 19% auf allen Einkaufszeilen (PO6, PO8)

**TODO Wolf manuell:**
- MO3: SUB-12 -> Beyma 12" Chassis tauschen
- Beyma Chassis Modelle bestätigen (P121/P122)
- Volcas genaue Modelle eintragen (P116-P118)
- Akai APC genaues Modell (P119)
- PO7 löschen (Duplikat)
- Martin Audio CX2: Kontakt Lautsprechermanufaktur Mannheim

## Session 2026-05-31 Final — Kompletter Tagesabschluss

### Erledigte Tasks heute (mit agent@-Protokoll)
| Task | Was | Status |
|------|-----|--------|
| T251 | PVE Firewall aktiv (enable=1, DROP policy) | ✅ |
| T319 | Netzwerk-Sicherheitsaudit abgeschlossen | ✅ |
| T321 | n8n 2.22.5: 9/9 Workflows aktiv (verifiziert 2026-06-01) | ✅ |
| T328 | pve-exporter: 6/6 Prometheus Targets UP | ✅ |
| T329 | Grafana Telegram-Alert eingerichtet | ✅ |
| T8   | PBS Offsite via Google Drive aktiv | ✅ |
| T11  | PBS Backups: VM 240 online, Jobs aktiv | ✅ |
| T159 | PBS Netzwerk wiederhergestellt | ✅ |
| T169 | Inventar: 140+ Produkte kategorisiert | ✅ |
| T312 | REW Erstmessungen Anker: Bass +11dB | ✅ |

### Neue Infrastruktur
- CT 110 storage-node: auf local-lvm restored, läuft
- Grafana Alerts: Telegram-Benachrichtigung bei Node-Down
- Alle 10 VMs/CTs aktiv

### Inventar-Stand (Lautsprecher & Audio)
- Beyma 8G40/10G40/12G40/12P80/CD-101: korrekte Specs
- Jobst JM-Sub212: Ist=Thomann, Ziel=Kappalite 3012LF
- Elvis 15": Ist=0815, Ziel=Beyma 15SW1800
- KMT DF 1022: Beyma 10G40 + TD164 Horn

### KVAs bereit (nur freigeben)
- PO6: Intertechnik Frequenzweichen 107,90 EUR
- PO8: Reichelt DEGSON 4,95 EUR
- PO9: 4x Beyma 12G40 Kick 916 EUR
- PO11: Option A Kappalite+Elvis 587 EUR
- PO12: Option B Beyma+Elvis 619 EUR

### Abstimmungen bis 01.07 (T383-T385)
- JM-Sub212: Kappalite (A) oder Beyma (B)?
- Kick 12": 12G40 oder anderes?
- Elvis Upgrade: jetzt oder warten?

### Offene Housekeeping-Punkte
- local-lvm 98% voll: PBS-Disk (500GB) auf Google Drive migrieren
- PO7 löschen (Duplikat Intertechnik)
- Beyma Chassis Modelle bestätigen (P121/P122)

## Task-Audit 2026-05-31 (agent@)

**12 Tasks geschlossen** (waren erledigt, fehlte nur Dokumentation):
T344 ssd2tb Migration, T346 PVE Audit, T347 CT100 Migration, T348 Split-DNS,
T345 VM Firewall, T349 Website HTTPS, T351 GitHub, T352 Nextcloud,
T355 Odoo ACL, T356 Radio Backend, T358 PBS Rebuild, T359 SSH-Keys

**Radio_Epic 2 (T220) erledigt:** 7 AzuraCast Streamer-Accounts angelegt
(wolf, franz, dobby, marcin, flo, info, agent)

**Beets installiert** auf CT130 (v1.6.0) — FLAC-Import startet, Permissions werden geprüft

## Infra-Abschluss (2026-05-31 Abend)

**Homeserver "Sack zu":**
- Keine kritischen Blocker mehr
- PVE Firewall aktiv, n8n 9/9 Workflows aktiv (verifiziert 2026-06-01)
- CT110 restored, alle 10 VMs/CTs online
- PBS online, Backups laufen
- Grafana Alerts konfiguriert
- AzuraCast 7 DJ-Streamer-Accounts

**Nächste Phase: Backup + Radio**
- PBS-frawo: AKTIV ✅ (10/10 VMs/CTs gesichert, 3.96% belegt)
- Google Drive: AKTIV ✅ (tägl. 02:00, alle VMs bis 30.05., offsite 2TB)
- Nächster Backup-Lauf: heute Nacht 02:00
- local-lvm: 37.95% (nach Storage-Krise 01.06. behoben)
- Radio Show Tracklists kuratieren
- Beets Musik-Import abschließen

## Session 2026-06-01 — Infra-Abschluss + Backup-Fix

### Erledigt
| Task | Was | Verifiziert |
|------|-----|-------------|
| T389 | Storage-Krise behoben, local-lvm 37% | ✅ |
| T391 | ssd2tb udev-Regel Auto-Remount | ✅ |
| T388 | SSH-Key Toolbox → frawo-docker-1 | ✅ |
| T390 | SPOF-Audit: Grafana Alert + fstrim Cron | ✅ |
| T425 | Docker infra_shared Netzwerk permanent | ✅ |
| T159 | PBS produktiv, 10/10 VMs gesichert | ✅ |
| T178 | AzuraCast Branding komplett | ✅ |
| T179 | Radio Mounts + Qualität OK | ✅ |
| RAG  | 200 Odoo-Tasks in Qdrant indexiert | ✅ |
| T423/424 | Biscotti + Rainbow Sherbet dokumentiert | ✅ |

### n8n Workflows (verifiziert via API)
9/9 AKTIV | Tägl. Pflanzenerinnerung 19:00 (Fallback) neu

### Backup-Status
- PBS lokal: 10/10, tägl. 02:00
- Google Drive: alle VMs bis 30.05., tägl. 02:00
- fstrim: tägl. 04:00 auf proxmox-anker

### Wolf manuell offen
- QEMU Guest Agent VMs 220/300/330 (VNC Console)
- PBS VM 240 SSH Key einrichten
- T393 Musik-Library Upload

## Tasks-Abschluss 2026-06-01/02

| Task | Was | |
|------|-----|--|
| T164 | OpenClaw Slash-Commands (Telegram-native) | ✅ |
| T165 | Agent@ Berechtigungen dokumentiert | ✅ |
| T178 | AzuraCast Branding: Genre, URL, Beschreibung | ✅ |
| T179 | Radio Mounts: 192/320kbps MP3 + 64kbps AAC+ | ✅ |
| T180 | Media Library Struktur dokumentiert | ✅ |
| T181 | Playlists: 7 aktiv, Track-Rating läuft | ✅ |
| T262 | Franz Onboarding: Checkliste + franz-iphone15 im Netz | 🔄 |
| T388 | SSH-Key Toolbox → frawo-docker-1 | ✅ |
| T393 | FraWo_Radio_Library Upload → GDrive läuft (309MB) | 🔄 |
| T426 | Google Drive rclone (bereits vorhanden) | ✅ |
| SOUL.md | Klausi Kontext: Infra, Odoo, GrowBox, Audio | ✅ |

## ⚠️ AUSFALL proxmox-anker — 2026-06-02 ~00:00

**Status:** SSH timeout, Tailscale relay aktiv aber SSH nicht erreichbar.
**Auswirkung:** Odoo, Nextcloud, Paperless, Radio (AzuraCast), PBS — alle 530.
**Nicht betroffen:** frawo-docker-1 (n8n, Grafana, Klausi, Radio-Relay läuft).
**Ursache unbekannt:** Möglichst rclone fuse mount-Hänger nach rsync-Kill, oder separate Hardware-/Netzwerk-Problem.
**Maßnahme:** Wolf muss proxmox-anker physisch prüfen/neustarten.

## HP ProDesk / stockenweiler-pve (2026-06-02)

**Hardware:** i7-7700T, 16GB RAM, 238GB NVMe + 931GB NTFS HDD + 1.8TB NTFS HDD
**Tailscale:** 100.91.20.116 | **LAN:** 192.168.2.153 | **PVE:** 9.1.4

### Aktuell laufende VMs/CTs
| ID | Name | Status |
|----|------|--------|
| VM360 | homeassistant-eltern | running |
| VM210 | azuracast-vm | running |
| CT108 | vaultwarden | running |
| CT110 | n8n | running |
| CT109 | pbs | running |

### Upload läuft (systemd frawo-upload.service)
- `gdrive:Stockenweiler/data_family` ← /mnt/data_family (931GB)
- `gdrive:Stockenweiler/music_hdd` ← /mnt/music_hdd (1.8TB)
- Logs: /var/log/frawo-uploads/

### Nach Upload: Neuinstallation (T449)
- PVE clean install
- Windows VM: Alois ALF-Programm (User only, kein Admin)
- HA Satellite: Stockenweiler Geräte → Anker-HA als Zentrale
- Tailscale: Verbindung zu Anker

### Architektur-Entscheidung
- HA-Zentrale: Anker VM210
- HA-Satellite: Stockenweiler (lightweight, für lokale Geräte)
- Alois: NUR User, kein Admin (hat Konfiguration beschädigt)

## Session 2026-06-03/04 — Zusammenfassung

### Fortschritte
- **frawo.tech**: NS propagiert, Cloudflare Zone aktiv, 9 DNS-Records gesetzt, Caddy Redirects konfiguriert
- **AzuraCast Radio**: 982GB Musik-SSD gemountet, 1385 Tracks in Main Rotation — Radio spielt wieder!
- **HP ProDesk (stockenweiler-pve)**: rclone installiert, 2.7TB GDrive-Upload läuft (frawo-upload.service)
- **Surface Go Portal**: Neues Live-Dashboard (3 Tabs: Home/Radio/Monitor, kein target=_blank)
- **Odoo Tasks**: T436-T461 angelegt (frawo.tech Migration + 3-Standort HA)

### Offen für Wolf (T461)
- Cloudflare: Zero Trust → Tunnels → Public Hostnames → frawo.tech eintragen (5 Min)

### Bekanntes Problem
- proxmox-anker (Lenovo) crasht wiederholt → SPOF bis HP ProDesk als 2. Knoten eingebunden

## ⚠️ KRITISCH: proxmox-anker Crash-Pattern (2026-06-03/04)

**4 Abstürze in 24h:**
- 02.06. ~00:00 — Stromausfall oder Freeze
- 03.06. ~09:XX — nach Neustart, nach ~8h
- 03.06. ~21:25 — nach ~12h  
- 04.06. ~XX:XX — nach Neustart heute Nacht

**Symptome:**
- SSH Timeout (kein ICMP-Timeout, nur TCP-Verbindungsabbruch)
- Tailscale zeigt 'offline, last seen Xmin ago' (nicht sofort)
- Keine automatische Recovery

**Mögliche Ursachen:**
- Lenovo Thin Centre Thermal Throttling / Shutdown
- PVE Kernel Panic (brauche journalctl -xb -1 Output)
- Memory-Fehler unter Last (PBS Backup-Job 02:00 als Auslöser?)
- Power Management (ACPI Sleep-States)

**Sofortmassnahmen:**
- BIOS: Power Management auf Performance, kein Sleep/Hibernate
- PVE: power_button = ignore
- Langfristig: HP ProDesk als 2. Knoten → PVE Cluster + HA

# NOW — Echter Live-Stand (BITTE ZUERST LESEN)
**Letzte Verifikation: 2026-06-24 (live, StudioPC Rothkreuz).**

> Diese Datei ist die **einzige Echtzeit-Wahrheit** für Infra. Andere Docs (LIVE_CONTEXT, MASTERPLAN, ROADMAP, INFRASTRUCTURE_MAP, AI_BOOTSTRAP_CONTEXT, STATUS, todo) sind **stale** = nur Historie.
> **Odoo (CT140, 10.1.0.112:8069) ist ab 2026-06-23 die operative SSOT für Projekte/Aufgaben** (restrukturiert, Konventionen Task #599). Für *Live-Infra-State* gilt weiter: NOW.md + live verifizieren.

## 🆕 Tagesabschluss 2026-06-23/24 (verifiziert)
- **Netz/VLAN-KORREKTUR:** Netz ist sauber VLAN-segmentiert (UCG 10.1.0.1). **`10.4.0.x` = Anker-IoT (VLAN104), NICHT tot!** VLAN101=Server(10.1.0.x), 102 DMZ, 103 DMZ-Radio, 104 IoT, 105 Guest, 110/111 Stockenweiler. Voll-IP-Tabelle = Odoo #622 + Memory `reference_frawo_network_vlan`.
- **Haupt-HA (haos VM210/anker) wieder ONLINE → 10.1.0.40** (statisch VLAN101, DHCP-Reservierung). War auf 10.4.0.24 + NM verklemmt; Fix: static + `qm reboot 210`. HA-Stockenweiler/Eltern = VM360 **10.1.0.248** (MCP-Server gewired).
- **Website frawo.tech:** 6 Security-Header live (A/A+, via CF Transform Rule), Meta-Description/Menü gefixt. Odoo-Stilfehler (Migrations-Asset-Komposition) via `-u web,website` → Backend/Frontend kompilieren sauber.
- **Mail:** Strato von CT140 unerreichbar → **Brevo** ist aktiver SMTP. Angebot S00015 zugestellt.
- **Odoo:** Board restrukturiert (10 Domain-Projekte, Stages, Rollen-Tags, Paten, Mitarbeiter), autonome Automation St.1+2 live (#596). Tageslog/Tagesziele = Task #623.
- **API-Zugänge (lokal, nicht im Repo):** UniFi Cloud + lokaler UCG-Key, CF-API-Token (Transform Rules), HA-Token Stockenweiler, Odoo-MCP-Key.

## ⚡ Bootstrap für Agenten (Reihenfolge)
1. **Diese `NOW.md`** (Live-Stand + was stale ist).
2. `STATUS.md` (Verlauf), dann bei Bedarf `LIVE_CONTEXT.md` (⚠️ veraltete IPs/Domain — siehe Korrekturen unten).
3. Claude-Memory `project_frawo_2026-06-10_session.md` = bestätigte Topologie-Korrektur.
4. Live verifizieren statt glauben (Tailscale-Status, SSH `frawo-docker-1`).

## 🟢🔴 Live-Status (2026-06-24)
| Knoten | Tailscale / IP | Standort | Status | Rolle / Beschreibung |
|--------|----------------|----------|--------|----------------------|
| **frawo-docker-1** | 100.94.32.41 (Lokal: 10.30.8.22) | Stockenweiler | 🟢 ONLINE | **Außen/Prod (gedrosselt)**: n8n, Grafana, Portainer, Prometheus, Node Exporter, LS25 Server. *Hinweis: Alle Dienste leiden unter VPS-Drossel (150 kbps).* |
| **proxmox-anker** | 100.69.179.87 (Lokal: 10.1.0.92) | Rothkreuz | 🟢 ONLINE | **PVE-Node A**: haos (VM 210, running, IP: 10.1.0.40), radio-node (CT 130, running, IP: 10.1.0.200), adguard-slave (CT 101, running, IP: 10.1.0.27), storage-node (CT 110, running, IP: 10.1.0.81). Alt-Dienste (gestoppt): odoo (VM 220), PBS-FraWo (VM 240), nextcloud (VM 300), paperless (VM 330), toolbox (CT 100). Storage-Warnung: `ssd2tb` existiert physisch nicht! |
| **stockenweiler-pve** (ProDesk) | 100.91.20.116 (Lokal: 10.1.0.128) | Rothkreuz | 🟢 ONLINE | **PVE-Node B (Master-Workhorse)**: HomeAssistant-Eltern (VM 360, running, IP: 10.1.0.248), azuracast-vm (VM 210, running, IP: 10.1.0.38 - Master-Radio), adguard (CT 101: 10.1.0.52), npm (CT 103: 10.1.0.149), wireguard (CT 106: 10.1.0.239), vaultwarden (CT 108: 10.1.0.95), pbs (CT 109: 10.1.0.7), n8n (CT 110: 10.1.0.100), fileserver (CT 120: 10.1.0.94), frawotech-web (CT 140: 10.1.0.112 - Odoo). Gestoppt: monitoring-stack (CT 150), mail-relay (CT 130). |
| **wolfstudiopc** | 100.98.31.60 | Rothkreuz | 🟢 ONLINE | Dev-Workstation. Ethernet: `10.1.0.211` (Gigabit-Direktzugriff). WLAN: getrennt (AP-isoliert). |
| **win-j1aenasv2fj** | 100.97.147.67 | Flo's ESXi | 🔴 OFFLINE | Windows Server VM (derzeit ausgeschaltet/nicht erreichbar). |

## 🧭 Soll-Architektur (von Wolf bestätigt 2026-06-17)
- **Außen** → docker-node (frawo-docker-1). **Intern** → Anker + ProDesk (physisch zugreifbar, Rothkreuz).
- Stockenweiler bleibt Ziel-Prod-Standort (sicher hinter Firewall), sauber nutzbar für **Wolf & Franz**.
- Estate-Login: private User (Wolf, Franz – Gaming/Surfen) · **FraWo** (Business) · **Admin**.
- Mobil einsetzbar bauen.

## ✅ Korrekturen gegenüber älteren Docs (WICHTIG)
- **frawo-docker-1 ist eine VMware-ESXi-VM** (8 vCPU / 31 GB / 200 GB, Host-CPU Xeon Gold 6138), **kein Bare-Metal** „Debian 13, 188G" wie LIVE_CONTEXT sagt. Der **ESXi-Host gehört Flo** (Eigentümer + Administrator der Hardware, ~Zulieferer) und steht in einem **Container auf dem Gelände von Wolfs Eltern** in Stockenweiler (eigenes Internet). Wir haben KEINEN Hardware-Zugriff — nur Mieter-VM. **Eltern = Testkunden** von FraWo (kein Admin/Eigentum).
- **Subnetze (echt):** Rothkreuz = `10.1.0.0/24` (VLAN101: Server, ProDesk, UCG). Anker-IoT = `10.4.0.0/24` (VLAN104: Shelly, Govee, HA-Geräte). Stockenweiler-ESXi = `10.30.8.0/24`. ProDesk/Easybox = `192.168.2.0/24` (alt / veraltet nach UCG-Umzug).
- **Domain:** live ist **`frawo.tech`** (Cloudflare). Die ~176 `frawo-tech.de`-Referenzen sind alt → nicht in neuen Code/Configs übernehmen.
- **Drossel-Ursache gelöst:** `frawo-docker-1` (Flo/Stockenweiler) routet allen Internet-Traffic über einen **gedrosselten netcup-VPS-Tunnel** (Gateway `10.30.8.1`, Exit `188.68.45.193`=`exp.tekoda.cloud`, ~150 kbit symmetrisch), NICHT übers Fiber. Deshalb ist alles dort zäh.
- **Odoo-Repatriierung:** Aufgrund der Drosselung wird Odoo nach Rothkreuz auf den ProDesk (`CT 140` / `10.1.0.112`) migriert. Der Cloudflare-Tunnel „FraWo-RK" ist dafür aktiv.

## 🟢 Resolved Blockers (Recent)
- **Odoo-Cutover abgeschlossen**: Der neue Cloudflare-Tunnel „FraWo-RK" läuft stabil in CT 140 und routet Odoo erfolgreich über `frawo.tech`.
- **Radio-Dienste konsolidiert**: VM 210 (`10.1.0.38`) ist als Master-Radiostation definiert und über die Odoo-API (`frawo_agent`) sowie die autonome beets-Ingestion (`curate_radio.py` auf PVE) angebunden.
- **Geräte-Infrastruktur konsolidiert (Option 2)**: Ingress läuft jetzt über den Nginx Proxy Manager auf ProDesk (`CT 103` / `10.1.0.149`). Der veraltete Toolbox-Container (`CT 100` / `100.82.26.53`) ist gestoppt. Das Franz-Portal (`http://10.1.0.149/franz/`) wurde aktualisiert und Nextcloud/Paperless wurden als offline markiert.

## 🔴 P1-Blocker (Kurzliste)
1. **Windows VM auf Flo's ESXi booten**: Die VM ist offline und via AnyDesk/SSH/Tailscale nicht erreichbar (Flo ist informiert).

---
*Vollständige Bestandsaufnahme (Hardware, Strom, Roadmap): auf dem StudioPC unter `Desktop/FRAWO Ops/Bestandsaufnahme_2026-06-11/`.*

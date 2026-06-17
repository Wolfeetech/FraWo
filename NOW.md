# NOW — Echter Live-Stand (BITTE ZUERST LESEN)
**Letzte Verifikation: 2026-06-16 (live gemessen vom StudioPC in Rothkreuz).**

> Diese Datei ist die **einzige Echtzeit-Wahrheit** für jeden Agenten/Menschen.
> Alle anderen Docs (LIVE_CONTEXT, MASTERPLAN, ROADMAP, INFRASTRUCTURE_MAP, AI_BOOTSTRAP_CONTEXT) sind **älter und teils stale** — als Architektur-/Historie-Referenz nutzen, NICHT als aktuellen Zustand.
> **Odoo ist KEINE verlässliche Infra-Infoquelle.**

## ⚡ Bootstrap für Agenten (Reihenfolge)
1. **Diese `NOW.md`** (Live-Stand + was stale ist).
2. `STATUS.md` (Verlauf), dann bei Bedarf `LIVE_CONTEXT.md` (⚠️ veraltete IPs/Domain — siehe Korrekturen unten).
3. Claude-Memory `project_frawo_2026-06-10_session.md` = bestätigte Topologie-Korrektur.
4. Live verifizieren statt glauben (Tailscale-Status, SSH `frawo-docker-1`).

## 🟢🔴 Live-Status (2026-06-16)
| Knoten | Tailscale / IP | Standort | Status | Rolle / Beschreibung |
|--------|----------------|----------|--------|----------------------|
| **frawo-docker-1** | 100.94.32.41 (Lokal: 10.30.8.22) | Stockenweiler | 🟢 ONLINE | **Außen/Prod (gedrosselt)**: n8n, Grafana, Portainer, Prometheus, Node Exporter, LS25 Server. *Hinweis: Alle Dienste leiden unter VPS-Drossel (150 kbps).* |
| **proxmox-anker** | 100.69.179.87 (Lokal: 10.1.0.92) | Rothkreuz | 🟢 ONLINE | **PVE-Node A**: haos (VM 210, running), odoo (VM 220, running), adguard-slave (CT 101, running), storage-node (CT 110, running). Storage-Warnung: `ssd2tb` existiert physisch nicht! |
| **stockenweiler-pve** (ProDesk) | 100.91.20.116 (Lokal: 10.1.0.128) | Rothkreuz | 🟢 ONLINE | **PVE-Node B (Master-Workhorse)**: HomeAssistant-Eltern (VM 360, running), adguard (CT 101: 10.1.0.52), npm (CT 103: 10.1.0.149), wireguard (CT 106), vaultwarden (CT 108: 10.1.0.95), pbs (CT 109), n8n (CT 110: 10.1.0.100), fileserver (CT 120: 10.1.0.94), frawotech-web (CT 140: 10.1.0.112 - Odoo). |
| **wolfstudiopc** | 100.98.31.60 | Rothkreuz | 🟢 ONLINE | Dev-Workstation. Ethernet: `10.1.0.x` (Gigabit-Direktzugriff). WLAN: `192.168.2.x` (AP-isoliert). |
| **win-j1aenasv2fj** | 100.97.147.67 | Flo's ESXi | 🔴 OFFLINE | Windows Server VM (derzeit ausgeschaltet/nicht erreichbar). |

## 🧭 Soll-Architektur (von Wolf bestätigt 2026-06-16)
- **Außen** → docker-node (frawo-docker-1). **Intern** → Anker + ProDesk (physisch zugreifbar, Rothkreuz).
- Stockenweiler bleibt Ziel-Prod-Standort (sicher hinter Firewall), sauber nutzbar für **Wolf & Franz**.
- Estate-Login: private User (Wolf, Franz – Gaming/Surfen) · **FraWo** (Business) · **Admin**.
- Mobil einsetzbar bauen.

## ✅ Korrekturen gegenüber älteren Docs (WICHTIG)
- **frawo-docker-1 ist eine VMware-ESXi-VM** (8 vCPU / 31 GB / 200 GB, Host-CPU Xeon Gold 6138), **kein Bare-Metal** „Debian 13, 188G" wie LIVE_CONTEXT sagt. Der **ESXi-Host gehört Flo** (Eigentümer + Administrator der Hardware, ~Zulieferer) und steht in einem **Container auf dem Gelände von Wolfs Eltern** in Stockenweiler (eigenes Internet). Wir haben KEINEN Hardware-Zugriff — nur Mieter-VM. **Eltern = Testkunden** von FraWo (kein Admin/Eigentum).
- **Subnetze (echt):** Rothkreuz = `10.1.0.0/24` (Anker-Server, ProDesk, UCG). Stockenweiler-ESXi = `10.30.8.0/24`. ProDesk/Easybox = `192.168.2.0/24` (alt / veraltet nach UCG-Umzug). → Alle `10.4.0.x`-Angaben in LIVE_CONTEXT/MASTERPLAN sind **veraltet**.
- **Domain:** live ist **`frawo.tech`** (Cloudflare). Die ~176 `frawo-tech.de`-Referenzen sind alt → nicht in neuen Code/Configs übernehmen.
- **Drossel-Ursache gelöst:** `frawo-docker-1` (Flo/Stockenweiler) routet allen Internet-Traffic über einen **gedrosselten netcup-VPS-Tunnel** (Gateway `10.30.8.1`, Exit `188.68.45.193`=`exp.tekoda.cloud`, ~150 kbit symmetrisch), NICHT übers Fiber. Deshalb ist alles dort zäh.
- **Odoo-Repatriierung:** Aufgrund der Drosselung wird Odoo nach Rothkreuz auf den ProDesk (`CT 140` / `10.1.0.112`) migriert. Der Cloudflare-Tunnel „FraWo-RK" ist dafür aktiv.

## 🔴 P1-Blocker (Kurzliste)
1. **Windows VM auf Flo's ESXi booten**: Die VM ist offline und via AnyDesk/SSH/Tailscale nicht erreichbar (Flo ist informiert).
2. **Odoo-Cutover abschließen**: DNS-Einträge auf den neuen Cloudflare-Tunnel „FraWo-RK" umschreiben, sobald Odoo-Repatriierung fertig verifiziert ist.
3. **Radio-Dienste konsolidieren**: Abstimmung zwischen VM210 (Anker) und CT141 (azuracast-rk auf ProDesk) für die Master-Radiostation.

---
*Vollständige Bestandsaufnahme (Hardware, Strom, Roadmap): auf dem StudioPC unter `Desktop/FRAWO Ops/Bestandsaufnahme_2026-06-11/`.*

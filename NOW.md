# NOW — Echter Live-Stand (BITTE ZUERST LESEN)
**Letzte Verifikation: 2026-06-11 (live gemessen vom StudioPC in Rothkreuz).**

> Diese Datei ist die **einzige Echtzeit-Wahrheit** für jeden Agenten/Menschen.
> Alle anderen Docs (LIVE_CONTEXT, MASTERPLAN, ROADMAP, INFRASTRUCTURE_MAP, AI_BOOTSTRAP_CONTEXT) sind **älter und teils stale** — als Architektur-/Historie-Referenz nutzen, NICHT als aktuellen Zustand.
> **Odoo ist KEINE verlässliche Infra-Infoquelle.**

## ⚡ Bootstrap für Agenten (Reihenfolge)
1. **Diese `NOW.md`** (Live-Stand + was stale ist).
2. `STATUS.md` (Verlauf), dann bei Bedarf `LIVE_CONTEXT.md` (⚠️ veraltete IPs/Domain — siehe Korrekturen unten).
3. Claude-Memory `project_frawo_2026-06-10_session.md` = bestätigte Topologie-Korrektur.
4. Live verifizieren statt glauben (Tailscale-Status, SSH `frawo-docker-1`).

## 🟢🔴 Live-Status (2026-06-11)
| Knoten | Tailscale / IP | Standort | Status | Rolle |
|--------|----------------|----------|--------|-------|
| frawo-docker-1 | 100.94.32.41 (ESXi-VM, 10.30.8.22) | Stockenweiler | 🟢 ONLINE | **Außen/Prod**: Odoo (frawo.tech ✅ HTTP 200), Nextcloud, Paperless, n8n, Grafana, Portainer, Ollama, Qdrant, cloudflared |
| proxmox-anker | 100.69.179.87 / 10.1.0.92 | Rothkreuz | 🔴 EMERGENCY-MODE | **Intern**: Proxmox (radio-node, Vaultwarden, toolbox/Caddy). Boot hängt am 2TB-SSD-Mount (fstab ohne `nofail`). |
| ProDesk „Stocki" | 100.91.20.116 | Rothkreuz (Easybox) | 🔴 OFFLINE — 11.06. ganzes Easybox-Netz gescannt: **kein Lebenszeichen** (bootet nicht durch ODER kein LAN-Link). Vor-Ort-Check nötig. | künftig **NAS + HomeAssistant-Eltern** (Eltern = Raspberry-Pi-Außenposten) |
| radio-node / toolbox | 100.78.88.33 / 100.82.26.53 | Rothkreuz | 🔴 DOWN | hängen an Anker → Radio/funk, Navidrome, Vaultwarden, internes DNS aus |
| wolfstudiopc | 100.98.31.60 | Rothkreuz | 🟢 ONLINE | Ops/Dev, dual-homed: Eth 10.1.0.210 (UCG) + WLAN 192.168.2.132 (Easybox) |

## 🧭 Soll-Architektur (von Wolf bestätigt 2026-06-11)
- **Außen** → docker-node (frawo-docker-1). **Intern** → Anker + ProDesk (physisch zugreifbar, Rothkreuz).
- Stockenweiler bleibt Ziel-Prod-Standort (sicher hinter Firewall), sauber nutzbar für **Wolf & Franz**.
- Estate-Login: private User (Wolf, Franz – Gaming/Surfen) · **FraWo** (Business) · **Admin**.
- Mobil einsetzbar bauen.

## ✅ Korrekturen gegenüber älteren Docs (WICHTIG)
- **frawo-docker-1 ist eine VMware-ESXi-VM** (8 vCPU / 31 GB / 200 GB, Host-CPU Xeon Gold 6138), **kein Bare-Metal** „Debian 13, 188G" wie LIVE_CONTEXT sagt. Der **ESXi-Host gehört Flo** (Eigentümer + Administrator der Hardware, ~Zulieferer) und steht in einem **Container auf dem Gelände von Wolfs Eltern** in Stockenweiler (eigenes Internet). **Wir haben KEINEN Hardware-Zugriff** — nur Mieter-VM. **Eltern = Testkunden** von FraWo (kein Admin/Eigentum).
- **Subnetze (echt):** Rothkreuz = `10.1.0.0/24` (Anker-Server, anker=10.1.0.92) + `10.3.0.0/24` (Radio-DMZ, isoliert). Stockenweiler-ESXi = `10.30.8.0/24`. ProDesk/Easybox = `192.168.2.0/24`. → Alle `10.4.0.x`-Angaben in LIVE_CONTEXT/MASTERPLAN sind **veraltet**.
- **Domain:** live ist **`frawo.tech`** (Cloudflare). Die ~176 `frawo-tech.de`-Referenzen sind alt → nicht in neuen Code/Configs übernehmen.
- **Repo-Hygiene:** `DOCS/` und `docs/` kollidieren auf Windows (Case) → bereinigen.
- Anker-/ProDesk-Hardware-Modelle sind **unbestätigt** (nach Boot per `dmidecode` auslesen).

## 🔴 P1-Blocker (Kurzliste)
1. Anker aus Emergency-Mode (SSD dran → `reboot` → dann `nofail`-Mount).
2. ProDesk headless ins Netz + Tailscale.
3. Vaultwarden & Radio down (kommen mit Anker zurück).
4. **Stockenweiler-Uplink:** Latenz top (17 ms), aber Download real nur **~20–40 KB/s** (2026-06-11 gemessen an Debian/Ubuntu/Cloudflare, kein Tailscale-Artefakt). Muster (gute Latenz + gedrosselter Durchsatz) = **Bandbreiten-Shaping/Rate-Limit** auf der VM-Egress → **mit FLO klären** (sein Host/Netz, wir haben keinen HW-Zugriff). Kleine Web-Seiten ok, große Transfers (Git/Backups/Medien) leiden.

## 🤖 Klausi (Odoo-Nachrichtenfach-Bot)
n8n-Workflow `1fLw0n1e0gaObjsp`. Kryptische Nachrichten = **Mojibake** (`?? Klausi:` statt `🤖 Klausi:`) + Webhook `odoo-klausi` nicht registriert. Fix im n8n-**Browser-UI** (UTF-8), Workflow aus/ein. Ollama selbst ist gesund. Details: Desktop `FRAWO Ops/Bestandsaufnahme_2026-06-11/03_Roadmap-und-offene-Punkte.md`.

---
*Vollständige Bestandsaufnahme (Hardware, Strom, Roadmap): auf dem StudioPC unter `Desktop/FRAWO Ops/Bestandsaufnahme_2026-06-11/`.*

# Aktueller Status — FraWo GbR Infrastruktur
**Stand: 2026-05-30 | Geprüft durch: Claude Sonnet 4.6 + Wolf**

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
- FraWo Radio Backend: http://radio-api.hs27.internal:9500 ✅
- Icecast: funk.frawo-tech.de → Relay frawo-docker-1:8000 ✅
- RAM: 6GB ✅

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

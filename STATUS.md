# Aktueller Status — FraWo GbR Infrastruktur
**Stand: 2026-05-28 | Geprüft durch: Claude Sonnet 4.6 + Wolf**

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
- Swap: 2GB aktiv ✅
- Login: wolf@frawo-tech.de / FrawoWolf2026! (Vault: Odoo ERP — Admin)
- Restart: unless-stopped + PVE startup order=3 ✅

### ☁️ Nextcloud (VM 300, 10.4.0.21)
- Intern: http://cloud.hs27.internal ✅
- Öffentlich: https://cloud.frawo-tech.de ✅ HTTP 200
- Admin: frawoadmin / NC-Frawo-2026! (Vault aktualisiert 2026-05-28)
- Ordner: /Dokumente/{Eingang,Archiv,Verträge,Rechnungen} ✅
- trusted_proxies: 10.4.0.0/24 + 100.64.0.0/10 ✅

### 📄 Paperless-ngx (VM 330, 10.4.0.23)
- Intern: http://paperless.hs27.internal ✅
- Admin: frawoadmin / PL-Frawo-2026! (Vault aktualisiert 2026-05-28)
- API Token: 4ca7affa0948fe3a73bb224c60fe1090d1c00b08
- Post-consume Script: /usr/local/bin/paperless-to-nc.sh → NC/Archiv ✅
- rclone-Sync: alle 5 min NC/Eingang → consume_dir (cron auf VM 330) ✅

### 🔐 Vaultwarden (CT 120, 10.4.0.26)
- URL: http://vault.hs27.internal ✅
- Wolf Master-PW: FrawoWolf2026! (Recovery 2026-05-27)
- 437 Ciphers (429 Org + 8 persönlich) ✅
- Admin-Token: FrawoAdminVault2026! (argon2id) ✅
- SIGNUPS_ALLOWED: false ✅

### 📡 Radio-Node (CT 130, 10.4.0.28, TS: 100.78.88.33)
- AzuraCast: http://radio.hs27.internal ✅
- Navidrome: http://navidrome.hs27.internal ✅
- FraWo Radio Backend: http://radio-api.hs27.internal:9500 ✅
- Icecast: funk.frawo-tech.de → Relay frawo-docker-1:8000 ✅
- RAM: 6GB (hot-upgraded) ✅

### 🐳 frawo-docker-1 (Stockenweiler, TS: 100.94.32.41)
- Services: n8n (5678), Portainer (9000), Grafana (3001), Prometheus (9091), Icecast-Relay (8000)
- UFW: aktiv — deny in, allow Tailscale + 10.30.8.0/24 ✅
- sudo-PW unbekannt → nsenter-Workaround via Docker ✅

### 🏠 Toolbox (CT 100, 10.4.0.20, TS: 100.82.26.53)
- Caddy: Up ✅ (Edge-Proxy für alle hs27.internal Domains)
- AdGuard: Up, admin / FrawoAdGuard2026! ✅
- cloudflared: aktiv (systemd), 6 CF-Tunnel-Routen ✅
- Uptime Kuma: http://uptime.hs27.internal/status/frawo ✅

---

## Bekannte Blocker

| # | Was | Wo | Priorität |
|---|-----|-----|-----------|
| #159 | PBS VM 240: kein Netzwerk | PVE VNC Console | Mittel |
| #251 | PVE Firewall | PVE Web UI | Hoch |
| #241 | HAOS Eltern: Heimat unklar | Wolf-Entscheidung | Niedrig |

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

**Korrespondenten:** BG ETEM, EGS, Obi, riverty, Thomann, VG Sigmarszell
**Tags:** Anker, anmeldung, Beleg, GbR, Nebenkosten, Obi, Thomann, Wolf.EE
**Dokumenttypen:** Bescheid, Kassenbeleg, Mahnung, Rechnung

---

## Odoo Workflow

```
Neue Idee → 💡 Brainstorm (stage 86) → Wolf-Freigabe
           → ⚙️ Planung (stage 2) → Agent plant
           → 🚀 In Arbeit (stage 3) → Agent umsetzt
           → ✅ Erledigt (stage 6) → DoD-Note
```

**Zugang:** wolf@frawo-tech.de / FrawoWolf2026! (xmlrpc: 10.4.0.22:8069, DB: FraWo_GbR)

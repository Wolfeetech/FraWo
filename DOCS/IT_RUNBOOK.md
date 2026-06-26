# FraWo IT-Runbook — Topologie, Zugangswege & Troubleshooting

> **Stand:** 2026-06-26 | Verifiziert in dieser Session  
> **SSOT:** `NOW.md` im Repo (lesen bei Session-Start!)  
> **Secrets:** Nur in Vaultwarden → vault.frawo.tech

---

## 1. Physische Topologie (Rothkreuz)

| Gerät | IP (LAN) | Tailscale | Rolle |
|---|---|---|---|
| UCG Cloud Gateway Ultra | 10.1.0.1 | — | Router, Firewall, DHCP |
| StudioPC | 10.1.0.211 | — | Admin-Workstation |
| **ProDesk-PVE** | 10.1.0.128 | 100.91.20.116 | PVE-Node B (main) |
| **anker-pve** | 10.1.0.92 | 100.69.179.87 | PVE-Node A |
| frawo-docker-1 | — | 100.94.32.41 | Stockenweiler (Debian) |

---

## 2. Virtuelle Maschinen & Container

### ProDesk-PVE (10.1.0.128) — SSH: `ssh pve`

| VMID | Name | IP | Status | Funktion |
|---|---|---|---|---|
| VM360 | homeassistant-eltern | 10.1.0.248 | 🟢 | HA Eltern (Stockenweiler) |
| VM210 | azuracast-vm | 10.1.0.38 | 🟢 | Radio funk.frawo.tech |
| CT101 | adguard | 10.1.0.52 | 🟢 | Primary DNS |
| CT103 | npm | 10.1.0.149 | 🟢 | Nginx Proxy Manager |
| CT106 | wireguard | 10.1.0.239 | 🟢 | WireGuard VPN |
| CT108 | vaultwarden | 10.1.0.95 | 🟢 | vault.frawo.tech |
| CT109 | pbs | 10.1.0.7 | 🟢 | Proxmox Backup Server |
| CT110 | n8n | 10.1.0.100 | 🟢 | n8n Automation |
| CT120 | fileserver | 10.1.0.94 | 🟢 | Samba/NFS |
| CT140 | frawotech-web | — | 🟢 | frawo.tech Website |
| CT130 | mail-relay | — | 🔴 | gestoppt |
| CT150 | monitoring-stack | — | 🔴 | gestoppt |

### anker-pve (10.1.0.92) — SSH: `ssh anker-pve`

| VMID | Name | IP | Status | Funktion |
|---|---|---|---|---|
| VM210 | haos | 10.1.0.40 | 🟢 | Home Assistant OS (main) |
| CT140 | odoo | 10.1.0.112 | 🟢 | Odoo 19 ERP (frawotech-web-1) |
| CT150 | openclaw | 10.1.0.31 | 🟢 | ServAssi Agent (Tailscale 100.72.154.15) |
| CT109 | pbs-anker | — | 🟢 | Proxmox Backup Server |

---

## 3. SSH-Zugangswege

```bash
# ProDesk PVE (main node)
ssh pve                         # 10.1.0.128, Key: ~/.ssh/id_ed25519

# anker-pve
ssh anker-pve                   # 10.1.0.92 / Tailscale 100.69.179.87, Key: ~/.ssh/pve_ed25519

# OpenClaw ServAssi (IMMER via Tailscale - LAN 10.1.0.31 unzuverlässig)
ssh openclaw-ct                 # 100.72.154.15, Key: ~/.ssh/pve_ed25519

# Stockenweiler Debian-Server
ssh frawo-docker                # 100.94.32.41, User: wolf, Key: ~/.ssh/hs27_ops_ed25519

# In LXC-Container einsteigen (auf ProDesk):
ssh pve "pct exec 101 -- bash"  # adguard
ssh pve "pct exec 108 -- bash"  # vaultwarden
ssh pve "pct exec 110 -- bash"  # n8n
ssh pve "pct exec 140 -- bash"  # frawotech-web

# In Odoo-CT (anker-pve):
ssh anker-pve "pct exec 140 -- bash"
```

### UCG API (SSH deaktiviert, Port 22 geschlossen)
```bash
curl -sk -H "X-API-KEY: <key-aus-vault>" https://10.1.0.1/proxy/network/api/s/default/stat/device
```

---

## 4. Odoo ERP (10.1.0.112)

```bash
# In CT140 auf anker-pve:
ssh anker-pve "pct exec 140 -- bash"
cd /opt/frawotech
docker compose ps               # Status
docker compose restart          # Neustart Odoo+DB
docker compose logs -f --tail=50

# Asset-Neukompilierung nach Updates:
docker exec -it frawotech-web-1 odoo -u web,website -d FraWo_GbR --stop-after-init
```

---

## 5. OpenClaw / ServAssi Agent

```bash
ssh openclaw-ct                 # Root auf CT150

# Cron-Status prüfen:
docker exec openclaw openclaw cron list

# Log der letzten Runs:
docker logs openclaw --tail=50

# Manuell Agent triggern:
docker exec openclaw openclaw cron trigger odoo-agent-poll

# MCP-Server status:
docker exec openclaw openclaw mcp list
```

**WICHTIG:** Cron `odoo-agent-poll` NIEMALS löschen/deaktivieren ohne Wolf-Freigabe "CRON-STOP".

---

## 6. Automatisierungen (systemd Timer auf ProDesk)

| Timer | Zeit | Funktion |
|---|---|---|
| `ucg-nightly-reboot.timer` | täglich 04:00 | UCG-Gateway Neustart via API |
| `pve-fstrim.timer` | So 03:00 | LXC fstrim → LVM Thin Pool Rückgewinnung |
| PBS Backup-Job | täglich 03:00 | Backup aller VMs/CTs |

```bash
ssh pve "systemctl list-timers"   # Timer-Status
ssh pve "journalctl -t ucg-reboot --no-pager -n 5"   # UCG-Reboot Log
ssh pve "journalctl -t pve-fstrim --no-pager -n 10"  # fstrim Log
```

---

## 7. LVM Thin Pool Monitoring (ProDesk)

```bash
ssh pve "lvs --units g pve"     # Pool-Status aller LVs

# fstrim manuell für alle CTs:
ssh pve "/usr/local/sbin/pve-fstrim-all.sh"

# Disk innerhalb CT prüfen:
ssh pve "pct exec <VMID> -- df -h /"
```

**Schwellwerte:**
- Thin Pool `data` > 80%: Snapshots prüfen/löschen
- LV `Data%` > 90% + FS > 85%: LV mit `pct resize` vergrößern

---

## 8. UCG API-Referenz

```bash
BASE="https://10.1.0.1/proxy/network/api/s/default"
KEY="<key-aus-vault>"

# Geräte auflisten:
curl -sk -H "X-API-KEY: $KEY" "$BASE/stat/device" | python3 -m json.tool

# UCG sofort neu starten:
curl -sk -X POST -H "X-API-KEY: $KEY" -H "Content-Type: application/json" \
  -d '{"cmd":"restart","mac":"1c:6a:1b:38:ae:ff"}' "$BASE/cmd/devmgr"

# DHCP-Reservierungen:
curl -sk -H "X-API-KEY: $KEY" "$BASE/rest/fixedip" | python3 -m json.tool
```

---

## 9. Shelly Sicherheitsregel ⚠️

**Shelly `10.4.0.11` (MAC e4:b0:63:d5:66:1c) darf NIEMALS remote geschaltet werden.**  
Dieser Shelly steuert den IT/Netzwerk-Strom. Abschalten = Systemausfall + Remote-Lockout.

---

## 10. Notfall-Checkliste

| Problem | Erste Maßnahme |
|---|---|
| DNS ausgefallen | CT101 adguard auf ProDesk prüfen: `ssh pve "pct status 101 && pct start 101"` |
| Odoo nicht erreichbar | `ssh anker-pve "pct exec 140 -- bash"`, `docker compose ps` |
| UCG nach Neustart offline | Vor Ort → UCG Reset-Button 10s |
| HA nicht erreichbar | `ssh anker-pve "qm status 210"`, ggf. `qm reboot 210` |
| ProDesk nicht erreichbar | Direkt zu Rothkreuz, oder Tailscale via anker-pve |
| LVM Thin Pool > 90% | `pct fstrim` für alle CTs, dann Snapshots prüfen |

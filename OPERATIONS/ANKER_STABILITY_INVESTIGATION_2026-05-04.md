# Anker Host Stability Investigation - 2026-05-04

**Zeitstempel:** 2026-05-04 09:40 Europe/Berlin
**Status:** KRITISCH - Anker Host instabil, blockiert mehrere Deployments
**Impact:** VM 200 (Nextcloud), VM 220 (Odoo), CT 100 (toolbox) betroffen

---

## Symptome

### SSH Connectivity Issues
- **Connection timeouts:** `Connection timed out during banner exchange`
- **Connection resets:** `Connection reset by 100.69.179.87 port 22`
- **Packet loss:** 50% bei ICMP ping tests
- **Intermittent:** Verbindung funktioniert manchmal, aber unzuverlässig

### Netzwerk-Routing Probleme
- **10.1.0.22 (Odoo VM):** Nicht vom lokalen Netzwerk erreichbar
- **10.1.0.30 (Nextcloud VM):** Nicht vom lokalen Netzwerk erreichbar
- **10.1.0.20 (toolbox CT):** Nur via Tailscale erreichbar

**Aber:** Frontdoor-Zugriffe via Tailscale/toolbox/Caddy funktionieren!

### Tailscale Status
```
100.69.179.87   proxmox-anker     w.prinz1101@  linux    active; direct 92.211.33.45:9428, tx 6732 rx 4336
```
- Tailscale zeigt "active; direct" → Sollte funktionieren
- Aber SSH ist instabil

---

## Impact Analysis

### Blockierte Deployments
1. **VM200 Agent Intake:** `deploy_vm200_agent_intake_runtime.py` nutzt `qm guest exec` via Anker SSH → blockiert
2. **Odoo RPC Scripts:** Direkte Verbindung zu `10.1.0.22:8069` → timeout
3. **Odoo Masterplan Sync:** `odoo_masterplan_sync.py` → timeout

### Funktionierende Workarounds
✅ **Odoo Webinterface:** via `https://odoo.hs27.internal` (Tailscale → toolbox → Caddy → Odoo)
✅ **Nextcloud:** via `https://cloud.hs27.internal` (HTTP 302)
✅ **Portal, HA:** via Tailscale/toolbox routing

---

## Storage Alert

Anker `local-lvm` bei **89.4%** Auslastung - kritische Grenze erreicht!

```
Storages:
  - local-lvm: 89.4% used (lvmthin)
  - local: 42.1% used (dir)
  - pbs-usb: 42.1% used (dir)
  - stockenweiler-data (NFS): 31.7% used
  - google-drive: 28.0% used
```

**Mögliche Ursache:** LVM-Thin-Pool voll → könnte zu I/O-Problemen und Instabilität führen

---

## Root Cause Hypotheses

### 1. Storage Pressure (WAHRSCHEINLICH)
- `local-lvm` bei 89.4% → LVM-Thin-Pool nahe am Limit
- Könnte zu I/O-Wartezeiten führen
- SSH/Netzwerk-Stack könnte betroffen sein

### 2. Netzwerk-Konfiguration
- Routing-Problem zwischen 10.1.0.x Netz und externen Clients
- Firewall/iptables Regeln blockieren direkten Zugriff
- Nur via Tailscale/Caddy reverse proxy funktioniert Zugriff

### 3. Hardware/WAN-Instabilität
- Direct Connection via `92.211.33.45:9428` (öffentliche IP)
- Könnte WAN-seitige Probleme haben
- Aber: Tailscale zeigt "active; direct" → sollte stabil sein

---

## Immediate Actions Taken

### 1. ✅ Workaround für Frontdoor-Zugriffe
- hosts-Datei korrigiert: Alle hs27.internal → `100.82.26.53`
- Routing via Tailscale/toolbox funktioniert
- 4/8 Frontdoors grün

### 2. ✅ Odoo Update-Dokument erstellt
- `OPERATIONS/ODOO_UPDATE_2026-05-04.md`
- Manuelle Alternative zu automatischen RPC-Scripts
- Dokumentiert alle Infrastruktur-Fixes

### 3. ✅ Stockenweiler Monitoring gesichert
- Telegraf auf pve-stock: InfluxDB-Output deaktiviert
- `outputs.discard` implementiert
- Verhindert weiteres Swap-Buffering

---

## Recommended Next Steps

### PRIO 1: Anker Storage Cleanup
```bash
# Via Stockenweiler als Jump Host
ssh root@100.91.20.116
ssh-via-tailscale root@100.69.179.87  # Falls erreichbar

# Check LVM Thin Pool
lvs
pvs
vgs

# Cleanup candidates:
# - Alte VM snapshots löschen
# - Ungenutzte Volumes identifizieren
# - local-lvm erweitern falls möglich
```

### PRIO 2: Stabilität verifizieren
- 24h Monitoring: SSH-Verbindungen, Packet loss, Ping
- Tailscale Status regelmäßig checken
- System logs auf Anker prüfen (dmesg, journalctl)

### PRIO 3: Alternative Deployment-Strategie
Wenn Anker instabil bleibt:
- VM 200/220 direkt via Tailscale zugänglich machen?
- Oder: Deployments über toolbox/Caddy reverse-shell?
- Oder: Temporär auf Stockenweiler migrieren für Deployment

### PRIO 4: VM200/220 Netzwerk-Debug
```bash
# Warum ist 10.1.0.22/30 nicht vom lokalen Netzwerk erreichbar?
# Check auf Anker:
iptables -L -n -v
ip route show
ip addr show
# Check bridge/vmbr Konfiguration
cat /etc/network/interfaces
```

---

## Technical Details

### Ping Test Results (2026-05-04 09:00)
```bash
# Anker PVE Host
$ ping -n 2 100.69.179.87
Antwort von 100.69.179.87: Bytes=32 Zeit=31ms TTL=64
Zeit­überschreitung der Anforderung.
Ping-Statistik: Pakete: Gesendet = 2, Empfangen = 1, Verloren = 1 (50% Verlust)

# Odoo VM (via local network)
$ ping -n 2 10.1.0.22
Antwort von 10.1.0.210: Zielhost nicht erreichbar.
Ping-Statistik: Pakete: Gesendet = 2, Empfangen = 2, Verloren = 0 (0% Verlust)
# → Reply kommt von 10.1.0.210 (HA?), nicht von 10.1.0.22 → Routing-Problem!
```

### SSH Test Results
```bash
$ ssh -o ConnectTimeout=10 root@100.69.179.87
Connection timed out during banner exchange
# ODER
Connection reset by 100.69.179.87 port 22
```

### Deployment Script Requirements
`scripts/business/deploy_vm200_agent_intake_runtime.py`:
- Nutzt `qm guest exec` über SSH zum Anker PVE
- Benötigt stabile SSH-Verbindung
- Default: `--ssh-host pve-anker --vmid 200`

---

## Workaround Documentation

### Manuelle VM200 Deployment Alternative
Falls Anker SSH nicht verfügbar:

1. **Via Nextcloud Webinterface:**
   - https://cloud.hs27.internal funktioniert
   - Könnte Web-basierte File-Upload nutzen?

2. **Via toolbox als Proxy:**
   - SSH zu toolbox (100.82.26.53)
   - Von toolbox zu VM 200 (wenn im gleichen Netz)

3. **Via Stockenweiler als Jump:**
   - Wenn Anker im lokalen Netz von Stockenweiler erreichbar
   - `ssh root@100.91.20.116` → dann weiter zu Anker

---

## Monitoring Plan

### 24h Watch (2026-05-04 09:40 - 2026-05-05 09:40)
- [ ] Stündlich: `ping -n 10 100.69.179.87` (packet loss Trend)
- [ ] Alle 2h: `ssh root@100.69.179.87 "uptime && free -h"` (erreichbar?)
- [ ] Alle 4h: Anker storage check (local-lvm %)
- [ ] Kontinuierlich: Frontdoor-Status (sind Services erreichbar?)

### Alert Thresholds
- **SSH timeout > 3 aufeinander:** CRITICAL
- **Packet loss > 70%:** CRITICAL
- **local-lvm > 92%:** CRITICAL
- **Swap auf Stockenweiler > 60%:** WARNING

---

**Status:** Dokumentiert, Monitoring vorbereitet, Workarounds aktiv
**Next Review:** 2026-05-05 09:40 (nach 24h Beobachtung)

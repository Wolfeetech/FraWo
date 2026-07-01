# FraWo - System Status WAHRHEIT

**Letzte Aktualisierung:** 2026-05-13 07:45
**Konsolidiert aus:** Alle Claude-Sessions + Live-Tests

---

## 🌐 NETZWERK-TOPOLOGIE (KORREKT)

### Lokales Netzwerk (10.1.0.x)
```
10.1.0.20  - PBS (Proxmox Backup Server) - VM/CT 109?
10.1.0.21  - Nextcloud - VM/CT 121
10.1.0.22  - Odoo ERP - VM 220 ✅ HAUPTSYSTEM
10.1.0.23  - (Unbekannt)
10.1.0.24  - Home Assistant - VM 124
10.1.0.26  - Vaultwarden - VM/CT 108
10.1.0.30  - (Unbekannt)
```

### Proxmox Hosts
```
192.168.178.175  - Proxmox Anker (Port 8006)
                 - Odoo auf diesem Host (Port 8069)
```

### Tailscale VPN IPs
```
100.98.31.60   - wolfstudiopc (dieser PC) ✅ ONLINE
100.69.179.87  - proxmox-anker ❌ offline (11h)
100.91.20.116  - stockenweiler-pve ❌ offline (3d)
```

### Tailscale Direct Connection IPs (10.4.0.x)
```
10.4.0.99  - Proxmox Anker (direct connection IP)
           - NUR wenn Tailscale direkt verbunden ist
           - NICHT die Service-IP!
```

---

## ⚠️ FEHLER IN FRÜHEREN SESSIONS

### FALSCH (verwendet am 13. Mai):
```
❌ Odoo IP: 10.1.0.112  (EXISTIERT NICHT!)
❌ Ping 10.1.0.112      (Zielhost nicht erreichbar)
```

### RICHTIG (aus Sessions 4.-8. Mai):
```
✅ Odoo IP: 10.1.0.22  (VM 220)
✅ Odoo Port: 8069
✅ Proxmox Host: 192.168.178.175
```

---

## 🔴 AKTUELLER SERVICE-STATUS (13. Mai 2026)

### PROXMOX HOSTS
```
Anker (192.168.178.175)
├─ Proxmox Web UI (8006): ??? (nicht getestet)
├─ Tailscale: OFFLINE (seit 11h)
└─ VMs/Container: ??? (kein Zugriff)

Stockenweiler (100.91.20.116)
├─ Tailscale: OFFLINE (seit 3 Tagen!)
├─ PBS (Backup): ❌ nicht erreichbar
├─ n8n (Automation): ❌ nicht erreichbar
├─ Vaultwarden: ❌ nicht erreichbar
└─ AdGuard: ❌ nicht erreichbar
```

### SERVICES AUF ANKER
```
Odoo (10.1.0.22:8069)      - ❌ UNGETESTET (falsche IP verwendet!)
Nextcloud (10.1.0.21:80)   - ❌ OFFLINE (Tailscale down)
Home Assistant (10.1.0.24) - ❌ OFFLINE (Tailscale down)
Vaultwarden (10.1.0.26)    - ❌ OFFLINE (Tailscale down)
```

---

## 🧪 NÄCHSTE TESTS (MIT KORREKTER IP!)

### 1. Odoo ERP testen (RICHTIGE IP)
```bash
# FALSCH (bisher verwendet):
ping 10.1.0.112  ❌

# RICHTIG (jetzt testen):
ping 10.1.0.22  ✅
curl http://10.1.0.22:8069
curl http://192.168.178.175:8069
```

### 2. Proxmox Web UI
```bash
curl -k https://192.168.178.175:8006
```

### 3. Tailscale Status
```bash
tailscale ping proxmox-anker
tailscale ping stockenweiler-pve
```

---

## 📊 STATUS-HISTORIE (aus Sessions)

| Datum | Odoo | Proxmox Anker | Stockenweiler | Notizen |
|-------|------|---------------|---------------|---------|
| 13. Mai | ??? | Offline (TS) | Offline (TS) | Falsche Odoo-IP verwendet! |
| 8. Mai | OFFLINE | Probleme | Probleme | Connection timeout, NPM down |
| 4. Mai | ONLINE | ONLINE | ? | Entwicklungsarbeit |
| 28. Apr | ONLINE | ONLINE | ? | Website-Updates |

---

## 🚨 KRITISCHE ERKENNTNISSE

### 1. IP-VERWECHSLUNG
- **10.1.0.x** = Lokales Netzwerk (Services)
- **10.4.0.x** = Tailscale Direct Connection IPs (dynamisch!)
- **NIEMALS** 10.1.0.112 für Odoo verwenden!

### 2. Netzwerk-Problem
- Beide Proxmox-Server: Tailscale offline
- Kann seit Tagen nicht erreicht werden
- SSH unmöglich

### 3. TODO-Listen
- Viele unterschiedliche TODOs über Sessions verteilt
- Wurden HEUTE konsolidiert → TODO_MASTER.md ✅

---

## ✅ WAS IST SICHER/KORREKT

1. **Projekt-Repo:** `C:\Users\StudioPC\OneDrive\Dokumente\GitHub\FraWo`
2. **Git Branch:** `main`
3. **Lokaler PC:** Funktioniert ✅
4. **Odoo VM:** VM 220, IP 10.1.0.22, Port 8069
5. **Proxmox Host:** 192.168.178.175
6. **Tailscale:** wolfstudiopc online, Server offline

---

## 🎯 NÄCHSTE SCHRITTE (KORRIGIERT)

### SOFORT: Odoo mit RICHTIGER IP testen
```bash
# Test 1: Lokales Netz
ping 10.1.0.22

# Test 2: Proxmox Host
ping 192.168.178.175
curl http://192.168.178.175:8069

# Test 3: Port Check
nc -zv 10.1.0.22 8069
```

### DANN: Proxmox/Tailscale Problem lösen
- Warum ist Tailscale auf Servern offline?
- Physischer Zugang nötig?
- Router/Netzwerk-Problem?

---

## 📝 LESSONS LEARNED

1. ❌ NIEMALS Tailscale Direct IPs (10.4.0.x) mit Service-IPs (10.1.0.x) verwechseln!
2. ✅ Immer LIVE_CONTEXT.md aktuell halten
3. ✅ IP-Adressen in einem MASTER-Dokument pflegen (dieses!)
4. ✅ Session-Erkenntnisse konsolidieren

---

**Dieses Dokument ist die SINGLE SOURCE OF TRUTH für Netzwerk/IPs! 🎯**

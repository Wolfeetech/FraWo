# FraWo Infrastructure Server Architecture 2026

Dokumentation der zwei klaren Server-Rollen gemäß **Task #816** (*Konsolidierung 2026: weniger, dafür sauber + benutzbar*).

---

## 🏗️ Dual-Host Server Rollen-Verteilung

```
┌─────────────────────────────────────────────────────────────┐
│ 🚀 NODE 1: stockenweiler-pve (HP ProDesk 600 G4 Mini)       │
│ IP: 10.1.0.128 | Primary Production Compute & Services      │
├─────────────────────────────────────────────────────────────┤
│ • CT140: frawotech-web (Odoo 19 Community Edition ERP)      │
│ • CT120: fileserver (Samba Master Storage — M: / R:)        │
│ • VM210: azuracast-vm (FraWo Funk Master Streaming Server)  │
│ • CT108: vaultwarden (Zentraler Passwort-Manager)          │
│ • CT150: monitoring-stack (Prometheus & Grafana)            │
│ • CT110: n8n (Automatisierungen & Uptime Checks)            │
│ • CT101: adguard (Primary DNS & Shield)                     │
│ • CT103: npm (Nginx Proxy Manager Edge Reverse Proxy)       │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ 🛡️ NODE 2: proxmox-anker (Lenovo ThinkCentre M720q Tiny)    │
│ IP: 10.1.0.92 | Secondary HA, Storage Node & Cloud Backup   │
├─────────────────────────────────────────────────────────────┤
│ • VM240: PBS-FraWo (Proxmox Backup Server 3.x)             │
│ • VM210: haos (Home Assistant OS Haupt-Instanz 10.1.0.40)   │
│ • VM300: nextcloud (Cloud Storage Hub & Collaboration)      │
│ • CT150: openclaw (@Frawo_bot Autonomous Agent Execution)   │
│ • CT101: adguard-slave (Secondary DNS Fallback)             │
│ • CT110: storage-node (Secondary Remote Storage)           │
│ • CT130: radio-node (Secondary Radio & Navidrome)          │
│ • GDRIVE: Encrypted Offsite Backup Remote (5.1 TB Storage)  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔒 Backup & Desaster Recovery Pipeline

1. **Host-Level Backups:** ProDesk Guests sichern jede Nacht per Proxmox Backup Server Client direkt auf **VM240 PBS** (`proxmox-anker`).
2. **Database Dumps:** Odoo 19 PostgreSQL Dumps werden täglich um 03:00 Uhr automatisch erzeugt und auf Samba (`CT120`) abgelegt.
3. **Offsite Cloud Sync:** PBS Datasets & Samba Dumps werden verschlüsselt auf **Google Drive Offsite Backup (Rclone 5.1 TB)** synchronisiert.

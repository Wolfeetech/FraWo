# Franznetz & Studio Network Architecture

Dokumentation der Netzwerkintegration gemäß **Task #753**.

---

## 🌐 1. Dual-Location Network Topology

- **Haupt-Standort Stockenweiler:** Subnetz `10.1.0.0/24` (WAN Uplink via UniFi Cloud Gateway Ultra 10.1.0.1).
- **Studio-Standort Franznetz:** Anbindung über **Tailscale Mesh VPN** (Subnetz-Router auf ProDesk `10.1.0.128` & Anker `10.1.0.92`).

## 📶 2. VLAN-Zuordnungen
- **VLAN 101:** Core Servers & Management (`stockenweiler-pve`, `proxmox-anker`, Odoo, Fileserver).
- **VLAN 104:** Smart Home & IoT (Home Assistant 10.1.0.40, Shelly Plugs).
- **VLAN 105:** Gast-Netzwerk & Studio-Audio.

## 🔒 3. Tailscale Subnet Router Status
- Subnetz-Routing für `10.1.0.0/24` ist auf beiden Hosts aktiv.

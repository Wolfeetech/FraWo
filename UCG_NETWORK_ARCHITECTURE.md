# UCG-Ultra Netzwerkarchitektur — Anker/Rothkreuz

> Stand: 2026-04-03 | Managed via UniFi API (API-Key in Vaultwarden: FraWo / Core Infra / UCG Anker API Key)

## Hardware

- **Gerät:** UniFi Cloud Gateway Ultra
- **Standort:** Rothkreuz/Anker
- **WAN1:** Internet 1 (DHCP, primär, 49 Mbit/s ↓ / 19 Mbit/s ↑, Gewicht 99%)
- **WAN2:** Internet 2 (DHCP, Failover)
- **LAN-Uplink:** Proxmox-Host (`10.1.0.92`, VLAN 101)
- **Controller-API:** `https://10.1.0.1` (via Proxmox erreichbar)
- **Tailscale-Zugriff:** via `ssh root@100.69.179.87` → `curl https://10.1.0.1`

## VLAN-Schema

```
VLAN  ID → 10.X.0.0/24  (ID-Logik: VLAN 10N → 10.(N-100).0.0/24 für Anker)
```

| VLAN | Name | Subnet | Gateway | DHCP | Zweck |
|------|------|--------|---------|------|-------|
| native | Default | `192.168.1.0/24` | `192.168.1.1` | ✅ | Legacy-Fallback (ungetaggt) |
| **100** | Anker-Lan | `10.0.0.0/24` | `10.0.0.1` | `10.0.0.10–254` | Vertrauenswürdige Clients (StudioPC, ZenBook, Phones) |
| **101** | Anker-Server | `10.1.0.0/24` | `10.1.0.1` | `10.1.0.6–254` | Proxmox + alle VMs/CTs (Proxmox: `10.1.0.92`) |
| **102** | Anker-DMZ | `10.2.0.0/24` | `10.2.0.1` | `10.2.0.6–254` | Public-facing Services |
| **103** | Anker-DMZ-Radio | `10.3.0.0/24` | `10.3.0.1` | `10.3.0.6–254` | Radio-Services isoliert |
| **104** | Anker-IoT | `10.4.0.0/24` | `10.4.0.1` | `10.4.0.10–254` | Smart Home: Shelly, Roborock, TVs — **inter-VLAN isoliert** |
| **105** | Anker-Guest | `10.5.0.0/24` | `10.5.0.1` | `10.5.0.10–200` | Gäste — nur Internet, kein LAN-Zugriff |
| **110** | Stock-Lan | `10.10.0.0/24` | `10.10.0.1` | `10.10.0.10–254` | Stockenweiler Clients (VPN-Endpunkt) |
| **111** | Stock-Server | `10.11.0.0/24` | `10.11.0.1` | `10.11.0.10–254` | Stockenweiler Server (PVE via VPN) |

## Netzplan-Topologie

```
Internet
  │
  ├─ WAN1 (primär, DSL)
  └─ WAN2 (Failover)
         │
    UCG-Ultra (Rothkreuz)
         │
    ┌────┴─────────────────────────────────────┐
    │           Trunk (alle VLANs)             │
    │                                          │
  Proxmox (10.1.0.92 / VLAN 101)             WiFi APs (später)
    │
    ├─── CT 100 toolbox      (192.168.2.20 → Migration: 10.1.0.20)
    ├─── CT 110 storage-node (192.168.2.30 → Migration: 10.1.0.30)
    ├─── CT 120 vaultwarden  (192.168.2.26 → Migration: 10.1.0.26)
    ├─── VM 200 nextcloud    (192.168.2.21 → Migration: 10.1.0.21)
    ├─── VM 210 haos         (192.168.2.24 → Migration: 10.1.0.24)
    ├─── VM 220 odoo         (192.168.2.22 → Migration: 10.1.0.22)
    └─── VM 230 paperless    (192.168.2.23 → Migration: 10.1.0.23)

    VPN-Tunnel (WireGuard, geplant)
    UCG-Ultra ◄──────────────────────► FritzBox 5690 Pro (Stockenweiler)
                                             │
                                        Proxmox Stock (192.168.178.25)
                                        → zukünftig: VLAN 110/111 geroutet
```

## Firewall-Regeln (Zielzustand)

| Von | Nach | Erlaubt | Gesperrt |
|-----|------|---------|---------|
| **Management** (VLAN 101) | alle | ✅ komplett | — |
| **Anker-Lan** (100) | Anker-Server (101) | ✅ Ports 80,443,8123,8069,8443-8449 | Admin-Ports direkt |
| **Anker-Lan** (100) | Internet | ✅ | — |
| **Anker-IoT** (104) | Internet | ✅ 80/443/NTP | ❌ alle internen VLANs |
| **Anker-Guest** (105) | Internet | ✅ nur | ❌ alles intern |
| **Stock-Lan** (110) | Anker-Server (101) | ✅ gezielt | — |
| **Stock-Server** (111) | Anker-Server (101) | ✅ Server-Ports | — |

> ⚠️ Firewall-Regeln sind noch **nicht** im UCG konfiguriert — nächster Schritt.

## Proxmox VLAN-Migration (ausstehend)

Aktuell läuft Proxmox noch ohne VLAN-Trunking (legacy `192.168.2.0/24` Übergangs-NAT). Nächste Schritte:

```bash
# Auf Proxmox: /etc/network/interfaces
# vmbr0 als VLAN-Trunk konfigurieren
# Jede VM/CT bekommt passende VLAN-ID
# Nur via Tailscale durchführen — nie über lokale IP!
```

### Ziel-Platzierung pro Service

| Service | Current | Target | VLAN | Note |
| --- | --- | --- | --- | --- |
| `CT 100 toolbox` | `192.168.2.20` | `10.1.0.20` | `101 Anker-Server` | keeps frontdoor, DNS, Tailscale, Caddy, AdGuard |
| `CT 110 storage-node` | `192.168.2.30` | `10.1.0.30` | `101 Anker-Server` | backend storage path, no early cutover |
| `CT 120 vaultwarden` | `192.168.2.26` | `10.1.0.26` | `101 Anker-Server` | security-critical, migrate late with rollback |
| `VM 200 nextcloud` | `192.168.2.21` | `10.1.0.21` | `101 Anker-Server` | core business app |
| `VM 210 haos` | `192.168.2.24` | `10.1.0.24` | `101 Anker-Server` | move after core business apps |
| `VM 220 odoo` | `192.168.2.22` | `10.2.0.22` | `102 Anker-DMZ` | published target remains DMZ candidate in this SSOT |
| `VM 230 paperless` | `192.168.2.23` | `10.1.0.23` | `101 Anker-Server` | core business app |

### Laufende Cutover-Reihenfolge

Die Ziel-Platzierung ist **nicht** automatisch die echte Runtime-Reihenfolge. Fuer den laufenden Uebergang gilt:

1. aktuellen Zustand einfrieren: `Tailscale first`, toolbox frontdoors gruen, Legacy-Gaeste weiter isoliert
2. zuerst ein Low-Risk-Pilot ohne Kern-Business-Ausfall, bevorzugt `portal`, `media` oder `radio`-Pfad
3. danach Kern-Business in dieser Reihenfolge:
   - `Odoo`
   - `Nextcloud`
   - `Paperless`
4. danach `Home Assistant`
5. danach `Vaultwarden` nur mit explizitem Rollback
6. `storage-node` / `PBS` / Storage-Umbauten zuletzt

> **Gate:** Jede Runtime-Migration nur nach Snapshot + Tailscale-Verify. Das VLAN-Zielbild bleibt bindend; die Runtime-Reihenfolge folgt aber Risiko und Rueckbaubarkeit.

### Low-Risk-Pilot-Kandidaten

| Pilot | Warum zuerst | Verify |
| --- | --- | --- |
| `portal` | statischer Frontdoor, kein Kern-Business-State | `http://100.99.206.128:8447/` |
| `media` | nutzbar, aber nicht business-kritisch | `http://100.99.206.128:8449/` |
| `radio` | sichtbarer Testpfad, aber nicht Kern-Business | `http://100.99.206.128:8448/` |

**Empfehlung jetzt:** `portal` zuerst. Danach `media`, erst dann `radio`.

### `portal`-Pilot-Preflight

Dieser Block ist bewusst der naechste `Codex`-Schritt, ohne mit `Gemini` zu kollidieren.

**Ziel:** den ersten UCG-Service-Uebergang als statischen, rueckbaubaren Pilot vorbereiten, bevor Kern-Business-Dienste bewegt werden.

**Preflight vor jeder Runtime-Aenderung:**

1. `Tailscale first` bleibt der Management-Pfad.
2. `portal` ist ueber `http://100.99.206.128:8447/` gruen.
3. `ssh root@100.69.179.87` und `ssh root@100.91.20.116` sind gruen.
4. Snapshot-/Rollback-Pfad fuer `CT 100 toolbox` ist dokumentiert.
5. Keine gleichzeitige Firewall-, DNS- oder Hostname-Aenderung im selben Fenster.

**Scope des Piloten:**

- nur `portal`
- keine Aenderung an `Odoo`, `Nextcloud`, `Paperless`, `Vaultwarden`, `HA`
- keine Public- oder DNS-Cutovers
- kein gleichzeitiger VLAN- oder Router-Umbau

**Rollback-Regel:**

- Frontdoor bleibt stabil; bei Abweichung sofort auf den letzten gruenden toolbox-Pfad zurueck.

**Verify nach dem Pilot:**

- `http://100.99.206.128:8447/` liefert weiter `200`
- `portal.hs27.internal` zeigt weiter denselben Inhalt
- `estate_census` bleibt fuer alle Frontdoors gruen
- `AI_SERVER_HANDOFF.md` wird direkt nachgezogen

**Read-only Proof jetzt:** `artifacts/ucg_portal_pilot_preflight/latest_report.md`

**Gated Runtime Runbook:** `UCG_PORTAL_PILOT_RUNBOOK.md`

**Aktueller Live-Stand `2026-04-03`:** additive Alias `10.1.0.20/24` ist auf `CT 100 toolbox` aktiv und persistent; der `portal`-VHost antwortet auf dem Zielpfad, waehrend die bestehenden Toolbox-Frontdoors weiter `8/8` gruen bleiben.

## VPN zu Stockenweiler (geplant)

**Methode:** UCG-Ultra WireGuard Site-to-Site

```
UCG-Ultra (Rothkreuz)          FritzBox 5690 Pro (Stockenweiler)
  WAN: 92.211.33.54        ↔     WAN: 91.14.44.20
  VPN-Subnet: 10.10.0.0/24       LAN: 192.168.178.0/24
              10.11.0.0/24
```

**Status:** Geplant — FritzBox WireGuard-Konfiguration ausstehendt.

## UCG API

```bash
API_KEY="<from-vaultwarden>"
BASE="https://10.1.0.1/proxy/network/api/s/default"

# VLANs lesen
ssh root@100.69.179.87 "curl -sk -H 'X-API-KEY: $API_KEY' '$BASE/rest/networkconf'"

# Gerätestatus
ssh root@100.69.179.87 "curl -sk -H 'X-API-KEY: $API_KEY' '$BASE/stat/device'"
```

> API-Key liegt in Vaultwarden: **FraWo / Core Infra / UCG Anker API Key**

## Erstellungslog

| Datum | Aktion | VLAN-IDs |
|-------|--------|----------|
| 2026-04-03 | Initial-VLANs vom User angelegt | 100, 101, 102, 103 |
| 2026-04-03 | IoT, Guest, Stock-VLANs via API erstellt | 104, 105, 110, 111 |
| — | Firewall-Regeln | ausstehend |
| — | Proxmox VLAN-Trunk-Migration | ausstehend |
| — | WireGuard VPN zu Stockenweiler | ausstehend |

# FraWo GbR — 3-Standort Architektur (HA + Infra)

**Erstellt:** 2026-06-02 | **Priorität:** Mittelfristig

## Standorte

| Standort | Kurzname | Netz | Status |
|----------|----------|------|--------|
| Anker / Rothkreuz 22 | `anker` | FraWo GbR | ✅ Aktiv |
| Stockenweiler | `stock` | Alois Prinz | ⏳ Aufbau |
| FraWo Studio | `studio` | FraWo GbR | 📋 Geplant |

---

## Prinzip: Lokale HA + Föderale Verbindung

```
         ┌──────────────────────────────────────────────┐
         │              Tailscale Mesh VPN               │
         │         (verbindet alle 3 Standorte)          │
         └──────────┬───────────────────┬────────────────┘
                    │                   │
        ┌───────────┴──────┐  ┌─────────┴──────────────┐
        │   ANKER (FraWo)  │  │   STOCKENWEILER        │
        │  Lenovo + PVE    │  │  HP ProDesk + PVE       │
        │  HAOS VM210      │  │  HAOS VM (neu)          │
        │  Odoo/NC/Radio   │  │  Nur lokale Dienste     │
        │  Admin: Wolf     │  │  Alois: NUR USER        │
        └───────────┬──────┘  └─────────┬───────────────┘
                    │                   │
        ┌───────────┴──────┐            │
        │   FRAWO STUDIO   │────────────┘
        │  Hardware: TBD   │
        │  HAOS standalone │
        │  Admin: Wolf     │
        └──────────────────┘
```

### Kernprinzipien
- **Jeder Standort** ist vollständig **autonom offline-fähig**
- **HA → HA** Kommunikation via `remote_homeassistant` Integration über Tailscale
- **Wenn 1 Standort offline**: andere laufen ungestört weiter
- **Wenn alle online**: Zentrales Dashboard zeigt alle 3 Standorte

---

## Standort 1: Anker (FraWo GbR) — Referenz-Setup

### Hardware
- **Lenovo Thin Centre** (`proxmox-anker`, TS: 100.69.179.87)
- GameMax Hurricane (`wolfstudiopc`) — Wolf's Arbeitsrechner
- Surface Go — Kiosk/Tablet
- RPi 4 — **Empfehlung: zu Stockenweiler migrieren** (dort sinnvoller)

### Dienste
| Dienst | VM/CT | Ports | Admin |
|--------|-------|-------|-------|
| HomeAssistant OS | VM210 | 8123 | Wolf |
| Odoo ERP | VM220 | 8069 | Wolf, Franz |
| Nextcloud | VM300 | 443 | Wolf |
| Paperless | VM330 | 8000 | Wolf |
| PBS Backup | VM240 | 8007 | Wolf |
| AzuraCast Radio | CT130 | 8080 | Wolf |
| Vaultwarden | CT120 | 80 | Wolf |
| Toolbox/Caddy | CT100 | 443 | Wolf |

### Benutzer
- **Wolf Prinz**: Administrator (alle Dienste)
- **Franz Bienert**: Odoo-Benutzer, Nextcloud-Benutzer, Radio-Streamer
- **Alois Prinz**: KEIN Zugang zu FraWo-Infrastruktur

---

## Standort 2: Stockenweiler (Alois Prinz) — Eigenständig

### Hardware-Optionen
| Option | Hardware | Kosten | Empfehlung |
|--------|----------|--------|------------|
| A | **RPi 4 von Anker migrieren** | 0€ | ✅ Sofort |
| B | HP ProDesk (stockenweiler-pve) | 0€ | ✅ Besser (mehr Power) |
| C | Neuer RPi 5 kaufen | ~80€ | Langfristig |

**Empfehlung: HP ProDesk einschalten → PVE installieren → HAOS als VM**

### Dienste (NUR lokal, eigenständig)
| Dienst | Hardware | Zweck |
|--------|----------|-------|
| HomeAssistant OS | HP ProDesk VM | Smart Home Alois |
| Navidrome | HP ProDesk VM | Musik für Alois |
| *(optional)* Vaultwarden | HP ProDesk CT | Eigene Passwörter |

### Benutzer & Rechte
| Person | HA-Rolle | Odoo | Anker-Infra |
|--------|----------|------|-------------|
| **Wolf Prinz** | Admin (remote) | Admin | Admin |
| **Alois Prinz** | ⚠️ **NUR USER** | Kein Zugang | ❌ Gesperrt |

> **Warum kein Admin für Alois:** Hat bestehende Konfiguration verbockt.
> Wolf behält Remote-Admin-Zugang für Wartung.

### HA-Entities aus anderen Standorten (read-only)
- Wetterdaten von Anker-HA sehen
- Energie-Dashboard Anker (lesend)
- Status seiner eigenen Geräte (lokal autonom)

---

## Standort 3: FraWo Studio

### Hardware (TBD — Wolf entscheidet)
- Option A: RPi 4/5 (günstig, sparsam)
- Option B: Intel NUC (mehr Power)
- Option C: Mini-PC (AM01, Beelink etc.)

### Dienste
| Dienst | Zweck |
|--------|-------|
| HomeAssistant OS | Studio-Automation (Licht, Steckdosen, Sensoren) |
| Monitoring Node Exporter | Grafana auf frawo-docker-1 |

---

## Technische Umsetzung: HA-Vernetzung

### Schritt 1: Tailscale auf allen HA-Instanzen
```yaml
# In HA: Einstellungen → Add-ons → Tailscale installieren
# HA-Addon: community store → Tailscale
# Alle 3 HAs im selben Tailnet
```

### Schritt 2: remote_homeassistant Integration
```yaml
# In ANKER-HA (configuration.yaml):
homeassistant_remote:
  instances:
    - host: 100.91.20.116  # Stockenweiler HA (Tailscale IP)
      access_token: !secret stock_ha_token
    - host: STUDIO_TS_IP
      access_token: !secret studio_ha_token
```

### Schritt 3: Alois auf User herabstufen
```
HA Stockenweiler → Einstellungen → Personen → Alois Prinz
→ Gruppe: Benutzer (NICHT Administrator)
Wolf: Administrator (für Fernwartung)
```

### Schritt 4: Grafana Node Exporter auf allen Nodes
```bash
# Auf jedem PVE: Node Exporter bereits auf frawo-docker-1 aktiv
# Neu: stockenweiler-pve + studio nach Einrichtung
```

---

## Migrations-Reihenfolge

1. **HP ProDesk einschalten** (Stockenweiler, an Easybox) → Tailscale reconnect
2. **PVE auf HP ProDesk** aufsetzen (falls nicht schon drauf)
3. **HAOS VM** auf HP ProDesk anlegen
4. **Alois User** anlegen, Admin entfernen
5. **Tailscale HA-Addon** auf allen Instanzen
6. **remote_homeassistant** konfigurieren
7. **FraWo Studio Hardware** beschaffen + aufsetzen

---

## Kosten-Schätzung

| Posten | Kosten |
|--------|--------|
| RPi 5 für Studio (Optional) | ~80€ |
| Tailscale (kostenlos bis 100 Geräte) | 0€ |
| HA (Open Source) | 0€ |
| HP ProDesk (bereits vorhanden) | 0€ |
| **Gesamt** | **~0-80€** |

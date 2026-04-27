# Surface Control Architecture - KORRIGIERT

**Last Updated**: 2026-04-27
**Status**: Architektur-Klarstellung

## ✅ RICHTIGE Architektur - 3 Knoten, EINE Instanz

### Das tatsächliche Setup:

```
┌─────────────────────────────────────────────────────────────┐
│  Surface Control V2 (EINE Code-Instanz)                    │
│  Läuft auf: Surface Go Frontend (mobiler Zugriffspunkt)    │
└─────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Stock    │    │ Anker    │    │ Mobile   │
    │ Server   │    │ Server   │    │ Funk Pi  │
    └──────────┘    └──────────┘    └──────────┘
    Hauptlast       Upload/Musik    Mobiler Node
```

## Die drei Service-Knoten (NICHT drei Surface-Instanzen!)

### 1. **Stockenweiler Server** (Hauptlast)
**Rolle**: Primary Production Services
**Standort**: Stockenweiler
**IP**: `192.168.178.0/24` Netzwerk

**Services:**
- **VM 210**: AzuraCast Radio (192.168.178.210) - **LIVE**
  - Radio4yourparty
  - 320kbps MP3 Stream
  - 283GB Musikbibliothek
  - Liquidsoap + Icecast
- **VM 360**: Home Assistant (Eltern-Support)
- Weitere Services nach Bedarf

**Zweck**:
- Trägt die Hauptlast
- Immer online
- Stabile Infrastruktur

### 2. **Anker Server** (Upload/Musikverwaltung)
**Rolle**: Content Management & Upload Node
**Standort**: Anker (primärer Wohnort)
**IP**: `10.1.0.0/24` Netzwerk

**Services:**
- CT 100 Toolbox (10.1.0.20)
- CT 110 Storage Node (10.1.0.30) - SMB/NFS
- Nextcloud für Upload
- Musikverwaltung
- Paperless Eingang

**Zweck**:
- Dokumente hochladen (Nextcloud → Paperless)
- Musik hochladen/organisieren
- Zentrale Speicherverwaltung

### 3. **Mobile Funk Pi** (Mobiler Knoten)
**Rolle**: Mobile Radio Station
**Hardware**: Raspberry Pi 4
**IPs**:
- Legacy: 192.168.2.155
- VLAN: 10.3.0.10
- Tailscale: 100.64.23.77
**Status**: **OFFLINE** (physischer Zugriff erforderlich)

**Geplante Services:**
- AzuraCast (frawo-funk Station)
- Mobile DJ-Station
- Event-Radio
- Backup Radio Node

**Zweck**:
- Mobil einsetzbar
- Unabhängig vom Hauptserver
- Events, Parties, externe Locations

## Surface Go Frontend (DER Zugriffspunkt)

**EINE Surface-Instanz**, die auf **ALLE DREI Knoten** zugreift:

```
Surface Go @ Anker
├── Netzwerk: Wechselnd (Anker/Stockenweiler/Mobil via Tailscale)
├── User: frontend (Kiosk Mode)
└── Firefox Kiosk → http://localhost:17827

    Surface Control V2 zeigt:
    ├── Dokumente → Anker Server (Nextcloud, Paperless)
    ├── Odoo → Anker Server (10.1.0.22)
    ├── Radio Stock → Stockenweiler Server (192.168.178.210)
    ├── Radio Anker → Mobile Funk Pi (10.3.0.10) - wenn online
    └── System → Anker Server (Portal, Vault, HA, Jellyfin)
```

## Intelligente Service-Routing-Logik

Die **EINE Surface Control Instanz** muss wissen, welcher Knoten wo ist:

### Service-zu-Knoten-Mapping:

```javascript
const serviceNodes = {
  // Anker Server Services (10.1.0.0/24)
  dokumente: {
    nextcloud: 'http://cloud.hs27.internal',
    paperless: 'http://paperless.hs27.internal'
  },
  odoo: {
    primary: 'http://odoo.hs27.internal',
    direct: 'http://10.1.0.22:8069'
  },
  system: {
    portal: 'http://portal.hs27.internal',
    vault: 'http://vault.hs27.internal',
    ha: 'http://ha.hs27.internal',
    jellyfin: 'http://media.hs27.internal'
  },

  // Stockenweiler Server Services (192.168.178.0/24)
  radioStock: {
    player: 'http://192.168.178.210/public/radio.yourparty',
    control: 'http://192.168.178.210/login',
    api: 'https://192.168.178.210/api/station/1/nowplaying',
    fallback_dns: 'http://radio-stock.hs27.internal'  // wenn DNS deployed
  },

  // Mobile Funk Pi Services (10.3.0.10 / Tailscale)
  radioMobile: {
    player: 'http://radio-anker.hs27.internal/public/frawo-funk',
    control: 'http://radio-anker.hs27.internal/login',
    direct: 'http://10.3.0.10',
    tailscale: 'http://100.64.23.77',
    status: 'OFFLINE'  // Aktuell
  }
};
```

## Netzwerk-Topologie

### Surface Go kann in 3 Netzwerken sein:

**1. @ Anker (Hauptstandort)**
```
Surface Go (192.168.2.154)
  └── UCG Ultra (10.1.0.1)
      ├── Anker Services (10.1.0.0/24) ✅ Direkt
      ├── Stock Services (via Tailscale) ✅ Bridge
      └── Mobile Pi (10.3.0.10) ❌ Offline
```

**2. @ Stockenweiler (Besuch)**
```
Surface Go (192.168.178.XXX)
  └── Stockenweiler Router
      ├── Stock Services (192.168.178.0/24) ✅ Direkt
      ├── Anker Services (via Tailscale) ✅ Bridge
      └── Mobile Pi (via Tailscale) ❌ Offline
```

**3. @ Mobil/Event (mit Pi)**
```
Surface Go (Tailscale only)
  └── Tailscale Mesh
      ├── Mobile Pi (100.64.23.77) ✅ Direkt
      ├── Anker Services (via Tailscale) ✅ Bridge
      └── Stock Services (via Tailscale) ✅ Bridge
```

## Site-Detection Logic (Automatisch)

```javascript
async function detectCurrentSite() {
  // Versuch 1: Anker-spezifischer Service
  try {
    await fetch('http://10.1.0.20', { method: 'HEAD', timeout: 2000 });
    return {
      site: 'anker',
      network: '10.1.0.0/24',
      services: {
        anker: 'direct',
        stock: 'tailscale',
        mobile: 'offline'
      }
    };
  } catch {}

  // Versuch 2: Stockenweiler-spezifischer Service
  try {
    await fetch('http://192.168.178.210', { method: 'HEAD', timeout: 2000 });
    return {
      site: 'stockenweiler',
      network: '192.168.178.0/24',
      services: {
        anker: 'tailscale',
        stock: 'direct',
        mobile: 'offline'
      }
    };
  } catch {}

  // Versuch 3: Nur Tailscale (mobil/event)
  try {
    await fetch('http://100.64.23.77', { method: 'HEAD', timeout: 2000 });
    return {
      site: 'mobile',
      network: 'tailscale',
      services: {
        anker: 'tailscale',
        stock: 'tailscale',
        mobile: 'direct'
      }
    };
  } catch {}

  return {
    site: 'unknown',
    network: 'isolated',
    services: {
      anker: 'unavailable',
      stock: 'unavailable',
      mobile: 'unavailable'
    }
  };
}
```

## Workflow-Beispiele

### Beispiel 1: Dokument hochladen @ Anker
```
Surface Go @ Anker
  → Click "Nextcloud Eingang"
  → http://cloud.hs27.internal (Anker Server)
  → Upload Rechnung.pdf
  → Paperless processed auf Anker Server
```

### Beispiel 2: Radio hören @ Stockenweiler
```
Surface Go @ Stockenweiler
  → Click "Radio4yourparty"
  → http://192.168.178.210 (Stock Server, direkt)
  → 320kbps Stream läuft
```

### Beispiel 3: Mobile DJ-Session @ Event
```
Surface Go @ Event (via Tailscale)
  → Click "Radio Anker" (Mobile Pi)
  → http://100.64.23.77 (Tailscale)
  → frawo-funk Stream für Event
  → Musik-Upload via Tailscale zu Anker
```

## Datenfluss: Musik-Upload

```
1. Neue Musik hochladen:
   Surface Go → Nextcloud (Anker) → /Musik/Incoming

2. Musik organisieren:
   Anker Storage Node (CT 110) → SMB Share

3. Sync zu Radio Nodes:
   Option A: Anker Storage → rsync → Stock Radio VM
   Option B: Beide mounten gleichen SMB-Share
   Option C: Stock Radio mounted Anker NFS via Tailscale

4. Radio playlists aktualisieren:
   Stock Radio: Scannt SMB-Mount
   Mobile Pi: Scannt lokales oder gemountetes Verzeichnis
```

## Best Practice: Service-Verfügbarkeit

### Kritische Services (müssen immer erreichbar sein):
- **Odoo** → Anker (Hauptarbeit)
- **Nextcloud** → Anker (Upload)
- **Vault** → Anker (Passwörter)

### Entertainment Services (nice-to-have):
- **Radio Stock** → Stockenweiler (Hauptlast)
- **Radio Mobile** → Pi (Events/Backup)
- **Jellyfin** → Anker (Media)

### Fallback-Strategie:
```javascript
const radioEndpoints = {
  // Primär: Stock Server (immer online)
  primary: 'http://192.168.178.210',

  // Sekundär: Mobile Pi (wenn online)
  secondary: 'http://radio-anker.hs27.internal',

  // Fallback: Direkte IPs
  stock_direct: 'http://192.168.178.210',
  mobile_direct: 'http://10.3.0.10',
  mobile_tailscale: 'http://100.64.23.77'
};

// Auto-select verfügbaren Radio-Node
async function getAvailableRadio() {
  for (const [name, url] of Object.entries(radioEndpoints)) {
    if (await isReachable(url)) {
      return { name, url, node: name.includes('stock') ? 'stock' : 'mobile' };
    }
  }
  return null; // Kein Radio verfügbar
}
```

## Deployment

### Eine Surface Control Instanz = Ein Deployment:

```bash
# Deployment auf Surface Go @ Anker
ansible-playbook ansible/playbooks/deploy_surface_control.yml -l surface_go_anker

# Surface Control HTML beinhaltet:
# - Service URLs für ALLE DREI Knoten
# - Auto-Detection Logic
# - Fallback-Routing
# - Now-Playing Widget (Stock Radio)
```

### Kein Multi-Device Deployment nötig!

**FALSCH**: ❌ Drei Surface-Instanzen (eine pro Knoten)
**RICHTIG**: ✅ Eine Surface-Instanz (greift auf drei Knoten zu)

## Zusammenfassung der Korrektur

### Was ich falsch verstanden hatte:
- ❌ Drei Surface Go Devices
- ❌ Drei separate Control Surface Instanzen
- ❌ Multi-Device Deployment

### Was tatsächlich ist:
- ✅ **EINE** Surface Go (mobil einsetzbar)
- ✅ **DREI** Service-Knoten (Stock, Anker, Mobile Pi)
- ✅ Surface Control greift auf alle drei Knoten zu
- ✅ Intelligentes Routing je nach Standort/Verfügbarkeit

### Die Knoten-Rollen:

1. **Stockenweiler Server**: Heavy Lifting (Radio Hauptlast, HA Eltern)
2. **Anker Server**: Content Management (Upload, Musik, Dokumente, Odoo)
3. **Mobile Funk Pi**: Mobile Operations (Events, DJ, Backup)

### Surface Go:
- Mobiler **Zugriffspunkt**
- Kann überall sein (Anker/Stock/Mobil)
- **EINE** Instanz mit intelligentem Routing

## Nächste Schritte (Korrigiert)

1. ✅ Site-Detection in surface_index_v2 einbauen
2. ✅ Multi-Node Service-URLs konfigurieren
3. ✅ Fallback-Logic für Radio (Stock primary, Mobile secondary)
4. ✅ Ansible Playbook für EINE Surface (nicht drei)
5. ✅ Auto-Update via Git Pull

**Macht das jetzt Sinn?** 🎯

- Eine Surface, drei Service-Knoten
- Intelligentes Routing je nach Netzwerk
- Stock = Hauptlast, Anker = Upload/Musik, Mobile = Events

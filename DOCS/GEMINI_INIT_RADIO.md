# Gemini Init Prompt - FraWo Funk Radio Setup

## Deine Aufgabe
Du bist ausschließlich für **FraWo Funk (Radio)** zuständig.
Claude kümmert sich parallel um die **Website (frawo-tech.de)**.

## Aktueller Status

### Radio Infrastructure
- **Domain**: funk.frawo-tech.de
- **Software**: AzuraCast (Docker-basiert)
- **Server**: Proxmox Container oder VM (Details in RADIO_STATUS_2026-05-13.md)
- **Zugriff**: Tailscale VPN erforderlich

### Letzte Checks (2026-05-13)
```
Status: OFFLINE
- funk.frawo-tech.de → Connection refused
- AzuraCast Container/Service nicht erreichbar
- Proxmox Anker: Online (10.4.0.20)
- Proxmox Stockenweiler: Offline
```

## Deine Ziele (Reihenfolge)

### 1. Radio-Service wieder online bringen
- [ ] Proxmox VPN-Zugriff verifizieren
- [ ] AzuraCast Container/VM Status prüfen
- [ ] AzuraCast neu starten falls nötig
- [ ] funk.frawo-tech.de DNS/Proxy prüfen
- [ ] SSL-Zertifikat verifizieren

### 2. AzuraCast Grundkonfiguration
- [ ] Station-Name: "FraWo Funk"
- [ ] Beschreibung: "Community Radio. Bodensee."
- [ ] Genre: Electronic / Alternative / Community
- [ ] Bitrate: 128kbps MP3 (Minimum)
- [ ] Mount Point: /radio oder /stream

### 3. Web-Player Integration
- [ ] Embedded Player HTML für frawo-tech.de erstellen
- [ ] Player Design: Dark Theme, minimal (wie NTS Radio)
- [ ] "Now Playing" API-Integration
- [ ] Mobile-responsive

### 4. Content Setup
- [ ] Playlist-Struktur definieren
- [ ] Upload-Workflow für Musik
- [ ] Automation: Fallback-Playlist
- [ ] Optional: DJ Live-Streaming Setup

## Wichtige Infos

### FraWo CI Colors (für Player Design)
```css
--fw-bg: #0a0a0a;        /* Background */
--fw-text: #e0e0e0;      /* Text */
--fw-uv: #a855f7;        /* Purple Accent */
--fw-border: #1a1a1a;    /* Borders */
```

### Credentials Location
```
~/.ai-tools-shared/.env
```
Enthält:
- ODOO_URL, ODOO_USER, ODOO_PASSWORD (NICHT für dich!)
- Proxmox/Tailscale Zugänge (wenn vorhanden)

### DO NOT TOUCH
- ❌ Odoo Website (10.1.0.112:8069)
- ❌ frawo-tech.de HTML/CSS
- ❌ GitHub Repo außer `/DOCS/RADIO_*` Files
- ❌ Alles was mit "Veranstaltungstechnik" zu tun hat

### Kommunikation
- Schreibe Status-Updates in `/DOCS/RADIO_STATUS_YYYY-MM-DD.md`
- Bei Fragen zu Website/Odoo: "Frag Claude"
- Bei Infrastruktur-Konflikten: User entscheidet

## Nächste Schritte

1. Lies `RADIO_STATUS_2026-05-13.md` für letzten Zustand
2. Prüfe Tailscale/VPN-Zugang
3. Checke Proxmox Container-Status
4. Erstelle neuen Status-Report

## Radio-Philosophie (User-Vorgaben)
- "Radio ist Gadget, nicht Kerngeschäft"
- Community-Fokus, keine kommerzielle Nutzung
- Musikförderung, lokale Künstler
- Simple, zuverlässige Lösung
- Kein Overengineering

## Erfolg =
✅ funk.frawo-tech.de spielt Musik
✅ Player auf frawo-tech.de integriert (Section "FraWo Funk")
✅ "Now Playing" funktioniert
✅ Stabil, wartungsarm

---

**Start hier:** Prüfe Proxmox-Zugang und AzuraCast-Status.

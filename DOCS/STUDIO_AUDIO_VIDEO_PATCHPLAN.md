# Studio Audio & Video Signalplan / Patchplan

Systematischer Signal- & Geräteplan für Studio & Live-Curation (Tasks #105–#107).

---

## 🎙️ 1. Audio Signal Flow (FOH & Studio)

```
[Mikrofone / DJ Deck] ──(XLR / Line)──> [Yamaha MG12XU Mischpult]
                                              │
                         ┌────────────────────┴────────────────────┐
                         ▼                                         ▼
            [Crown CT 2000 Endstufe]                     [StudioPC Audio In / USB]
                         │                                         │
                         ▼                                         ▼
         [KMT CS-215 / Subwoofer Tops]               [AzuraCast Stream / AzuraCast API]
```

## 🎥 2. Video & Stream Routing
- **Video Interfaces:** NDI / HDMI Capture an StudioPC (`10.1.0.211`).
- **Kiosk Stream:** Surface Go Kiosk Terminal ([`/kiosk`](http://10.1.0.112:8069/kiosk)) greift auf den AzuraCast Live Player zu.

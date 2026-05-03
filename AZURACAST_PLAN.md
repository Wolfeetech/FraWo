# AzuraCast Implementation Plan (V1.1 Technical Blueprint)

## Lane E: Radio & Media

### 1. Standort-Strategie
*   **Primär-Node:** Stockenweiler VM 210 (`192.168.178.210`).
*   **Relay/Backup:** Anker Node (LXC im CT 100 Kontext).
*   **Konnektivität:** Tailscale Mesh (Inter-Site Bridge).

### 2. Media-Synchronisation (SSOT)
*   **Quelle:** StudioPC / Anker Storage Node (`10.1.0.30`).
*   **Ziel:** Stockenweiler Radio-Library.
*   **Tooling:** `rclone sync` mit `--bwlimit`.
*   **Automatisierung:** Crontab auf VM 210 oder via OpenClaw Agent Task.

### 3. Icecast & Relay
*   Konfiguration eines Icecast Relays auf dem Anker-Standort.

### 4. Odoo Integration
*   Synchronisation der Supporter-Datenbank.

---
**Status:** In technischer Prüfung (Remediation läuft...)
**Kritische Warnung:** Stockenweiler Swap 99% - Bereinigung eingeleitet.
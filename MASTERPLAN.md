# MASTERPLAN - FraWo Homeserver 2027

Dieses Dokument ist das zentrale Strategiepapier fuer den Aufbau und Betrieb des FraWo Homeservers 2027 (Standort: Anker und Stockenweiler). Es definiert die Lanes, den technologischen Standard und die Freigabemechanismen.

---

## 1. Vision & Strategie
Der Homeserver 2027 dient als produktive Basis fuer die **FraWo GbR**. Er konsolidiert alle Business-Applikationen (ERP, Cloud, Dokumente) und Sicherheitsinfrastrukturen (Vault, Backups) an zwei Standorten. Der Fokus liegt auf radikaler Stabilisierung, Skalierbarkeit und einer professionellen Operator-Erfahrung.

---

## 2. Work Lanes (Roadmap)

### Lane A: MVP Pilot (Release Gate) - **[STATUS: SEALED]**
Der Kern-Arbeitsplatz fuer Wolf und Franz. Alle Basis-Apps sind ueber HTTPS erreichbar. Die Infrastruktur ist dokumentiert und das `release_mvp_gate` ist bestanden.
- **Ziel**: Stabiler Betrieb fuer ERP (Odoo), Cloud und Vault.
- **Status**: **ABGESCHLOSSEN (2026-04-20)**.

### Lane B: Website & Public Activation - **[STATUS: ACTIVE]**
Exponierung der FraWo-Webseite (`www.frawo-tech.de`) an das Internet via Cloudflare Tunnel.
- **Ziel**: Sichtbarkeit nach Aussen, professionelle Mail-Zustellung (SPF/DKIM/DMARC).
- **Status**: **IN VORBEREITUNG**. Odoo-Config bereit, Tunnel-Token fehlt.

### Lane C: Security, PBS & Infrastructure - **[STATUS: ACTIVE]**
Sicherung des MVP durch Proxmox Backup Server (PBS) und Speicher-Optimierung.
- **Ziel**: Reduzierung des Speicherdrucks (<80%) und automatisierte Life-Cycle-Backups.
- **Status**: **IN DURCHFUEHRUNG**. Snapshots bereinigt, PBS GC gestartet.

### Lane D: Stockenweiler Integration
Standort-Koppelung und Site-to-Site VPN fuer den zweiten Knoten.
- **Ziel**: Nahtloser Zugriff auf `stock-pve` und Remote-Backup-Sync.

---

## 3. Infrastruktur & Routing

### Netzwerk-Wahrheit (UCG Ultra)
Das Netzwerk folgt dem UCG-Standard `10.1.0.0/24`. DNS-Aufloesung erfolgt am Standort Anker ueber AdGuard (CT 100).

| Dienst | Interner Host | Port | HTTPS | IP (UCG) |
| :--- | :--- | :--- | :--- | :--- |
| **Portal** | `portal.hs27.internal` | 8447 | Ja | 10.1.0.20 |
| **Odoo** | `odoo.hs27.internal` | 8069 | Ja | 10.1.0.22 |
| **Cloud** | `cloud.hs27.internal` | 443 | Ja | 10.1.0.21 |
| **Vault** | `vault.hs27.internal` | 443 | Ja | 10.1.0.20 |
| **Paperless** | `paperless.hs27.internal`| 443 | Ja | 10.1.0.23 |

---

## 4. Operational Insights

### Workstation-Routing Fix (WolfStudioPC)
- Auf `wolfstudiopc` war ein echter Routing-Fehler aktiv: Tailscale hat das von `toolbox` annoncierte Subnetz `192.168.2.0/24` akzeptiert und damit den direkten LAN-Pfad auf diesem PC uebersteuert.
- Der Workstation-Fix ist gesetzt: `tailscale set --accept-routes=false`.
- Damit ist die lokale Route auf diesem Admin-PC wieder priorisiert.
- Wenn Legacy-Pfade unter `192.168.2.x` trotzdem nicht sauber antworten, ist das als Infrastrukturpfad-Thema zu behandeln, nicht vorschnell als App-Defekt.

### Live-Stand nach Restoration (2026-04-20)

> [!NOTE]
> **Core System Sealed.** The infrastructure has been successfully cleared of old snapshot data following the 84% storage pressure incident. The system is stable.

- `VM 220 odoo`: LIVE auf `10.1.0.22:8069`. Database `FraWo_GbR` active. Public-Edge Ready.
- `VM 200 nextcloud`: LIVE auf `10.1.0.21`.
- `VM 230 paperless`: LIVE auf `10.1.0.23`.
- `VM 210 haos`: LIVE auf `10.1.0.24:8123`.
- `CT 100 toolbox`: LIVE auf `10.1.0.20`; mobile Frontdoor und Split-DNS laufen ueber `100.82.26.53`.
- `CT 110 Storage-Node`: LIVE. SMB Source of Truth verified.
- **ACTIVE: Lane B Deployment** (Public Edge / HTTPS / Tunnel).

### Bewusst getrennt oder aktuell blockiert
- **Radio-Node**: Aktuell Offline. Physische Intervention in Stockenweiler erforderlich.
- **Public Website**: Blockiert durch fehlenden Cloudflare-Token.

---

## 5. Governance & Handoff
Dieses Dokument wird bei jeder signifikanten Aenderung (Lane-Wechsel, Major-Fix) aktualisiert. Handoffs zwischen Agenten (Antigravity -> Claude) muessen zwingend auf diesem Masterplan basieren.

-- **End of Masterplan** --

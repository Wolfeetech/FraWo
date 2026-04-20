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

<<<<<<< HEAD
### Node 0: Lead (Admin Orchestrator & SSOT)
- `wolfstudiopc` (100.98.31.60): **Primärer Lead-Knoten**. Alle Änderungen werden hier zentral konsolidiert. Andere Geräte (z.B. Surface) fungieren als Remote-Satelliten.

### Node 1: Anker (Business, Automation & AI Layer)
- `VM 220 odoo`: Zentrale ERP- und FraWo-Website-Instanz.
- `VM 200 nextcloud`: Zusammengelegte, Single-Source Dokumenten-Instanz.
- `VM 230 paperless`: Zusammengelegtes, zentrales Dokumentenarchiv.
- `CT 300 n8n`: Automatisierungs-Backend fuer Workflow-Pipelines.
- `VM 310 openclaw`: Isoliertes, sicheres AI-Agent-Environment fuer Vibecoding.
- `CT/VM 211 haos-edge`: Zusaetzliche HA-Ebene zur Steuerung am Anker-Standort.

### Node 2: Stockenweiler (Media, Backup & IoT Lifeboat)
- `VM 210 haos`: Zentrale Smart-Home-Steuerung fuer das Elternhaus.
- `CT 100 media`: Strukturierte Medien-Ebene (AzuraCast, Jellyfin, Media-HDD).
- `CT/VM pbs`: Zentraler Proxmox Backup Server (Anker-Instanz wird obsolet).

### Hardware & Peripherie
- `wolfstudiopc`: **LEAD** Admin-Geraet & SSOT.
- `surface-franz`: Remote-Arbeitsgerät (Satellite).
- `surface-wolfi` (Admin): Remote-Arbeitsgerät (Satellite).
- `kiosk-frontend`: Touch-Kiosk fuer Franz und Wolf (Rebuild offen).
- `zenbook_radio_anchor`: Zukuenftiger Radio-Ankerpunkt.
- `raspberry_pi_radio`: Dedizierter AzuraCast-Node.
- `iphone-15`: Mobiles Primaergeraet Franz.
- `pixel-9-pro`: Mobiles Primaergeraet Wolf.
- `UniFi Cloud Gateway Ultra`: Netzwerkkontrollpunkt & VLANs.

## Professioneller Zielstandard


Der Server gilt erst dann als wirklich fertig, wenn alle folgenden Punkte erfuellt sind:

1. Alle Zielsysteme sind gebaut, dokumentiert und reproduzierbar ueber IaC pflegbar.
2. Inventar, IP-Plan, Hostrollen und Verantwortlichkeiten sind eindeutig.
3. Interne Erreichbarkeit laeuft kontrolliert ueber DNS, Reverse Proxy und Tailscale.
4. Backups sind nicht nur konfiguriert, sondern mit Restore-Drills praktisch bewiesen.
5. Sicherheitsbasis ist nachweisbar:
   - keine unnoetigen Admin-Flaechen im LAN
   - keine offenen Datenbankports
   - keine direkte Internet-Exposition von Admin-UIs
   - saubere Snapshot- und Rollback-Pfade
6. Der Netzrand ist kontrolliert:
   - Easy Box nur Uebergang
   - spaeter UCG-Ultra mit geplantem Cutover
7. Oeffentliche Freigaben passieren nur ueber einen gehaerteten Edge-Pfad mit DNS, TLS, Auth, Logging und Monitoring.

## Operator Shortcuts

- Operator Home: `OPS_HOME.md`
- Executive Roadmap: `EXECUTIVE_ROADMAP.md`
- Gesamtstatus: `PLATFORM_STATUS.md`
- Identitaetsstandard: `IDENTITY_STANDARD.md`
- Tool-Betriebsanweisungen: `OPERATIONS/TOOLS_OPERATIONS_INDEX.md`
- Vaultwarden-Referenzregister: `ACCESS_REGISTER_VAULTWARDEN_REFERENCES.md`
- Business-MVP-Gate: `artifacts/release_mvp_gate/.../release_mvp_gate.md`
- Website-Release-Gate: `artifacts/website_release_gate/.../website_release_gate.md`
- Release-Akte: `RELEASE_READINESS_2026-04-01.md`
- Mail-Rollout: `MAIL_SYSTEM_ROLLOUT.md`
- Vaultwarden + STRATO Uebergang: `BITWARDEN_STRATO_EXECUTION_RUNBOOK.md`
- Mobile-Scan-Workflow: `MOBILE_SCAN_WORKFLOW.md`
- Stress-Test-Readiness: `STRESS_TEST_READINESS.md`
- Stockenweiler / Rentner OS: `STOCKENWEILER_REMOTE_SUPPORT_PLAN.md`
- Anker + Stockenweiler Gesamtpfad: `ANKER_STOCKENWEILER_MARRIAGE_PLAN.md`
- AI-Arbeitsmodell: `AI_OPERATING_MODEL.md`
- Hosting-Optionen: `ONLINE_HOSTING_OPTIONS.md`
- Google-Drive-Plan: `GOOGLE_DRIVE_INTEGRATION_PLAN.md`
- Odoo-Studio-Entscheidung: `ODOO_STUDIO_DECISION.md`
- 2-TB-SSD-Bewertung: `TB_SSD_ASSESSMENT.md`

## 4. Operational Insights

### Workstation-Routing Fix (WolfStudioPC)
- Auf `wolfstudiopc` war ein echter Routing-Fehler aktiv: Tailscale hat das von `toolbox` annoncierte Subnetz `192.168.2.0/24` akzeptiert und damit den direkten LAN-Pfad auf diesem PC uebersteuert.
- Der Workstation-Fix ist gesetzt: `tailscale set --accept-routes=false`.
- Damit ist die lokale Route auf diesem Admin-PC wieder priorisiert.
- Wenn Legacy-Pfade unter `192.168.2.x` trotzdem nicht sauber antworten, ist das als Infrastrukturpfad-Thema zu behandeln, nicht vorschnell als App-Defekt.

### Live-Stand nach Restoration (2026-04-20)

> [!NOTE]
> **Core System Sealed.** The infrastructure has been successfully cleared of old snapshot data following the 84% storage pressure incident. The system is stable. MTU auf 1280 gehaertet.

- `VM 220 odoo`: LIVE auf `10.1.0.22:8069`. Database **`FraWo_GbR`** active. Public-Edge Ready.
- `VM 200 nextcloud`: LIVE auf `10.1.0.21`.
- `VM 230 paperless`: LIVE auf `10.1.0.23`.
- `VM 210 haos`: LIVE auf `10.1.0.24:8123`.
- `CT 100 toolbox`: LIVE auf `10.1.0.20`; mobile Frontdoor und Split-DNS laufen wieder ueber `100.82.26.53`. 
- **ACTIVE: Lane C & E Cleanup** (Node.js/Claude Code installed, Hue Bridges identified).
- **FIXED**: Odoo "Endless Loading" solved via MTU Alignment (2026-04-20).
- `CT 110 Storage-Node`: LIVE. SMB Source of Truth verified.
- **ACTIVE: Lane B Deployment** (Public Edge / HTTPS / Tunnel).

### Bewusst getrennt oder aktuell blockiert
- **Radio-Node**: Aktuell Offline. Physische Intervention in Stockenweiler erforderlich.
- **Public Website**: Blockiert durch fehlenden Cloudflare-Token.

---

## 5. Governance & Handoff
Dieses Dokument wird bei jeder signifikanten Aenderung (Lane-Wechsel, Major-Fix) aktualisiert. Handoffs zwischen Agenten (Antigravity -> Claude) muessen zwingend auf diesem Masterplan basieren.

-- **End of Masterplan** --

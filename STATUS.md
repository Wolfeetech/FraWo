# Aktueller Status & Praxis-Scan (Stand: 20.05.2026)

Dieses Dokument beschreibt den **tatsächlich getesteten und diagnostizierten** Zustand des Systems.

---

## 1. Was wirklich läuft und getestet wurde (Fakten)

### 🌍 Website & Domain
- **`https://www.frawo-tech.de/`**: **ERREICHBAR** und funktional.
- **`https://frawo-tech.de/` (ohne www)**: **ERREICHBAR**.
  - Der mobile Button-Wrap in `frawo_custom_css.css` wurde behoben, eingecheckt und gepusht.

### 🖥️ Odoo Server & SSOT Consolidation
- **IP `10.4.0.22`**: **ERREICHBAR** (Ping erfolgreich, <1ms).
- **Zentrales SSOT-Board**: **VOLLSTÄNDIG AKTIVIERT** und konsolidiert.
  - Alle 85+ Aufgaben aus allen separaten Projekten wurden in das zentrale Projekt **`🚀 Homeserver 2027: Masterplan`** migriert.
  - Alle Aufgaben sind mit Lane-Tags (z.B. `Lane A: MVP`, `Lane B: Website`, etc.) versehen.
  - Aufgaben besitzen klare visuelle Indikatoren und Zuweisungen:
    - **`[🤖 AGENT]`** zugewiesen an `agent@frawo-tech.de` (Infrastruktur, Automation).
    - **`[👤 WOLF]`** zugewiesen an `wolf@frawo-tech.de` (Physik, Verträge, manuelle Aufgaben).
    - **`[👤 FRANZ]`** zugewiesen an `franz@frawo-tech.de` (Villa Bienert Stream/Audio-Projekte).
  - Unnötige/leere Projekt-Boards wurden archiviert, um die Benutzeroberfläche sauber zu halten.
- **Dokumentations-Backup in Odoo**: **VOLLSTÄNDIG SYNCED**.
  - Die Dateien `MASTERPLAN.md`, `LIVE_CONTEXT.md` und `STATUS.md` wurden als HTML formatiert und in den Task **`📚 System-Dokumentation & SSOT (Masterplan, Live-Context, Status)`** injiziert.
  - Die Originaldateien sind zudem als binäre Dateianhänge direkt an der Aufgabe in Odoo gesichert.

### 🌐 Netzwerk-Stabilität & Diagnose
- **Netzwerk-Ausfall Root Cause**: **UDP PORT EXHAUSTION (Event 4266) gelöst**.
  - Der Server lief durch das gleichzeitige Flapping von VPN- und Tunnel-Diensten (Tailscale, Netbird, Cloudflared) über zwei aktive Gateways (WLAN zu Easybox `192.168.2.1` für Shellys und LAN zu UCG `10.1.0.1`/`10.4.0.1`) in einen Socket-Leak.
  - **Empfehlung für Windows-Port-Optimierung (als Administrator ausführen):**
    ```powershell
    # Dynamic Port Limit auf Maximum anheben
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name 'MaxUserPort' -Value 65534 -Type DWord
    
    # TIME_WAIT Socket-Haltezeit auf 30 Sekunden reduzieren
    Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' -Name 'TcpTimedWaitDelay' -Value 30 -Type DWord
    ```

---

## 2. Was unvollständig oder fehlerhaft ist

### 🔴 Stockenweiler Server
- **SSH `stock-pve` (100.91.20.116)**: **NICHT ERREICHBAR** (physisch ausgeschaltet).
  - **Fazit:** Ein Besuch vor Ort in Rothkreuz ist zwingend erforderlich, um den Host physisch einzuschalten.
  - **Odoo-Aktion:** Es wurde eine prioritäre Aufgabe **`[👤 WOLF] 🔌 Stockenweiler PVE physisch einschalten (Rothkreuz vor Ort)`** erstellt und Wolf zugewiesen. Alle davon abhängigen Aufgaben (Radio-Node, Backup-Sync, HA Eltern) wurden in die Stage `🛑 Blockiert` verschoben.

### ⚠️ Cloudflare Security Headers
- Die "Transform Rules" (Schritt 4 der Anleitung) für die Sicherheits-Header in Cloudflare sind noch nicht eingerichtet.

---

## 3. Nächste Schritte

1. **Stockenweiler PVE physisch einschalten** (Wolf vor Ort in Rothkreuz).
2. **Windows Registry-Optimierung anwenden** (Wolf im Administrator-Terminal).
3. **Cloudflare Transform Rules einrichten** (Agent & Wolf gemeinsam).
4. **Schritt-für-Schritt Abarbeitung der Lanes** direkt über das Odoo-Zentralboard.

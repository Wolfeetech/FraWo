# Master-Mapping: IST-Zustand (Network & Security)

Letzte Aktualisierung: 2026-04-05 (Ops Key Recovery)

## 1. Topologie-Uebersicht

| Hostname | IP (Tailscale) | OS / Typ | Status | SSH-Zugriff | Rolle |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Surface-IHL** | 100.79.103.59 | Win 11 | ONLINE | Local | **Mobile Unit (Admin-Konsole)** |
| **proxmox-anker** | 100.69.179.87 | Proxmox | ONLINE | **ERFOLGREICH** (root) | PVE Cluster FraWo (Haupt) |
| **pve** | 100.91.20.116 | Proxmox | ONLINE | **Tailscale-SSH/Port 22 + Web erreichbar** | PVE Cluster Stockenweiler |
| **toolbox** | 100.99.206.128 | Linux/LXC | ONLINE | **SSH mit Standard-Ops-Key** | Geplanter Ansible-Knoten |
| **wolfstudiopc** | 100.98.31.60 | Windows | ONLINE | Ping/TS sichtbar, RDP weiter offen | **Homing Node** |

## 2. Sicherheits-Status & Connectivity

- [x] **Tailscale Visibility:** Alle Kernknoten sind im Tailnet sichtbar.
- [x] **SSH-Rollout (Anker):** Login auf `root@proxmox-anker` funktioniert mit dem lokalen Standard-Ops-Key.
- [x] **PVE Connectivity:** `pve` ist via `100.91.20.116` auf `22` und `8006` erreichbar; Port `22` meldet sich derzeit als Tailscale-SSH-Endpunkt.
- [x] **Toolbox Connectivity:** `toolbox` ist via `100.99.206.128:22` direkt per lokalem Standard-Ops-Key erreichbar.
- [ ] **Vaultwarden:** Zugriff steht noch aus.

## 3. Bekannte Probleme ("Chaos-Register")

1.  **wolfstudiopc Isolation:** RDP auf `3389` ist weiterhin nicht bestaetigt; Tailscale-Sichtbarkeit allein reicht noch nicht fuer Remote-Desktop.
2.  **PVE Naming Drift:** Der Kurzname `pve` ist auf diesem Rechner lokal gefixt und zeigt stabil auf `100.91.20.116`. Die SSH- und Web-Starter bevorzugen jetzt den Tailscale-Hostnamen statt des alten WireGuard/LAN-Pfads.
3.  **Ops-Key Standardisierung:** `proxmox-anker` und `toolbox` akzeptieren jetzt denselben lokalen Standard-Ops-Key `Admin@Surface-Work 2025-09-08`.
4.  **PVE SSH Ausnahme:** `pve` meldet auf Port `22` aktuell Tailscale-SSH statt normalen OpenSSH-Zugriffs. Der Tailscale-Pfad bleibt daher dokumentierter Ausnahmefall.
5.  **Ansible-Master:** `toolbox` ist als Runner funktionsfaehig (`ansible`, `python3`, `sshd` aktiv), operative Playbooks sind aber noch nicht weiter ausgebaut.
6.  **Inventory Sync:** `inventory.ini` wurde auf Tailscale-IPs migriert (Backup vorhanden).

## 4. Naechste Schritte (Operational)

1.  **Standardpfad nutzen:** Admin-PC -> `proxmox-anker`/`toolbox` via OpenSSH mit Standard-Ops-Key; `Anker-SSH.cmd` und `Toolbox-SSH.cmd` sind die bevorzugten Einstiege.
2.  **Toolbox als Runner nutzen:** `Toolbox-SSH.cmd` landet direkt auf dem vorbereiteten Debian-12-Runner mit `ansible`.
3.  **DNS ist lokal gefixt:** `pve` und `anker-pve` sind auf diesem Rechner jetzt als stabile Kurz-Aliase hinterlegt.
4.  **PVE Zugriff vereinheitlichen:** `PVE-Web.cmd` und `PVE-SSH.cmd` bevorzugen den Tailscale-Pfad; der Legacy-WireGuard-Weg bleibt nur als Fallback.

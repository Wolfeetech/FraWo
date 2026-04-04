# Master-Mapping: IST-Zustand (Network & Security)

Letzte Aktualisierung: 2026-04-05 (Live Catch-up)

## 1. Topologie-Uebersicht

| Hostname | IP (Tailscale) | OS / Typ | Status | SSH-Zugriff | Rolle |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Surface-IHL** | 100.79.103.59 | Win 11 | ONLINE | Local | **Mobile Unit (Admin-Konsole)** |
| **proxmox-anker** | 100.69.179.87 | Proxmox | ONLINE | **ERFOLGREICH** (root) | PVE Cluster FraWo (Haupt) |
| **pve** | 100.91.20.116 | Proxmox | ONLINE | **Tailscale erreichbar** | PVE Cluster Stockenweiler |
| **toolbox** | 100.99.206.128 | Linux/LXC | ONLINE | **SSH-Port erreichbar** | Geplanter Ansible-Knoten |
| **wolfstudiopc** | 100.98.31.60 | Windows | ONLINE | Ping/TS sichtbar, RDP weiter offen | **Homing Node** |

## 2. Sicherheits-Status & Connectivity

- [x] **Tailscale Visibility:** Alle Kernknoten sind im Tailnet sichtbar.
- [x] **SSH-Rollout (Anker):** Login auf `root@proxmox-anker` wurde bereits erfolgreich verifiziert.
- [x] **PVE Connectivity:** `pve` ist via `100.91.20.116` auf `22` und `8006` erreichbar.
- [x] **Toolbox Connectivity:** `toolbox` ist via `100.99.206.128:22` wieder erreichbar.
- [ ] **Vaultwarden:** Zugriff steht noch aus.

## 3. Bekannte Probleme ("Chaos-Register")

1.  **wolfstudiopc Isolation:** RDP auf `3389` ist weiterhin nicht bestaetigt; Tailscale-Sichtbarkeit allein reicht noch nicht fuer Remote-Desktop.
2.  **PVE Naming Drift:** Der Kurzname `pve` ist auf diesem Rechner lokal gefixt und zeigt stabil auf `100.91.20.116`. Alt-Skripte wurden vom frueheren WireGuard/LAN-Pfad `192.168.178.172` auf Tailscale umgestellt.
3.  **Priority 1 Recovery:** `proxmox-anker` ist wieder auf `22` und `8006` erreichbar, `toolbox` wieder auf `22`.
4.  **Ansible-Master:** `toolbox` ist netzseitig zurueck, als zentraler Runner aber noch nicht finalisiert.
5.  **Inventory Sync:** `inventory.ini` wurde auf Tailscale-IPs migriert (Backup vorhanden).

## 4. Naechste Schritte (Operational)

1.  **Priority 1 nutzen:** `Anker-Web.cmd` bzw. SSH gegen `100.69.179.87` und `Toolbox-SSH.cmd` koennen wieder produktiv verwendet werden.
2.  **Toolbox finalisieren:** SSH-Key-Mapping und Ansible-Rolle auf `toolbox` als naechsten operativen Schritt abschliessen.
3.  **DNS ist lokal gefixt:** `pve` und `anker-pve` sind auf diesem Rechner jetzt als stabile Kurz-Aliase hinterlegt.
4.  **PVE Zugriff vereinheitlichen:** `PVE-Web.cmd` und `PVE-SSH.cmd` nutzen; beide bevorzugen jetzt den Tailscale-Pfad.

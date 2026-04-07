# FACTSHEET CODEX - Homeserver 2027

Dieses Dokument ist die hochverdichtete "Source of Truth" für den Agenten **Codex**. 

## 🤖 Rollenverteilung
- **Codex (Du):** Experte für Code, Logik, Shell-Härtung & direkte Interaktion mit der Toolbox.
- **Gemini/Antigravity (Ich):** Infrastruktur-Audit, SOT-Zentralisierung, Gesamtplanung & Task-Koordination.

## 📁 Workspace-Status (Surface)
- **Local Path:** `c:\Users\Admin\Documents\Private_Networking`
- **Remote Source:** `\\wolfstudiopc\Workspace` (Audit & Migration zu 100% abgeschlossen).
- **Git:** Aktiv auf dem Surface, Branch `main`, User `wwolfitec`.

## 🌐 Netzwerk-Topologie (UCG-Uebergang)
- **Router (Legacy):** `192.168.2.1` (Easy Box)
- **Gateway (UCG-Ultra):** `10.1.0.1` (VLAN 101 aktiv für Anker)
- **Proxmox-Anker:** `10.1.0.92` (Tailscale: `100.69.179.87`)
- **Toolbox (CT 100):** `10.1.0.20` (Tailscale: `100.99.206.128`) - **Dein primäres Arbeitsumfeld**.

### Service-IPs (VLAN 101):
| Service | IP | Port | Status |
| --- | --- | --- | --- |
| Nextcloud | `10.1.0.21` | 80 | Aktiv |
| Odoo | `10.1.0.22` | 8069 | Aktiv (Härtung läuft) |
| Paperless | `10.1.0.23` | 8000 | Aktiv |
| Vaultwarden | `10.1.0.26` | 80 | Aktiv |

## 💼 Business-MVP Status
- **Nextcloud:** SMTP verifiziert, User `frawoadmin`/`frontend` angelegt.
- **Paperless:** SMTP verifiziert, Paperless-Nextcloud-Bridge aktiv.
- **Odoo:** 
  - **SMTP:** `noreply@frawo-tech.de` via `smtp.strato.de`. Härtung (`harden_smtp.sh`) ist deine Aufgabe.
  - **Task-Sync:** [odoo_masterplan_sync.py](file:///c:/Users/Admin/Documents/Private_Networking/odoo_masterplan_sync.py) ist optimiert (Projekte, Tags, Dedup). Ausführung auf Toolbox ausstehend.

## 🛠️ Deine nächsten Code-Aufgaben
1.  **SMTP-Härtung:** Verifiziere `harden_smtp.sh` und `test_odoo_smtp.py`.
2.  **Run Sync:** Bereite `run_sync.sh` für den Import des Masterplans in Odoo vor.
3.  **Caddy:** [fix_caddy_root.py](file:///c:/Users/Admin/Documents/Private_Networking/fix_caddy_root.py) gegen die neuen UCG-IPs prüfen.

## ⚠️ Wichtige Regeln
- Keine Klartext-Passwörter in `.md` Dateien (nur in `ansible/inventory/group_vars/all/vault.yml`).
- Nach Code-Änderungen: Gemini informieren, damit ich den SOT (`MEMORY.md`) aktualisieren kann.

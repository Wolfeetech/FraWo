# Operator Todo Queue

Stand: `2026-05-02`

> **[DEPRECATED]** 
> Odoo (`FraWo_GbR` Datenbank) ist jetzt das **Single Source of Truth (SSOT)** für alle Aufgaben und Projekte.
> Diese Datei dient nur noch als Legacy-Referenz. Aktuelle Tasks, Prioritäten und Lanes sind im Odoo Project Board (Projekt 1: 🚀 Homeserver 2027: Masterplan) zu pflegen und zu synchronisieren.

## Zweck

Diese Datei wurde durch die Odoo Projektverwaltung abgelöst. Laufzeitwahrheit steht im `LIVE_CONTEXT.md` und Odoo, strategische Wahrheit steht im `MASTERPLAN.md`.

## Lane Status

- `Lane A: MVP Closeout` -> `sealed`
- `Lane B: Website/Public` -> `stabilized` (v3.5 Live, CSS fix applied, SEO updated)
- `Lane C: Security/PBS/Infra` -> `active`
- `Lane D: Stockenweiler` -> `active` (Radio/HA Parents)
- `Lane E: Radio/Media` -> `active`

## Manuelle Unblock-Punkte

### `workspace_drift_guard` [WATCH]

- `lane`: `Lane C: Security/PBS/Infra`
- `goal`: Alle Agenten arbeiten dauerhaft im selben FraWo-Projekt und koordinieren ueber Repo-Dateien statt ueber verstreute Workspaces.
- `current_state`: `C:\Users\Admin\Workspace\Repos\FraWo` ist kanonisch; `C:\Users\Admin\Workspace\FraWo` und `C:\WORKSPACE\FraWo` sind Junctions dorthin; Agentenvertrag und Board sind im Repo.
- `next_operator_action`: Alte Fenster/IDE-Sessions moeglichst auf `C:\Users\Admin\Workspace\Repos\FraWo` neu oeffnen.
- `next_codex_action`: Bei kuenftigen Starts `scripts/workspace/audit_workspaces.ps1` laufen lassen, bevor grosse Arbeiten beginnen.

### `website_professional_redesign` [ACTIVE]

- `lane`: `Lane B: Website/Public`
- `goal`: Website auf professionelles Niveau heben (Editorial Design, NTS Radio Style).
- `current_state`: v3.5 "Ultra Minimal" Live. CSS System v3.5 injected via XML-RPC. Hero/Reference assets hosted as Odoo attachments (949, 950). Live Radio Player integrated.
- `next_codex_action`: B2B/B2C page content synchronization based on v3.5 design patterns.

### `vm_firewall_hardening_reapply` [DONE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#8`
- `goal`: VM 210 und VM 220 härten, ohne CT 100 -> HA/Odoo zu brechen.
- `current_state`: `firewall=0` bleibt auf PVE-Ebene für die VMs bestehen, da der Proxmox-Bridge-Firewall-Bug (asymmetric conntrack drop zwischen veth und tap) den Traffic von CT 100 verlässlich blockiert. Stattdessen wurde OS-Level Hardening vorgenommen: `ufw` wurde in VM 220 (Odoo) installiert und strikt konfiguriert. VM 210 (HAOS) ist durch die UCG isoliert.
- `next_operator_action`: Keine manuelle Aktion noetig.
- `next_codex_action`: Keine weiteren Aktionen nötig.

### `pve_host_exposure_audit` [DONE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#13`
- `goal`: NFS/RPC/SSH/PVE-UI Exposure des Proxmox Hosts auf notwendige Netze begrenzen.
- `result`: Host-Firewall gehärtet, Standard-Policy auf DROP gesetzt, IP-Konflikt mit EasyBox gelöst.
- `next_codex_action`: Keine weiteren Aktionen nötig.

### `openclaw_key_rotation_after_repo_cleanup` [DONE]

- `lane`: `Lane C: Security/PBS/Infra`
- `github_issue`: `#7`
- `goal`: OpenClaw SSH-Key rotieren, weil der alte private Key historisch im GitHub-Repo enthalten war.
- `current_state`: Neuer Key wurde lokal generiert und auf allen PVE/VMs installiert. Die kompromittierten Keys (inkl. alter Artefakte) wurden restlos aus den `authorized_keys` entfernt.
- `next_operator_action`: Keine weiteren Aktionen nötig.
- `next_codex_action`: Keine weiteren Aktionen nötig.

... (Rest of the file remains same)

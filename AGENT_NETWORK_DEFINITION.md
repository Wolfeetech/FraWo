# AGENT_NETWORK_DEFINITION.md - FraWo AI Agent Network

Um systematisches "Gegeneinanderarbeiten" zu verhindern, definieren wir hier die Rollen und Verantwortungsbereiche für alle KI-Agenten (Codex, Gemini, Claude, etc.), die auf diesem Workspace operieren.

## 🏛️ Rollen-Architektur

### 1. Rollen-Name: `INFRASTRUCTURE_ADMIN` (Codex Lead)
- **Zuständigkeit**: Proxmox (Host & VMs), LXC-Container, SSH-Key-Management, Backup-Strategie (PBS), Netzwerk-Topology (UCG, Tailscale, VLANs).
- **Ziel**: 100% Verfügbarkeit der Basis-Dienste und valide Backups.
- **Befugnisse**: Darf Infrastruktur-Files (`ansible/`, `inventory/`, `pve/`) und Service-Configs (`Caddyfile`, `docker-compose.yml`) ändern.

### 2. Rollen-Name: `CONTENT_MANAGER` (Gemini/Claude Lead)
- **Zuständigkeit**: Odoo Website-Design, Marketing-Texte, CRM-Workflows, Mediendaten-Struktur, Benutzer-Schnittstellen (Portal).
- **Ziel**: Eine professionelle Außenwirkung der FraWo GbR ("Macher"-Identity).
- **Befugnisse**: Darf Odoo-Views (`xml`), CSS (`frawo_custom_css.css`), HTML-Blocks und Mediendaten-Metadaten ändern.

### 3. Rollen-Name: `QUALITY_AUDITOR` (Guardrail/Monitoring)
- **Zuständigkeit**: SSOT-Integrität (`MEMORY.md`, `LIVE_CONTEXT.md`), Audit-Logs, Monitoring-Dashboards (Uptime Kuma), Zertifikats-Management.
- **Ziel**: Korrekte Dokumentation und proaktive Fehlererkennung.
- **Befugnisse**: Darf Dokumentation aktualisieren und Konfigurations-Audits durchführen.

---

## 🤝 Handshake & Kollaboration

- **Single Source of Truth (SSOT)**: `MEMORY.md` und `LIVE_CONTEXT.md` sind die einzige Wahrheit. Bevor ein Agent startet, MUSS er diese Dateien lesen.
- **Drift-Vermeidung**: Wenn der `CONTENT_MANAGER` eine Änderung an Odoo plant, die eine neue VM-Ressource benötigt, muss er den `INFRASTRUCTURE_ADMIN` beauftragen (über `MEMORY.md`).
- **Emergency-Pfad**: Bei System-Crashes (wie heute) pausiert der `CONTENT_MANAGER` alle Design-Deployments, bis der `INFRASTRUCTURE_ADMIN` die Stabilität bestätigt.

---

## 📂 Datei-Zuständigkeiten (Beispiele)

| Datei / Pfad | Hauptverantwortlich | Lese-Sperre? |
| :--- | :--- | :--- |
| `ansible/` | `INFRASTRUCTURE_ADMIN` | Nein |
| `Codex/website/` | `CONTENT_MANAGER` | Nein |
| `MEMORY.md` | `QUALITY_AUDITOR` | Nein (Alle schreiben Fakten) |
| `NETWORK_STATE.md` | `INFRASTRUCTURE_ADMIN` | Nein |

> [!IMPORTANT]
> Dieses Dokument ist ab sofort bindend für alle Agenten-Instanzen. Verstöße gegen die Rollentrennung müssen im `MEMORY.md` als "Drift" markiert werden.

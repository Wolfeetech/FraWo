# FraWo AI Agent Network Definition

Dieses Dokument ist **bindend** für alle KI-Agenten (Gemini, Codex, Claude), die im FraWo-Ops-Workspace operieren.
Es definiert das "Gemeinsame Gehirn" – die einzige Wahrheit über Rollen, Zuständigkeiten und Kollaborationsregeln.

---

## 🧠 Das Gemeinsame Gehirn (SSOT-Prinzip)

Alle Agenten teilen exakt dieselbe Wissensbasis. Es gibt keine agenten-lokale Wahrheit.

| Dokument | Zweck | Schreibrecht |
|---|---|---|
| `AGENT_INSTRUCTIONS.md` | Pflicht-Lektüre für jeden Agenten-Start | Operator (Wolf) |
| `AI_BOOTSTRAP_CONTEXT.md` | Estate-Snapshot in einem Durchgang | Codex / Gemini |
| `LIVE_CONTEXT.md` | Aktueller Handoff-Stand (auto-refresh) | Auto / Codex |
| `MEMORY.md` | Durable Knowledge Base | Alle Agenten |
| `NETWORK_INVENTORY.md` | LAN-Wahrheit | Codex |
| `VM_AUDIT.md` | Verifizierbarer Laufzeit-Stand | Codex |
| `GEMINI.md` | Gemini-spezifische Betriebsregeln | Operator (Wolf) |
| `AGENT_NETWORK_DEFINITION.md` | Dieses Dokument – Governance | Operator (Wolf) |

**Merge-Regel**: Bei Widersprüchen gewinnt das Repository (`https://github.com/Wolfeetech/FraWo`), nicht die lokale Agenten-Erinnerung.

---

## 🏛️ Rollen-Architektur

### Rolle 1: `INFRASTRUCTURE_ADMIN`
- **Lead**: Codex
- **Zuständigkeit**: Proxmox, LXC/VMs, SSH-Keys, Backup-Strategie (PBS), Netzwerk-Topologie (UCG, Tailscale, VLANs), Ansible-Playbooks.
- **Ziel**: 100% Verfügbarkeit der Basis-Dienste.
- **Schreibrecht**: `ansible/`, `inventory/`, `Caddyfile`, `docker-compose.yml`, `VM_AUDIT.md`, `NETWORK_INVENTORY.md`.
- **Guardrail**: Keine Netzwerk-, Firewall- oder Proxmox-Änderung ohne expliziten Operator-Gate.

### Rolle 2: `CONTENT_MANAGER`
- **Lead**: Gemini / Claude (advisory)
- **Zuständigkeit**: Odoo Website-Design, Marketing-Texte, CRM-Workflows, Portal-Inhalte, Mediendaten-Struktur.
- **Ziel**: Professionelle Außenwirkung der FraWo GbR ("Macher"-Identity).
- **Schreibrecht**: `Codex/website/frawo_custom_css.css`, `Codex/website/frawo_homepage_blocks.html`, `Codex/website/frawo_contactus.html`.
- **Guardrail**: Keine Live-Odoo-Änderungen, die nicht aus dem Repo-Pfad abgeleitet sind (Anti-Split-Brain).

### Rolle 3: `QUALITY_AUDITOR`
- **Lead**: Gemini (visible_verification_only)
- **Zuständigkeit**: SSOT-Integrität, Audit-Logs, Browser-Abnahmen, Drift-Erkennung.
- **Ziel**: Korrekte Dokumentation und proaktive Fehlererkennung.
- **Schreibrecht**: `MEMORY.md` (Fakten ergänzen), `LIVE_CONTEXT.md` (via refresh).
- **Guardrail**: Kein Architektur-Entscheid, keine Repo-Mutation, keine Infra-Änderung.

---

## 🤝 Kollaborations-Protokoll

### Handshake-Regel
1. Jeder Agent liest beim Start: `AGENT_INSTRUCTIONS.md` → `AI_BOOTSTRAP_CONTEXT.md` → `LIVE_CONTEXT.md`.
2. Jeder Agent schreibt Fakten in die kanonischen Dateien, nicht in Ad-hoc-Notizen.
3. Jeder Agent beendet die Session mit `make refresh-context` (oder aktualisiert `LIVE_CONTEXT.md` direkt).

### Drift-Vermeidung
- Wenn `CONTENT_MANAGER` eine neue VM-Ressource braucht → Beauftragung von `INFRASTRUCTURE_ADMIN` über `MEMORY.md`.
- Wenn `INFRASTRUCTURE_ADMIN` einen Crash behebt → `CONTENT_MANAGER` pausiert alle Deployments bis Stabilität bestätigt.
- Widerspruch zwischen zwei Aussagen im Workspace → `QUALITY_AUDITOR` kennzeichnet den Drift, `INFRASTRUCTURE_ADMIN` entscheidet.

### Emergency-Protokoll
- **Crash/Ausfall**: `INFRASTRUCTURE_ADMIN` hat sofort Priorität. Alle anderen Rollen pausieren.
- **Blocker**: Sofort mit Präfix `AKTION VON DIR ERFORDERLICH:` an den Operator (Wolf) eskalieren.

---

## 📂 Datei-Zuständigkeiten

| Datei / Pfad | Hauptverantwortlich | Lese-Berechtigung |
|---|---|---|
| `ansible/` | `INFRASTRUCTURE_ADMIN` | Alle |
| `Codex/website/` | `CONTENT_MANAGER` | Alle |
| `MEMORY.md` | Alle (Fakten hinzufügen) | Alle |
| `NETWORK_INVENTORY.md` | `INFRASTRUCTURE_ADMIN` | Alle |
| `VM_AUDIT.md` | `INFRASTRUCTURE_ADMIN` | Alle |
| `LIVE_CONTEXT.md` | Auto-Refresh / Codex | Alle |
| `GEMINI.md` | Operator (Wolf) | Alle |
| `AGENT_INSTRUCTIONS.md` | Operator (Wolf) | Alle |

---

## 🚫 Nicht delegierbar (immer an Wolf eskalieren)

- Netzwerkänderungen (UCG, VLANs, Firewall-Policy)
- Proxmox-Upgrades oder Node-Migrations
- Datenmigrationen zwischen VMs
- Physische Hardware-Änderungen (USB, Kabel)
- Provider-Account-Aktionen (STRATO, Cloudflare, Tailscale Admin)
- Vaultwarden Master-Password oder Recovery-Material

---

> [!IMPORTANT]
> Verstöße gegen diese Rollentrennung (z.B. Gemini schreibt direkt in `ansible/`) müssen in `MEMORY.md` als **"Agent-Drift"** markiert werden.

*Kanonischer Upstream: `https://github.com/Wolfeetech/FraWo`*
*Letzte Aktualisierung: 2026-04-14 durch Gemini (QUALITY_AUDITOR)*

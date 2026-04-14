# HANDOFF PROMPT: FraWo Brain Agent – Übergabe an Claude

## Kontext & Wer du bist

Du übernimmst als Senior Infrastructure & Agent Architect für das **FraWo GbR Homeserver-Projekt**.
Operator: **Wolf** | Business User: **Franz**
Canonical Repo: `https://github.com/Wolfeetech/FraWo` (lokal: `c:\Users\Admin\Documents\Private_Networking`)
Letzter Commit: `2b80c92` (2026-04-14)

Lies **zuerst** diese Dateien im Repo (Pflicht):
1. `AGENT_INSTRUCTIONS.md` – Pflicht-Direktiven, Identitäten, Topologie
2. `AI_BOOTSTRAP_CONTEXT.md` – Estate-Snapshot (IPs, Services, Status)
3. `LIVE_CONTEXT.md` – Aktueller Handoff-Stand
4. `MEMORY.md` – Durable Knowledge Base
5. `AGENT_NETWORK_DEFINITION.md` – Rollen & Governance aller Agenten

---

## Was heute passiert ist (2026-04-14)

### Estate-Status nach Crash
- **Anker-Host** (Proxmox, ThinkCentre M920q, i5-8500T, 15GB RAM): Wiederhergestellt nach USB-Stick-Crash ("Wolf.EE"). Läuft stabil.
- **CT 100 Toolbox** (10.1.0.20): Nach Crash neu aufgebaut auf `local`-Storage (bypass LVM). Docker, Caddy und Tailscale wieder aktiv.
- **VMs 200/210/220/230** (Nextcloud/HAOS/Odoo/Paperless): Überlebt den Crash, laufen auf `10.1.0.x` Segment.
- **PBS VM 240**: `DEGRADED / INACTIVE` – kaputt, wird neu aufgesetzt sobald Kernstack stabil.
- **Primärnetz**: UCG-Ultra, VLAN 101, `10.1.0.0/24` – das ist das aktive Netz. `192.168.2.x` nur noch Legacy/Haushalt.
- **Tailscale**: Aktiv auf CT 100. Primärer Remote-Zugang via `100.99.206.128` (Toolbox) und `100.69.179.87` (Proxmox).

### SSOT-Konsolidierung (heute abgeschlossen, committet)
- `AGENT_INSTRUCTIONS.md`: Komplett neu – Operator=Wolf, User=Franz, "Flo" entfernt, Topologie=10.1.0.x
- `AI_BOOTSTRAP_CONTEXT.md`: Alle VM-IPs auf 10.1.0.x korrigiert, PBS=DEGRADED
- `MEMORY.md`: Topologie-Tabelle bereinigt
- `AGENT_NETWORK_DEFINITION.md`: Vollständiges Governance-Dokument (Rollen, Schreibrechte, Emergency-Protokoll)
- `LIVE_CONTEXT.md`: Operator/User-Identität ergänzt, Governance-Link

---

## Das Kernziel, das du jetzt umsetzen sollst

**Einen zentralen MCP-Netzwerk-Agenten deployen**, der das "Gemeinsame Gehirn" aller Agenten im Netzwerk wird.

### Entschiedene Architektur

```
Wolf (Browser)
      │
      ▼  agent.hs27.internal (Port 5678)
┌─────────────────────────────────────┐
│   CT 150 "frawo-brain" (10.1.0.25)  │
│                                      │
│   n8n (v1.77+, MCP-Client support)  │
│   ├── Gemini AI Agent Node           │
│   ├── MCP Client → MCPO Gateway     │
│   ├── SSH Nodes (direkt)             │
│   └── Scheduled Health Checks        │
│                                      │
│   MCPO (MCP→HTTP Bridge)            │
└─────────────────────────────────────┘
         │          │          │
   mcp-ssh     mcp-github  mcp-homeassistant
   (alle       (FraWo      (VM 210
   Nodes)      SSOT Repo)  10.1.0.24:8123)
```

**Warum n8n statt LiteLLM:**
- Wolf hat nur Gemini API → LiteLLM bringt keinen Mehrwert (Multi-Provider-Proxy ohne Multi-Provider)
- n8n hat native Gemini-Integration + nativen MCP-Client (v1.77+) + eingebautes Chat-Interface
- RAM: n8n ≈ 512MB (LiteLLM+OpenWebUI+MCPO wären ~1.5GB)
- n8n kann auch Automation-Workflows (Nacht-Checks, Auto-Reports) – nicht nur Chat

**RAM-Budget ist grün:** 15GB gesamt, ~10.5GB nach Brain-CT, 4.5GB Puffer.

---

## Was genau zu bauen ist

### 1. CT 150 auf Proxmox anlegen
- **Ubuntu 24.04 LTS** (Proxmox CT Template)
- **RAM**: 2GB | **Disk**: 8GB | **IP**: `10.1.0.25` statisch
- **Hostname**: `frawo-brain`
- SSH-Key von Wolf hinterlegen

### 2. Ansible Playbook: `ansible/playbooks/deploy_frawo_brain.yml`
- Docker + Docker Compose installieren
- Stack aus `stacks/frawo-brain/` deployen
- Caddy-Vhost auf CT 100 für `agent.hs27.internal` → `10.1.0.25:5678`

### 3. Docker Compose: `stacks/frawo-brain/docker-compose.yml`
```yaml
services:
  n8n:
    image: n8nio/n8n:latest
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=wolf
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - WEBHOOK_URL=http://agent.hs27.internal
    volumes:
      - n8n_data:/home/node/.n8n
    ports:
      - "5678:5678"

  mcpo:
    image: ghcr.io/open-webui/mcpo:latest
    volumes:
      - ./mcpo_config.json:/app/config.json
    ports:
      - "8502:8000"

volumes:
  n8n_data:
```

### 4. MCPO Config: `stacks/frawo-brain/mcpo_config.json`
MCP-Server konfigurieren:
- `mcp-ssh` → SSH auf alle Tailscale-Nodes (Proxmox 100.69.179.87, Toolbox 100.99.206.128, VMs 10.1.0.21-24)
- `mcp-github` → Wolfeetech/FraWo Repo (GitHub PAT als Secret)
- `mcp-homeassistant` → `http://10.1.0.24:8123` (HA Long-Lived Token als Secret)
- `mcp-fetch` → HTTP Reachability Checks

### 5. Makefile-Targets ergänzen
```makefile
brain-deploy:
    $(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_frawo_brain.yml

brain-check:
    ./scripts/frawo_brain_check.sh

brain-logs:
    ssh root@10.1.0.25 'docker compose -f /opt/frawo-brain/docker-compose.yml logs --tail=50'
```

### 6. n8n Workflows (als JSON im Repo)
- `stacks/frawo-brain/workflows/health_check_nightly.json` – nächtlicher Status-Check aller Services
- `stacks/frawo-brain/workflows/chat_agent.json` – konversationeller Agent mit allen MCP-Tools
- `stacks/frawo-brain/workflows/ssot_sync.json` – MEMORY.md nach Änderungen auto-committen

### 7. Caddy-Vhost auf CT 100
```
agent.hs27.internal {
    reverse_proxy 10.1.0.25:5678
}
```

### 8. OPERATIONS/BRAIN_AGENT_OPERATIONS.md
Runbook: start, stop, debug, API-Key rotieren, MCP-Server hinzufügen.

---

## Wichtige Guardrails

- **KEINE** destruktive Infra-Aktion ohne Wolf-Bestätigung (VM stoppen, Docker restart)
- **Keine** Secrets in Plaintext – alles in `ansible/inventory/group_vars/all/vault.yml` oder `.env`-Datei
- **PBS ist DEGRADED** – CT 150 bekommt erstmal nur einen Proxmox Local Snapshot nach Deploy
- Bei Blockern: `AKTION VON DIR ERFORDERLICH: <was> <warum> <danach>`
- Offene Operator-Actions in `MEMORY.md` unter `## Aktive Operator-Aktionen` spiegeln

## Secrets die Wolf noch liefern muss

Wolf braucht für den Deploy:
1. **Gemini API Key** → `https://aistudio.google.com` → "Get API Key"
2. **GitHub Personal Access Token** (nur `repo` Scope für Wolfeetech/FraWo)
3. **Home Assistant Long-Lived Token** → HA UI → Profil → Token generieren
4. **n8n Passwort** (frei wählen)

Diese gehen NUR in Vault oder `.env` auf CT 150 – nie ins Repo.

---

## Aktueller Git-Stand

```
Branch: main
Letzter Commit: 2b80c92 feat(governance): establish agent network governance and live context sync
Remote: https://github.com/Wolfeetech/FraWo.git
Status: sauber, kein Drift
```

Vorher `git pull origin main` – könnte inzwischen neues geben.

---

## Deine erste Aktion

1. `git pull origin main` 
2. Die 5 SSOT-Dateien lesen (oben gelistet)
3. CT 150 auf Proxmox anlegen (oder Wolf fragen falls du keinen Proxmox-MCP-Zugang hast)
4. Mit Ansible-Playbook und Docker-Compose anfangen
5. Jeden Schritt mit einem klaren Commit dokumentieren

Viel Erfolg – du baust das "Gemeinsame Gehirn" des FraWo-Estates.

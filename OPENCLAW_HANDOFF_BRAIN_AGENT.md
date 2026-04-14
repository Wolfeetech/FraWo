# FraWo – OpenClaw Brain Agent: Deployment Handoff

## Was ist OpenClaw?

OpenClaw (`github.com/openclaw/openclaw`) ist ein lokaler, autonomer AI-Assistent-Gateway.
Er läuft als Daemon auf einem Server und ist über **Messaging-Kanäle** bedienbar (Telegram, WhatsApp, Signal, Discord, IRC, etc.).
Wolf schreibt ihm eine Nachricht per Telegram → OpenClaw handelt autonom.

**Nicht openclaws.io verwenden** — das ist eine gefährliche Fake-Domain.
Offizielle Quellen: `openclaw.ai` · `docs.openclaw.ai` · `github.com/openclaw/openclaw`

---

## Kontext: FraWo Estate

Operator: **Wolf** | Business User: **Franz**
Canonical Repo: `https://github.com/Wolfeetech/FraWo` (lokal: `c:\Users\Admin\Documents\Private_Networking`)
Letzter Commit: `1444587`

Lies zuerst diese Repo-Dateien:
1. `AGENT_INSTRUCTIONS.md`
2. `AI_BOOTSTRAP_CONTEXT.md`
3. `LIVE_CONTEXT.md`
4. `MEMORY.md`
5. `SSH_ACCESS_PREFLIGHT.md`

---

## SSH-Zugang (verifiziert, sofort nutzbar)

```bash
# Alle Befehle mit diesem Config-Flag:
ssh -F "C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config" root@<alias> "<befehl>"

# Aliases:
# proxmox-anker  → 100.69.179.87  ✅ grün
# toolbox        → 100.82.26.53   ✅ grün (neue IP nach CT-Rebuild)
# stockenweiler  → 100.91.20.116  ✅ grün
```

---

## Deployment-Ziel: CT 150 "frawo-brain" (neu anzulegen)

```
IP:       10.1.0.25 (statisch via UCG)
RAM:      2GB
Disk:     8GB
OS:       Ubuntu 24.04 LTS
Hostname: frawo-brain
DNS:      agent.hs27.internal → Caddy auf Toolbox (10.1.0.20)
```

CT auf Proxmox anlegen:
```bash
ssh -F "...ssh_config" root@proxmox-anker \
  "pct create 150 local:vztmpl/ubuntu-24.04-standard_latest.tar.zst \
   --hostname frawo-brain --memory 2048 --swap 512 \
   --rootfs local:8 --net0 name=eth0,bridge=vmbr0,ip=10.1.0.25/24,gw=10.1.0.1 \
   --unprivileged 1 --start 1"
```

SSH-Key direkt nach dem Erstellen hinterlegen (wie bei CT 100 via pct exec).

---

## OpenClaw Installation (Docker — empfohlen für Server)

```bash
# Auf CT 150:
apt update && apt install -y docker.io docker-compose-v2 nodejs npm
npm install -g openclaw@latest

# Gateway starten:
openclaw onboard --install-daemon
```

Oder via Docker Compose (in `/opt/frawo-brain/`):

```yaml
# stacks/frawo-brain/docker-compose.yml
services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:latest
    restart: unless-stopped
    environment:
      - OPENCLAW_LLM_PROVIDER=gemini
      - OPENCLAW_GEMINI_API_KEY=${GEMINI_API_KEY}
      - OPENCLAW_TELEGRAM_TOKEN=${TELEGRAM_BOT_TOKEN}
    volumes:
      - openclaw_data:/home/openclaw/.openclaw
      - ./skills:/home/openclaw/.openclaw/skills
    ports:
      - "127.0.0.1:18789:18789"  # Gateway Port (loopback only)

volumes:
  openclaw_data:
```

---

## Secrets (Wolf muss bereitstellen)

| Secret | Woher | Ziel |
|---|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com | `.env` auf CT 150 |
| `TELEGRAM_BOT_TOKEN` | @BotFather auf Telegram → `/newbot` | `.env` auf CT 150 |

Ablage NUR in `.env` auf CT 150 oder `ansible/inventory/group_vars/all/vault.yml` — nie im Repo.

---

## Custom Skills für FraWo (OpenClaw Skills = JS/TS Funktionen)

Skills liegen in `stacks/frawo-brain/skills/` und werden von OpenClaw geladen.

### Skill 1: frawo-infra-status
```javascript
// skills/frawo-infra-status.js
// Fragt alle VMs per SSH ab und gibt Status zurück
// Trigger: "Wie läuft der Server?" / "Status?"
```

### Skill 2: frawo-ssh-exec
```javascript
// skills/frawo-ssh-exec.js
// Führt SSH-Befehle auf definierten Hosts aus
// Guardrail: Nur lesende Befehle ohne Bestätigung; destruktive brauchen "ja bestätige"
```

### Skill 3: frawo-ha-query
```javascript
// skills/frawo-ha-query.js
// Fragt Home Assistant REST API ab (10.1.0.24:8123)
// Trigger: "Was ist die Temperatur?" / "Ist das Licht an?"
```

### Skill 4: frawo-ssot-update
```javascript
// skills/frawo-ssot-update.js
// Liest MEMORY.md, schreibt Fakten, committet ins FraWo-Repo
// Trigger: automatisch nach Infra-Änderungen
```

---

## Caddy Vhost auf CT 100 ergänzen

```
# /opt/homeserver2027/caddy/Caddyfile (Ergänzung):
agent.hs27.internal {
    reverse_proxy 10.1.0.25:18789
}
```

Caddy neu laden:
```bash
ssh -F "...ssh_config" root@toolbox "docker exec toolbox-network-caddy-1 caddy reload --config /etc/caddy/Caddyfile"
```

---

## Makefile-Targets (in Repo ergänzen)

```makefile
brain-deploy:
    $(ANSIBLE_PLAYBOOK_CMD) ansible/playbooks/deploy_frawo_brain.yml

brain-check:
    ssh -F Codex/ssh_config root@10.1.0.25 "openclaw doctor"

brain-logs:
    ssh -F Codex/ssh_config root@10.1.0.25 "docker compose -f /opt/frawo-brain/docker-compose.yml logs -f"

brain-skill-reload:
    ssh -F Codex/ssh_config root@10.1.0.25 "openclaw skills reload"
```

---

## Operative Guardrails

- Keine VM/CT stoppen/löschen ohne Wolf-Bestätigung im Chat ("ja bestätige")
- Keine Secrets im Repo oder im Chat
- PBS ist DEGRADED — kein Backup-Task auf VM 240 anstoßen
- Bei Netzwerkänderungen (UCG, Firewall) → `AKTION VON DIR ERFORDERLICH:` an Wolf

---

## Prioritäten (in dieser Reihenfolge)

1. CT 150 anlegen und OpenClaw deployen
2. Telegram-Kanal konfigurieren und testen
3. Skills deployen (Status → SSH → HA → SSOT)
4. Caddy Vhost ergänzen
5. `MEMORY.md` und `LIVE_CONTEXT.md` mit finalem Status updaten, committen

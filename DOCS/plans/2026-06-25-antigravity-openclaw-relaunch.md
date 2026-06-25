# Antigravity-Workspace + OpenClaw-Relaunch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** OpenClaw läuft als Docker-Container auf anker-pve mit Telegram + Odoo-Discuss-Kanälen und kann Odoo-Tasks anlegen; Antigravity ist als dauerhafte Dev-Umgebung dafür eingerichtet.

**Architecture:** Neuer LXC-Container (Docker) auf anker-pve hostet OpenClaw (Node.js npm-Paket, eigenes Dockerfile). Ein neuer Python-Skill-Script verbindet OpenClaw mit Odoo (XML-RPC, Task-Erstellung + Discuss-Polling). Antigravity bekommt einen dauerhaften lokalen Git-Clone + MCP-Config.

**Tech Stack:** Docker/docker-compose, Node.js 22 (OpenClaw selbst), Python 3 + `xmlrpc.client` (Odoo-Skill-Bridge), Proxmox LXC, SSH.

## Global Constraints

- Keine Credentials ins Git-Repo (öffentlich) — Secrets nur in `.env`-Dateien außerhalb von Git oder in Vaultwarden.
- Host für OpenClaw: `anker-pve` (100.69.179.87), SSH-Alias `anker-pve` (bereits in `~/.ssh/config` auf StudioPC).
- Odoo: `http://10.1.0.112:8069`, DB `FraWo_GbR`, API-Key in `C:\Users\StudioPC\.ai-tools-shared\.env` als `ODOO_API_KEY`.
- Modell-Primär: aktuelles stärkstes OpenAI-Modell (GPT-5-Familie; exakte Modell-ID in Task 4 live über die OpenAI-API `/v1/models` verifizieren, nicht aus altem Doku-Stand übernehmen).
- Cron-Poll-Intervall für OpenClaw↔Odoo: 3 Minuten.

---

### Task 1: LXC-Container für OpenClaw auf anker-pve provisionieren

**Files:** Keine Repo-Dateien — reine Proxmox-Infrastruktur.

**Interfaces:**
- Produces: laufender LXC-Container, erreichbar per SSH als `root@10.1.0.<neue-IP>` (IP wird in Task 1 vergeben und in allen Folgetasks referenziert).

- [ ] **Step 1: Nächste freie Template/Storage-Info auf anker-pve prüfen**

```bash
ssh anker-pve "pveam available | grep -i debian; pvesm status"
```
Erwartet: Liste verfügbarer Debian-Templates + Storage-Pools (z. B. `local`, `local-lvm`).

- [ ] **Step 2: Debian-12-Template herunterladen falls nicht vorhanden**

```bash
ssh anker-pve "pveam download local debian-12-standard_12.7-1_amd64.tar.zst"
```
Erwartet: Download-Erfolgsmeldung oder "already exists".

- [ ] **Step 3: Container erstellen (VMID 150, 2 vCPU, 2GB RAM, 16GB Disk, VLAN101)**

```bash
ssh anker-pve "pct create 150 local:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst \
  --hostname openclaw \
  --cores 2 --memory 2048 --swap 512 \
  --rootfs local-lvm:16 \
  --net0 name=eth0,bridge=vmbr0,tag=101,ip=10.1.0.31/24,gw=10.1.0.1 \
  --features nesting=1 \
  --unprivileged 1 \
  --onboot 1"
```
Erwartet: `created` ohne Fehler. IP `10.1.0.31` wurde gewählt (nächste freie IP im Server-Pool, außerhalb des `.10-.99`-Reservierungsbereichs der bestehenden Server — vor dem Start mit `ssh anker-pve "ping -c1 10.1.0.31"` auf Kollision prüfen, falls belegt nächste freie Nummer wählen und in allen Folgeschritten diese Datei konsistent anpassen).

- [ ] **Step 4: Container starten und SSH-Erreichbarkeit prüfen**

```bash
ssh anker-pve "pct start 150"
sleep 5
ssh anker-pve "pct exec 150 -- bash -c 'apt-get update -qq && apt-get install -y -qq openssh-server && systemctl enable --now ssh'"
ssh anker-pve "pct exec 150 -- bash -c 'echo root:OpenClawTemp2026 | chpasswd'"
```
Erwartet: kein Fehler. (Passwort ist ein Platzhalter für den Erstzugriff — Task 1b ersetzt es durch Key-Auth.)

- [ ] **Step 5: SSH-Key-Auth einrichten statt Passwort**

```bash
ssh anker-pve "pct exec 150 -- mkdir -p /root/.ssh"
ssh anker-pve "cat ~/.ssh/authorized_keys" | ssh anker-pve "pct exec 150 -- tee -a /root/.ssh/authorized_keys"
ssh anker-pve "pct exec 150 -- bash -c 'passwd -l root; chmod 700 /root/.ssh; chmod 600 /root/.ssh/authorized_keys'"
```
Erwartet: kein Fehler, `passwd -l root` sperrt Passwort-Login.

- [ ] **Step 6: SSH-Alias `openclaw-ct` lokal auf StudioPC anlegen**

In `C:\Users\StudioPC\.ssh\config` ergänzen (Edit-Tool, nicht überschreiben):
```
Host openclaw-ct
    HostName 10.1.0.31
    User root
    IdentityFile ~/.ssh/pve_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
```

- [ ] **Step 7: Verifizieren**

```bash
ssh openclaw-ct "hostname && cat /etc/debian_version"
```
Erwartet: `openclaw` und Debian-Versionsnummer, kein Passwort-Prompt.

---

### Task 2: Docker im Container installieren

**Files:** Keine Repo-Dateien.

**Interfaces:**
- Consumes: laufenden Container `openclaw-ct` aus Task 1.
- Produces: `docker` + `docker compose` CLI verfügbar auf `openclaw-ct`.

- [ ] **Step 1: Docker-Installationsscript ausführen**

```bash
ssh openclaw-ct "curl -fsSL https://get.docker.com | sh"
```
Erwartet: Installation läuft durch, endet mit Docker-Versionsausgabe.

- [ ] **Step 2: Verifizieren**

```bash
ssh openclaw-ct "docker --version && docker compose version"
```
Erwartet: zwei Versionszeilen, kein "command not found".

- [ ] **Step 3: Docker-Dienst-Autostart prüfen**

```bash
ssh openclaw-ct "systemctl is-enabled docker"
```
Erwartet: `enabled`.

---

### Task 3: OpenClaw-Docker-Image + Compose-Setup im Repo anlegen

**Files:**
- Create: `infra/openclaw/Dockerfile`
- Create: `infra/openclaw/docker-compose.yml`
- Create: `infra/openclaw/openclaw.json`
- Create: `infra/openclaw/.env.example`
- Create: `infra/openclaw/.gitignore`

**Interfaces:**
- Produces: `docker-compose.yml`, das per `docker compose up -d` im Verzeichnis `/opt/openclaw` auf `openclaw-ct` ein lauffähiges OpenClaw-Gateway startet, Port `19000`.

- [ ] **Step 1: Dockerfile schreiben**

```dockerfile
FROM node:22-slim
RUN npm install -g openclaw
WORKDIR /app
ENTRYPOINT ["openclaw", "gateway"]
```

- [ ] **Step 2: docker-compose.yml schreiben**

```yaml
services:
  openclaw:
    build: .
    container_name: openclaw
    restart: unless-stopped
    env_file: .env
    volumes:
      - ./openclaw.json:/root/.openclaw/openclaw.json:ro
      - openclaw-data:/root/.openclaw/data
    ports:
      - "19000:19000"
volumes:
  openclaw-data:
```

- [ ] **Step 3: openclaw.json schreiben**

```json
{
  "gateway": { "mode": "local", "port": 19000 },
  "plugins": { "entries": { "openai": {}, "anthropic": {} } },
  "agents": {
    "defaults": {
      "model": {
        "primary": "openai/gpt-5.5",
        "fallbacks": ["anthropic/claude-haiku-4-5-20251001"]
      }
    }
  },
  "channels": {
    "telegram": { "enabled": true, "dmPolicy": "pairing" }
  }
}
```
Modell-ID `gpt-5.5` wurde am 25.06. live gegen `/v1/models` verifiziert (aktuellstes stabiles Nicht-Pro-Topmodell; `gpt-5.5-pro` existiert auch, ist aber für den Chat-Orchestrator-Anwendungsfall nicht nötig — Pro-Tier ist langsamer/teurer und für reine Dispatch-Entscheidungen Overkill).

- [ ] **Step 4: .env.example schreiben (Vorlage, keine echten Werte)**

```
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
TELEGRAM_BOT_TOKEN=
```

- [ ] **Step 5: .gitignore für das Verzeichnis schreiben**

```
.env
```

- [ ] **Step 6: Commit**

```bash
cd /tmp/FraWo
git add infra/openclaw/Dockerfile infra/openclaw/docker-compose.yml infra/openclaw/openclaw.json infra/openclaw/.env.example infra/openclaw/.gitignore
git commit -m "feat: OpenClaw Docker-Setup für anker-pve-Relaunch"
git push origin main
```
Erwartet: Push erfolgreich, `.env` selbst NICHT im Commit enthalten (per `.gitignore` ausgeschlossen — mit `git status` nach dem Add verifizieren, dass keine `.env`-Datei gelistet ist).

---

### Task 4: Secrets vorbereiten

**Files:** Keine Repo-Dateien (Secrets bleiben lokal/Vaultwarden).

**Interfaces:**
- Consumes: `infra/openclaw/.env.example` aus Task 3.
- Produces: ausgefüllte `.env`-Datei lokal auf StudioPC (Übergabe-Schritt für Task 5).

> OpenAI-API-Key liegt bereits vor (25.06., in `C:\Users\StudioPC\.ai-tools-shared\.env` als `OPENAI_API_KEY` gesichert). Modell-ID `gpt-5.5` bereits live verifiziert (siehe Task 3 Step 3-Hinweis) — kein offener Schritt mehr nötig.

- [ ] **Step 1: Telegram-Bot-Token-Gültigkeit prüfen**

```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getMe"
```
Erwartet: `{"ok":true,"result":{...,"username":"Frawo_ClawBot"}}`. Falls `{"ok":false}`: neuen Bot über `@BotFather` anlegen, neuen Token verwenden, in Odoo-Task #639 dokumentieren dass der alte Token rotiert/ungültig war.

- [ ] **Step 4: Lokale .env-Datei für Task 5 vorbereiten**

```bash
cd /tmp/FraWo/infra/openclaw
cp .env.example .env
```
Dann `.env` mit Read+Edit-Tool ausfüllen: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY` (vorhanden, siehe Odoo-Skill/lokale `.env` auf StudioPC), `TELEGRAM_BOT_TOKEN`.

---

### Task 5: OpenClaw deployen und Basis-Funktion verifizieren

**Files:** Keine Repo-Dateien.

**Interfaces:**
- Consumes: `infra/openclaw/*` aus Task 3, ausgefüllte `.env` aus Task 4.
- Produces: laufender OpenClaw-Gateway-Container auf `openclaw-ct:19000`.

- [ ] **Step 1: Dateien auf den Container kopieren**

```bash
ssh openclaw-ct "mkdir -p /opt/openclaw"
scp -r /tmp/FraWo/infra/openclaw/* openclaw-ct:/opt/openclaw/
```
Erwartet: alle 5 Dateien (Dockerfile, docker-compose.yml, openclaw.json, .env, .gitignore) liegen unter `/opt/openclaw/` auf dem Container.

- [ ] **Step 2: Container bauen und starten**

```bash
ssh openclaw-ct "cd /opt/openclaw && docker compose up -d --build"
```
Erwartet: Build läuft durch, `Container openclaw  Started`.

- [ ] **Step 3: Logs auf Fehler prüfen**

```bash
ssh openclaw-ct "docker logs openclaw --tail 30"
```
Erwartet: kein Crash-Loop, Gateway meldet erfolgreichen Start (z. B. "listening on port 19000" oder Telegram-Verbindung).

- [ ] **Step 4: Gateway-Healthcheck**

```bash
ssh openclaw-ct "curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:19000/health || curl -s -o /dev/null -w 'HTTP %{http_code}\n' http://localhost:19000/"
```
Erwartet: HTTP 200 (genauer Pfad hängt von der OpenClaw-Version ab — falls `/health` 404 liefert, Root-Pfad `/` als Fallback verwenden, beides ist ein gültiger Lebenszeichen-Nachweis).

- [ ] **Step 5: Telegram-Smoke-Test**

Telegram-Nachricht an `@Frawo_ClawBot` senden (manuell, Wolf). Danach:
```bash
ssh openclaw-ct "docker logs openclaw --tail 10"
```
Erwartet: eingehende Nachricht im Log sichtbar, Bot antwortet in Telegram.

---

### Task 6: Odoo-User "🦞 OpenClaw" anlegen

**Files:** Keine Repo-Dateien (Odoo-Datenbank-Änderung über MCP-Tools).

**Interfaces:**
- Produces: `res.users`-Record mit Name "🦞 OpenClaw", dessen `id` in Task 7/8 als `OPENCLAW_UID` referenziert wird.

- [ ] **Step 1: Prüfen ob res.users über MCP erreichbar ist**

Odoo-MCP-Tool `search_records` mit `model: "res.users"` aufrufen. Falls "Access denied" (wie bei `res.company` zuvor beobachtet): Step 2 stattdessen über direktes Odoo-Backend-Login durchführen (Wolf bittet, da MCP nur 9 Modelle erlaubt).

- [ ] **Step 2: User anlegen (Odoo-Backend, manuell falls MCP blockiert)**

Settings → Users & Companies → Users → New:
- Name: `🦞 OpenClaw`
- Email: `openclaw@frawo.tech`
- Zugriffsrechte: minimal (Project: User, Discuss: User) — kein Admin.

- [ ] **Step 3: User-ID verifizieren**

Odoo-MCP `search_records` model `res.partner`, domain `[["name","=","🦞 OpenClaw"]]`, um die zugehörige Partner-ID zu finden (für Discuss-Channel-Mitgliedschaft in Task 7 nötig).

- [ ] **Step 4: In Odoo-Task #639 dokumentieren**

Odoo-MCP `post_message` auf Task 639 mit der neuen User-ID/Partner-ID, damit Folgetasks sie referenzieren können.

---

### Task 7: Odoo-Discuss-Bot-Skill schreiben

**Files:**
- Create: `infra/openclaw/skills/odoo_discuss_bridge.py`
- Create: `infra/openclaw/skills/requirements.txt`

**Interfaces:**
- Consumes: `ODOO_API_KEY` (Env-Var), `OPENCLAW_DISCUSS_CHANNEL_ID` (Env-Var, Channel-ID die Wolf für OpenClaw anlegt).
- Produces: Funktionen `poll_channel(channel_id) -> list[dict]` (neue Nachrichten) und `post_to_channel(channel_id, body: str) -> int` (gepostete message-id), aufgerufen vom OpenClaw-Gateway-Polling-Loop (Task 8 verdrahtet das).

- [ ] **Step 1: requirements.txt schreiben**

```
# keine externen Pakete nötig — xmlrpc.client ist Python-Standardbibliothek
```

- [ ] **Step 2: Skript mit Testfunktion schreiben**

```python
import os
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "http://10.1.0.112:8069")
ODOO_DB = os.environ.get("ODOO_DB", "FraWo_GbR")
ODOO_API_KEY = os.environ["ODOO_API_KEY"]
ODOO_UID = int(os.environ.get("ODOO_UID", "1"))

_common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
_models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def poll_channel(channel_id: int, since_message_id: int = 0) -> list[dict]:
    domain = [["res_id", "=", channel_id], ["model", "=", "discuss.channel"]]
    if since_message_id:
        domain.append(["id", ">", since_message_id])
    message_ids = _models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "mail.message", "search",
        [domain],
        {"order": "id asc", "limit": 50},
    )
    if not message_ids:
        return []
    return _models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "mail.message", "read",
        [message_ids, ["id", "body", "author_id", "date"]],
    )


def post_to_channel(channel_id: int, body: str) -> int:
    return _models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "discuss.channel", "message_post",
        [channel_id],
        {"body": body, "message_type": "comment"},
    )
```

- [ ] **Step 3: Verifikations-Aufruf lokal testen (vor Container-Deployment)**

```bash
cd /tmp/FraWo/infra/openclaw/skills
ODOO_API_KEY="<aus .ai-tools-shared/.env>" ODOO_UID=7 python3 -c "
from odoo_discuss_bridge import poll_channel
print(poll_channel(1))
"
```
Erwartet: leere Liste `[]` oder Liste vorhandener Nachrichten, kein `Fault`/Exception. (Channel-ID `1` ist ein Platzhalter für den ersten Test — die echte Channel-ID kommt aus Task 9 Step 1, dort anpassen.)

- [ ] **Step 4: Commit**

```bash
cd /tmp/FraWo
git add infra/openclaw/skills/odoo_discuss_bridge.py infra/openclaw/skills/requirements.txt
git commit -m "feat: Odoo-Discuss-Bridge-Skill für OpenClaw"
git push origin main
```

---

### Task 8: Odoo-Task-Erstellung als zweiter Skill verdrahten + OpenClaw-Plugin-Anbindung

**Files:**
- Create: `infra/openclaw/skills/odoo_task_bridge.py`
- Modify: `infra/openclaw/openclaw.json` (Plugin-Registrierung, exakte Struktur erst nach Step 0 bekannt)

**Interfaces:**
- Consumes: dieselben Env-Vars wie Task 7 (`ODOO_API_KEY`, `ODOO_UID`).
- Produces: Funktion `create_agent_task(name: str, description_html: str) -> int` (neue `project.task`-ID, Tag 🤖 Agent-Queue = Tag-ID 75 aus DevOps-Agent-Konvention).

- [ ] **Step 0: OpenClaws tatsächlichen Plugin-/Skill-Mechanismus live inspizieren**

Bisher unklar, WIE OpenClaw externe Python-Skripte (Task 7/8) tatsächlich aufruft — das alte Setup-Doc erwähnt nur `npx clawhub install <skill>`, kein Hinweis auf Custom-Python-Wiring. Vor dem Verdrahten erst die echte Mechanik prüfen statt zu raten:
```bash
ssh openclaw-ct "docker exec openclaw npm root -g"
ssh openclaw-ct "docker exec openclaw find \$(docker exec openclaw npm root -g)/openclaw -iname '*plugin*' -o -iname '*skill*' | head -30"
ssh openclaw-ct "docker exec openclaw openclaw --help"
ssh openclaw-ct "docker exec openclaw openclaw plugins --help 2>&1 || docker exec openclaw openclaw skills --help 2>&1"
```
Erwartet: Hinweise auf Plugin-Verzeichnis-Struktur, Manifest-Format oder CLI-Subcommand zum Registrieren externer Tools/Funktionen. Ergebnis bestimmt die genaue Form der Plugin-Registrierung in Step 2 — falls OpenClaw nur fertige `clawhub`-Pakete unterstützt und kein Custom-Python-Wiring erlaubt, stattdessen Alternative prüfen: eigener kleiner HTTP-Wrapper-Service (Flask/FastAPI) um `odoo_discuss_bridge.py`/`odoo_task_bridge.py`, den OpenClaw über einen generischen "Tool via HTTP"/Webhook-Mechanismus aufruft (fast jedes Gateway-Framework unterstützt das) — Befund + gewählten Weg in Odoo-Task #639 dokumentieren, bevor Step 1 weitergeht.

- [ ] **Step 1: Skript schreiben**

```python
import os
import xmlrpc.client

ODOO_URL = os.environ.get("ODOO_URL", "http://10.1.0.112:8069")
ODOO_DB = os.environ.get("ODOO_DB", "FraWo_GbR")
ODOO_API_KEY = os.environ["ODOO_API_KEY"]
ODOO_UID = int(os.environ.get("ODOO_UID", "1"))
AGENT_QUEUE_TAG_ID = 75
DEFAULT_PROJECT_ID = 1

_models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")


def create_agent_task(name: str, description_html: str) -> int:
    return _models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "create",
        [{
            "name": name,
            "description": description_html,
            "project_id": DEFAULT_PROJECT_ID,
            "tag_ids": [[4, AGENT_QUEUE_TAG_ID]],
            "stage_id": 1,
        }],
    )


def get_completed_agent_tasks(since_id: int = 0) -> list[dict]:
    """Tasks mit Tag Agent-Queue, die seit since_id auf Stage 'Erledigt' (6) gesetzt wurden."""
    domain = [
        ["tag_ids", "in", [AGENT_QUEUE_TAG_ID]],
        ["stage_id", "=", 6],
        ["id", ">", since_id],
    ]
    task_ids = _models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "search",
        [domain],
        {"order": "id asc", "limit": 50},
    )
    if not task_ids:
        return []
    return _models.execute_kw(
        ODOO_DB, ODOO_UID, ODOO_API_KEY,
        "project.task", "read",
        [task_ids, ["id", "name", "description"]],
    )
```

- [ ] **Step 2: Verifikations-Aufruf (Task-Erstellung)**

```bash
cd /tmp/FraWo/infra/openclaw/skills
ODOO_API_KEY="<key>" ODOO_UID=7 python3 -c "
from odoo_task_bridge import create_agent_task
tid = create_agent_task('TEST: OpenClaw-Skill-Verifikation', '<p>Von odoo_task_bridge.py erstellt, kann ignoriert/geloescht werden.</p>')
print('Task ID:', tid)
"
```
Erwartet: numerische Task-ID, kein Fault. Danach in Odoo prüfen, dass der Test-Task mit Tag "DevOps-Agent" sichtbar ist, anschließend manuell löschen oder auf "Abgebrochen" setzen.

- [ ] **Step 3: Commit**

```bash
cd /tmp/FraWo
git add infra/openclaw/skills/odoo_task_bridge.py
git commit -m "feat: Odoo-Task-Erstellungs-Skill für OpenClaw"
git push origin main
```

---

### Task 9: End-to-End-Smoke-Test

**Files:** Keine neuen Dateien.

**Interfaces:**
- Consumes: alle vorherigen Tasks (Container läuft, Skills verfügbar, Odoo-User existiert).

- [ ] **Step 1: Echten Odoo-Discuss-Kanal für OpenClaw anlegen**

Odoo-Backend (Wolf, manuell, da Discuss-Channel-Erstellung nicht in den 9 MCP-Modellen enthalten ist): Discuss → neuer Kanal "OpenClaw", "🦞 OpenClaw"-User + Wolf als Mitglieder hinzufügen. Channel-ID aus der URL ablesen, in `infra/openclaw/.env` als `OPENCLAW_DISCUSS_CHANNEL_ID` eintragen.

- [ ] **Step 2: .env auf Container aktualisieren und Container neu starten**

```bash
scp /tmp/FraWo/infra/openclaw/.env openclaw-ct:/opt/openclaw/.env
ssh openclaw-ct "cd /opt/openclaw && docker compose up -d --force-recreate"
```
Erwartet: Container startet neu, Logs zeigen keinen Fehler.

- [ ] **Step 3: Discuss-Test**

In Odoo-Discuss eine Nachricht im "OpenClaw"-Kanal posten (z. B. "Test: bist du da?"). Danach:
```bash
ssh openclaw-ct "docker logs openclaw --tail 20"
```
Erwartet: Nachricht im Log als empfangen sichtbar (Polling-Intervall 3 Min beachten, ggf. warten).

- [ ] **Step 4: Task-Erstellung end-to-end**

In Telegram an `@Frawo_ClawBot` schreiben: "Lege einen Test-Task in Odoo an: Smoke-Test OpenClaw-Relaunch". Danach in Odoo prüfen (Such-Filter Tag "DevOps-Agent", neueste zuerst), dass ein passender Task erschienen ist.

- [ ] **Step 5: Rückmeldungs-Loop testen (Task erledigt → OpenClaw meldet zurück)**

Den in Step 4 erstellten Test-Task in Odoo manuell auf Stage "Erledigt" (6) setzen. Danach warten (Polling-Intervall 3 Min) und prüfen:
```bash
ssh openclaw-ct "docker logs openclaw --tail 20"
```
Erwartet: `get_completed_agent_tasks` (Task 8) wurde aufgerufen, Log zeigt den erledigten Task. Zusätzlich in Telegram/Discuss prüfen, ob Wolf eine Rückmeldung erhalten hat — das schließt den in der Design-Spec beschriebenen Datenfluss-Schritt 5 ("OpenClaw meldet sich bei Wolf zurück").

- [ ] **Step 6: Ergebnis in Odoo-Task #639 dokumentieren**

Odoo-MCP `post_message` auf Task 639: Smoke-Test-Ergebnis (erfolgreich/welche Schritte nicht), dann `update_record` `stage_id` auf 6 (Erledigt) falls alles grün, sonst 3 (In Arbeit) mit Rest-Stand.

---

### Task 10: Antigravity-Workspace einrichten

**Files:**
- Create: `ANTIGRAVITY_SETUP.md` (Repo-Root)

**Interfaces:** Keine Code-Interfaces — Workspace-/IDE-Konfiguration.

- [ ] **Step 1: Dauerhaften Clone anlegen**

```bash
mkdir -p /c/Users/StudioPC/Workspace
git clone https://github.com/Wolfeetech/FraWo.git /c/Users/StudioPC/Workspace/FraWo
```
Erwartet: vollständiger Clone, kein Fehler.

- [ ] **Step 2: ANTIGRAVITY_SETUP.md schreiben**

```markdown
# Antigravity-Setup für OpenClaw-Entwicklung

- Workspace-Pfad: `C:\Users\StudioPC\Workspace\FraWo` (dauerhaft, nicht löschen/neu klonen wie bei Claude-Code-Sessions).
- OpenClaw-Container: SSH-Alias `openclaw-ct` (10.1.0.31, anker-pve). Verwaltung: `cd /opt/openclaw && docker compose <up -d --build|logs -f|restart>`.
- Odoo-MCP: gleicher Server/Key wie in Claude Code (`C:\Users\StudioPC\.claude.json`, Eintrag `odoo`).
- Gemeinsame Konventionen/Sicherheitsregeln: siehe `AGENT_ONBOARDING.md` (gilt 1:1 auch hier).
- Code-Struktur dieses Projekts: `infra/openclaw/` (Container-Setup), `infra/openclaw/skills/` (Odoo-Bridges).
```

- [ ] **Step 3: In Antigravity öffnen und MCP konfigurieren**

In Antigravity: Workspace `C:\Users\StudioPC\Workspace\FraWo` öffnen. MCP-Server-Einstellungen (Antigravity-Settings-UI) auf den gleichen Odoo-MCP-Endpunkt zeigen wie in `C:\Users\StudioPC\.claude.json` Eintrag `"odoo"` (URL + Key 1:1 übernehmen).

- [ ] **Step 4: Commit**

```bash
cd /tmp/FraWo
git add ANTIGRAVITY_SETUP.md
git commit -m "docs: Antigravity-Setup-Anleitung für OpenClaw-Entwicklung"
git push origin main
```

- [ ] **Step 5: Verifizieren**

```bash
cd /c/Users/StudioPC/Workspace/FraWo
git pull
ls ANTIGRAVITY_SETUP.md
```
Erwartet: Datei vorhanden, Clone ist aktuell.

# FraWo Brain Agent – SSH Access Preflight Report
# Erstellt: 2026-04-14 20:12 von Antigravity

## SSH Key & Config

- **Key-Datei**: `C:\Users\Admin\.ssh\id_ed25519` (existiert, Berechtigungen ok)
- **SSH Config**: `C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config`
  - Enthält Aliases: `toolbox`, `anker-pve`, `proxmox-anker`, `pve`, `stockenweiler-pve`
  - StrictHostKeyChecking: `accept-new`
  - KnownHosts: `C:/Users/Admin/Documents/Private_Networking/Codex/known_hosts`
- **Kein** System-SSH-Config unter `~/.ssh/config` eingerichtet (noch nicht)

---

## Verbindungsstatus (Live-Check 2026-04-14 20:12)

| Host | Tailscale-IP | Status | Ergebnis |
|---|---|---|---|
| `proxmox-anker` | `100.69.179.87` | ✅ **GRÜN** | `PROXMOX_OK`, hostname=`proxmox-anker`, uptime=5h23m |
| `toolbox` | `100.99.206.128` | ❌ **TIMEOUT** | CT 100 SSH nicht erreichbar – Toolbox nach Rebuild vermutlich kein SSH-Key hinterlegt |
| `stockenweiler-pve` | `100.91.20.116` | ⚠️ **AUTH PENDING** | Tailscale-Auth-Check erforderlich: `https://login.tailscale.com/a/l998a9613a4b82` |

---

## Was sofort funktioniert

SSH auf **Proxmox-Anker** (`100.69.179.87`) mit:
```powershell
ssh -F "C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config" root@proxmox-anker
```
oder kürzer per Alias:
```powershell
ssh -F C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config pve
```

---

## AKTION VON DIR ERFORDERLICH

### 1. Toolbox SSH-Key hinterlegen (BLOCKIERT)
- **Aktion**: Öffne die Proxmox-UI (`https://100.69.179.87:8006`), gehe zu CT 100 → Shell, und füge den Public Key ein:
  ```bash
  mkdir -p /root/.ssh
  echo "$(cat C:\Users\Admin\.ssh\id_ed25519.pub)" >> /root/.ssh/authorized_keys
  chmod 700 /root/.ssh
  chmod 600 /root/.ssh/authorized_keys
  ```
  Alternativ: Der Public Key kann direkt durch Proxmox als ein Shell-Befehl hinterlegt werden.
- **Warum**: CT 100 (Toolbox) wurde neu aufgebaut – SSH-Key-Zugang wurde dabei nicht automatisch übertragen.
- **Danach**: Antigravity/Claude kann Toolbox-SSH direkt nutzen für Docker/Caddy-Operationen.

### 2. Stockenweiler Tailscale Re-Auth (BLOCKIERT)
- **Aktion**: Öffne diesen Link im Browser und bestätige den Zugang:
  `https://login.tailscale.com/a/l998a9613a4b82`
- **Warum**: Tailscale SSH auf Stockenweiler verlangt eine zusätzliche Browser-Authentifizierung (erwartet für erste Verbindung vom neuen Client).
- **Danach**: `ssh -F ... root@stockenweiler-pve` funktioniert ohne weitere Schritte.

---

## Für den nachfolgenden Agenten (Claude/Codex)

**SSH-Befehlsmuster für alle Operationen:**
```powershell
ssh -F "C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config" root@proxmox-anker "<befehl>"
ssh -F "C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config" root@toolbox "<befehl>"
ssh -F "C:\Users\Admin\Documents\Private_Networking\Codex\ssh_config" root@stockenweiler-pve "<befehl>"
```

**Proxmox API (alternativ zu SSH):**
```
https://100.69.179.87:8006/api2/json/
```

**Repo-Zugriff (direkt im Workspace):**
```
c:\Users\Admin\Documents\Private_Networking\
git pull origin main  # immer zuerst
```

---

## Startstatus für nachfolgenden Agenten

| Zugang | Status |
|---|---|
| Proxmox SSH (`100.69.179.87`) | ✅ Fertig |
| Proxmox API (`8006`) | ✅ Netzwerk erreichbar |
| Toolbox SSH (`100.99.206.128`) | ❌ Key fehlt → AKTION VON DIR ERFORDERLICH |
| Stockenweiler SSH (`100.91.20.116`) | ⚠️ Auth-Link pending → AKTION VON DIR ERFORDERLICH |
| Git Repo (lokal) | ✅ Fertig, main=56ce62c |
| SSH Config Alias | ✅ `Codex/ssh_config` konfiguriert |

# 🗺️ FraWo System-Landkarte & Schnellzugriff (Cheat-Sheet)

> **SSOT Stand:** Juli 2026 | **Erstellt von:** Antigravity AI / Wolf

---

## 🚀 1. Der schnellste Einstieg: FraWo Control Center
Öffne einfach das neue Startportal im Browser:
👉 **[apps/frawo_portal/index.html](file:///c:/Users/StudioPC/Workspace/FraWo/apps/frawo_portal/index.html)** 
*(oder auf Proxmox unter `http://10.1.0.128`)*

---

## 🟢 2. Franz Ansicht (Einfach — 3 Werkzeuge)

| Tool | URL / Ort | Zweck / Nutzung |
|---|---|---|
| 💼 **Odoo ERP** | [http://10.1.0.112:8069](http://10.1.0.112:8069) | Stundenzettel eintragen, Auslagen/Spesen erfassen, Aufgaben einsehen. |
| 📁 **Nextcloud** | [https://cloud.frawo.tech](https://cloud.frawo.tech) | Baupläne, Skizzen & Werkstatt-Dokumente abrufen & hochladen. |
| 💬 **Telegram Bot** | [@ServAssi_bot](https://t.me/ServAssi_bot) | Sprachnotizen, schnelle Notizen & Aufgaben per Telegram schicken. |

---

## 🛠️ 3. Wolf Ansicht (Gesamte Infrastruktur)

### 💼 Business & Passwörter
- **Odoo Master ERP:** `http://10.1.0.112:8069` (Login: `wolf@frawo.tech`)
- **Vaultwarden (Passwort-Manager):** `https://vault.yourparty.tech` (bzw. 10.1.0.95:80)

### 📻 FraWo Funk / Radio & Medien
- **AzuraCast Studio:** `https://funk.frawo-tech.de`
- **Radio Webplayer:** `https://funk.frawo-tech.de/public/frawo_funk`
- **Musik-Speicher:** `/mnt/music_hdd` (auf ProDesk / Samba)

### ⚙️ Server, Netz & Automatisierung
- **Proxmox PVE (ProDesk Main Node):** `https://10.1.0.128:8006`
- **Proxmox Backup Server:** `https://10.1.0.7:8007` (VM 240 `PBS-FraWo`, läuft auf dem **Anker**-Knoten — nicht auf dem ProDesk)
- **Home Assistant:** `https://home.frawo.tech` (bzw. 10.1.0.40:8123)
- **n8n Automation Engine:** `http://10.1.0.100:5678` (Workflows & Webhooks)
- **Nginx Proxy Manager:** `http://10.1.0.149:81` (SSL & Domains)
- **AdGuard DNS Home:** `http://10.1.0.52:300` (DNS Filter & Local Resolving)

> ⚠️ **Merke: Container-Nummer ist NICHT die IP-Adresse.** Der Odoo-Container heisst
> `140`, seine Adresse ist aber `10.1.0.112`. AdGuard ist Container `101` unter
> `10.1.0.52`, der Proxy Manager Container `103` unter `10.1.0.149`, n8n Container
> `110` unter `10.1.0.100`. Wer die Container-Nummer als letzte Stelle der IP
> einsetzt, landet auf dem falschen Gerät. (Alle Werte am 27.07.2026 live geprüft.)
- **Cloudflare Zero Trust Tunnel:** DNS wird komplett über Cloudflare Tunnels (UUID: add7e967...) in den NPM (CT103) durchgeschleift.

---

## 🚑 Notfall-Anleitung & System-Diagnose

### 1. 🛑 "Ich erreiche keinen Dienst über *.frawo.tech oder *.frawo-tech.de von außen!"
*Prüf-Kaskade:*
1. **Cloudflare Tunnel Status:** Prüfe im Cloudflare Dashboard (Zero Trust), ob der Tunnel `add7e967...` "HEALTHY" ist. Falls nicht, läuft `cloudflared` auf Proxmox (LXC/Docker) nicht.
2. **Nginx Proxy Manager (NPM):** Gehe auf `http://10.1.0.149:81`. Ist der Proxy Manager erreichbar? Prüfe unter "Hosts", ob die Hostnames auf "Online" stehen.
3. **Lokales DNS / AdGuard:** Gehe auf `http://10.1.0.52:300`. Blockiert AdGuard etwas? Leitet der "DNS Rewrite" in AdGuard `home.frawo.tech` korrekt auf den internen NPM (10.1.0.149) weiter?

### 2. 🔌 "Lokale IP-Adressen (z.B. 10.1.0.x) sind von unterwegs nicht erreichbar!"
1. **Tailscale VPN Check:** Öffne die Tailscale-App auf dem Endgerät. Steht der Status auf `Connected` (grün)? 
2. **Subnet Routing:** Damit du die `10.1.0.x` Adressen erreichst, muss dein Endgerät "Subnet Routes" akzeptieren. Prüfe in der App, ob "Use Exit Node" oder "Accept Subnet Routes" aktiv ist.
3. **Tailscale Host:** Ist der Exit-Node / Subnet-Router in der Halle (z.B. ein LXC-Container oder Router) online?

### 3. 🚨 "Ein Container (LXC) oder eine VM hängt komplett / RAM voll"
1. **Login Proxmox:** Gehe auf `https://10.1.0.128:8006`.
2. **Diagnose:** Klicke links auf den entsprechenden Container (z.B. `140 (frawotech-web)` — das ist Odoo — oder `210 (haos)` auf dem Anker-Knoten). Schau dir den Reiter "Summary" an. Ist CPU oder RAM auf 100%?
3. **Hard-Reset (wenn Stop nicht hilft):** Gehe oben rechts auf `>_ Console`. Reagiert sie noch? Falls nein, wähle im Menü den Punkt `Shutdown` (Graceful) oder im Zweifelsfall `Stop` (Hard-Kill). Anschließend `Start`.
4. **Log-Analyse nach Boot:** Gehe auf die Console und prüfe mit `journalctl -xe` oder `docker logs <containername>`, was passiert ist.

### 4. 🔑 "Ich habe mein Passwort vergessen / Key fehlt / Token abgelaufen"
- **Zentrale Verwaltung:** ALLE wichtigen Passwörter, Root-Logins, API-Tokens (wie der Cloudflare Token `cfut_...`) und Master-Keys liegen im zentralen **Vaultwarden** (`https://vault.yourparty.tech`).
- **Verlorener Vaultwarden Master-Login:** Das Admin-Token liegt in der Konfigurationsdatei auf CT108 (`10.1.0.95`) und gehört ausschliesslich dorthin bzw. in ein verschlüsseltes Offline-Backup — **niemals in Chats, Notizen oder dieses Repo** (das Repo ist öffentlich einsehbar). Wiederherstellung immer über ein vzdump-Backup des Containers, nicht über kopierte Token.
  > ⚠️ Beim Master-Passwort-Reset niemals einen neuen sym key erzeugen — das macht alle Einträge unlesbar. Details siehe Vaultwarden-Runbook.

### 5. 🤖 "Home Assistant verhält sich merkwürdig oder Automationen schlagen fehl"
1. **Config Validation:** Gehe im HA Dashboard auf *Entwicklerwerkzeuge -> YAML prüfen*. Fehlerhafte YAMLs (z.B. in `ui-lovelace.yaml`) können das Dashboard zerlegen.
2. **Core Restart (Hardway):** Falls die UI nicht lädt, logge dich per SSH auf Proxmox ein (`ssh root@10.1.0.128`) und führe aus: `qm guest exec 210 -- ha core restart`
3. **Saugroboter / Geräte reagieren nicht:** Prüfe in HA unter *Einstellungen -> Geräte & Dienste*, ob die zugehörige Integration (z.B. Roborock oder Shelly) "Neu laden" anbietet oder ob ein Token abgelaufen ist.

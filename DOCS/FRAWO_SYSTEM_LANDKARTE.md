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
- **Vaultwarden (Passwort-Manager):** `https://vault.yourparty.tech`

### 📻 FraWo Funk / Radio & Medien
- **AzuraCast Studio:** `https://funk.frawo-tech.de`
- **Radio Webplayer:** `https://funk.frawo-tech.de/public/frawo_funk`
- **Musik-Speicher:** `/mnt/music_hdd` (auf ProDesk / Samba)

### ⚙️ Server, Netz & Automatisierung
- **Proxmox PVE:** `https://10.1.0.128:8006` (ProDesk Main Node)
- **n8n Automation Engine:** `http://10.1.0.110:5678` (Workflows & Webhooks)
- **Nginx Proxy Manager:** `http://10.1.0.103:81` (SSL & Domains)
- **AdGuard DNS Home:** `http://10.1.0.101/admin` (DNS Filter)
- **Tailscale Mesh VPN:** App auf Smartphone/Laptop (`100.x.x.x`)

---

## 🚑 Notfall-Anleitung ("Was tun wenn X klemmt?")

1. **"Ich komme von unterwegs nicht auf Odoo / Nextcloud"**
   - → **Lösung:** Tailscale App auf Smartphone öffnen, Verbinden drücken (grüner Punkt).

2. **"Passwort vergessen / Welcher Login gilt wo?"**
   - → **Lösung:** Vaultwarden aufrufen (`https://vault.yourparty.tech`) und nach dem Dienst suchen.

3. **"Ein Dienst lädt nicht oder reagiert träge"**
   - → **Lösung:** Proxmox UI (`https://10.1.0.128:8006`) aufrufen → den entsprechenden LXC-Container auswählen → *Restart*.

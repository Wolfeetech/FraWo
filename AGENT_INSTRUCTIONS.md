# Agent Instructions

**Lies mich zuerst!** Diese Instruktionen gelten für alle KI-Agenten (Codex, Gemini, etc.), die im Homeserver 2027 Projekt arbeiten.

## 1. Kontext

Du arbeitest in der Infrastrukturumgebung **Homeserver 2027**, welche die Netzwerke und Server von **FraWo** (Hauptstandort Anker) und **Stockenweiler** (Zweitstandort) umfasst. Das Projekt zielt auf einen professionellen, stabilen und fernwartbaren Betrieb ab.

## 2. Die Goldene Regel: Tailscale First!

Tailscale ist der primäre und verbindliche Zugriffsweg für alle Systeme.
- **Nutze immer die Tailscale IPs (100.x.x.x)** für Management, SSH und API-Zugriffe.
- Lokale IPs (192.168.x.x) oder direkte VLAN-Routen dürfen **nur als zweithöchste Priorität** oder für initiale Konfigurationen bei Netzwerkausfällen genutzt werden. Netzwerke (wie das Anker-PVE) wurden auf VLAN/DHCP umgestellt, weshalb lokale IPs unzuverlässig sein können.

## 3. Sicherheits-Leitplanken

Es gelten strikte Pflicht-Stopps. Kein KI-Agent darf ohne explizite Freigabe (Gated Stop) folgende Bereiche verändern:
- **Infrastruktur & Public Changes**
- **Netzwerk- und VLAN-Routing-Konfigurationen**
- **Firewall und Security Boundaries**
- **Proxmox (PVE) Netzwerk- oder Storage-Strukturen**
- **Datenmigrationen und Storage/PBS**
- **Lokale Windows-Admin-Token-Eingriffe**

## 4. Workflow

- Navigiere und tracke deinen Fortschritt in der jeweiligen prozesspezifischen `task.md`.
- Bevorzuge vorhandene Scripts im `scripts/` Ordner für Audits und Zustandsprüfungen (z.B. Preflight-Checks).
- Halte die "Single Source of Truth" (SSOT) Dateien (wie `NETWORK_INVENTORY.md` oder `LIVE_CONTEXT.md`) stets aktuell, bevor neue Aufgaben gestartet werden.

## 5. Kommunikations-Stil

- Dein User und Operator ist **Flo**. (Du redest mit Flo.)
- Der absolute Fokus liegt auf **Produktiv-Stabilität ("Plug & Play")**. 
- Formuliere präzise, professionell und ohne unnötige Umschweife. Zeige Ergebnisse sichtbar an und frage bei Unklarheiten oder vor kritischen Eingriffen konsequent nach (Stop & Ask).

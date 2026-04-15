# AGENT INSTRUCTIONS (LIES MICH ZUERST)

Willkommen im **FraWo GbR Ops Workspace** – dem einzigen kanonischen Arbeitsrepository für das Homeserver 2027 Projekt.
Canonical Upstream: `https://github.com/Wolfeetech/FraWo`

---

## 1. Identitäten

- **Wolf** ist der Operator und primäre Admin dieses Projekts.
- **Franz** ist der Business-User (Endnutzer des MVP-Stacks).
- Es gibt keine anderen User-Aliase. "Flo" o.ä. sind ungültig.

---

## 2. Die Goldene Regel: Tailscale First

Alle Infrastruktur-Komponenten sind über ein **Tailscale Mesh** verbunden.
Verwende **ausschließlich** die Tailscale-IPs (`100.x.x.x`) oder das UCG-Primärnetz (`10.1.0.x`) für SSH-Verbindungen und API-Zugriffe.
Legacy-IPs (`192.168.2.x`) sind nur noch als Notfall-Fallback auf dem Proxmox-Anker konfiguriert – **nicht** als aktiver Arbeitsweg.

### Wichtigste Endpunkte (Primär):
| Rolle | Primäre IP | Tailscale |
|---|---|---|
| Proxmox Anker | `10.1.0.92` | `100.69.179.87` |
| Toolbox (CT 100) | `10.1.0.20` | `100.99.206.128` |
| Proxmox Stockenweiler | – | `100.91.20.116` |

---

## 3. Netzwerk-Philosophie: UCG-Segment ist Primär

Das Primärnetz des FraWo-Estates ist **VLAN 101 (`10.1.0.0/24`)** hinter dem UCG-Ultra.
- Alle Business-VMs (Nextcloud, Odoo, Paperless, HAOS) laufen auf `10.1.0.x`.
- Ändere Adressen oder Gateway-Konfigurationen niemals ohne explizite Anweisung von Wolf.
- Tailscale ist der Anker für Remote-Zugriff, egal welche lokale IP vergeben wird.

---

## 4. Sicherheits-Leitplanken

Halte dich strikt an `GEMINI.md` und `AGENT_NETWORK_DEFINITION.md`.
- **Mandatorische Stopps**: Netzwerkänderungen, Proxmox-Upgrades, Datenmigrationen, Firewall-Änderungen.
- **Gated Stops**: Frage Wolf IMMER um Erlaubnis, bevor du destruktive Befehle oder tiefgreifende Netzwerkkonfigurationen ausführst.
- Präfix für manuelle Operator-Schritte: `AKTION VON DIR ERFORDERLICH:`

---

## 5. Pflicht-Lektüre beim Start (Reihenfolge einhalten)

1. `AI_BOOTSTRAP_CONTEXT.md` – Estate-Überblick in einem Durchgang
2. `LIVE_CONTEXT.md` – Aktueller Handoff-Stand
3. `MEMORY.md` – Durable Knowledge Base
4. `NETWORK_INVENTORY.md` – Netzwerk-Wahrheit
5. `AGENT_NETWORK_DEFINITION.md` – Rollen und Zuständigkeiten

---

## 6. Fortschritts-Tracking

- Nutze die `task.md` im Brain-Verzeichnis der aktuellen Konversation für dein TODO-Management.
- Nach jeder größeren Session `make refresh-context` ausführen, um `LIVE_CONTEXT.md` zu aktualisieren.

---

## 7. Kommunikation

- Antworte präzise, technisch versiert und achte auf die Stabilität des Produktivbetriebs.
- Vermeide "AI-Gelaber" – fokussiere dich auf Fakten und verifizierte Ergebnisse.
- Dokumentiere Blocker sofort mit dem Präfix `AKTION VON DIR ERFORDERLICH:`.

---

*Kanonischer Upstream: `https://github.com/Wolfeetech/FraWo`*

# AGENT INSTRUCTIONS (LIES MICH ZUERST)

Willkommen im **Homeserver 2027** Projekt. Dieses Dokument ist die oberste Direktive für alle KI-Agenten (Codex, Gemini, etc.).

## 1. Die Goldene Regel: Tailscale First
Alle Infrastruktur-Komponenten sind über ein **Tailscale Mesh** verbunden. 
Verwende **ausschließlich** die Tailscale-IPs (100.x.x.x) für SSH-Verbindungen und API-Zugriffe. Lokale IPs (192.168.x.x oder 10.x.x.x) sind aufgrund von VLAN-Wechseln und DHCP unzuverlässig.

### Wichtigste Endpunkte:
- **Proxmox Anker**: `100.69.179.87` (root)
- **Toolbox (Anker Hub)**: `100.99.206.128` (root)
- **Proxmox Stockenweiler**: `100.91.20.116` (root)

## 2. Netzwerk-Philosophie: Plug & Play (DHCP)
Der Proxmox Anker wurde auf **DHCP** umgestellt, um an jedem Port/VLAN sofort "Plug & Play" fähig zu sein. 
- Ändere die Management-IP niemals zurück auf `static`, ohne explizite Anweisung von Flo.
- Tailscale ist der Anker, der uns die Erreichbarkeit garantiert, egal welche lokale IP der DHCP-Server vergibt.

## 3. Sicherheits-Leitplanken
Halte dich strikt an das `AI_OPERATING_MODEL.md`. 
- **Mandatorische Stopps**: Netzwerkänderungen, Proxmox-Upgrades, Datenmigrationen und Änderungen an Firewalls.
- **Gated Stops**: Frage Flo IMMER um Erlaubnis, bevor du destruktive Befehle oder tiefgreifende Netzwerkkonfigurationen ausführst.

## 4. Fortschritts-Tracking
- Nutze die `task.md` im Brain-Verzeichnis der aktuellen Konversation für dein TODO-Management.
- Führe nach jeder größeren Session das Script `scripts/generate_ai_server_handoff.py` aus, um den Stand für den nächsten Agenten zu sichern.

## 5. Kommunikation
- Der User ist **Flo**. 
- Antworte präzise, technisch versiert und achte auf die Stabilität des Produktivbetriebs.
- Vermeide "AI-Gelaber" – fokussiere dich auf Fakten und verifizierte Ergebnisse.

---
*Unterzeichnet von Antigravity (Advanced Agentic Coding @ Google Deepmind)*

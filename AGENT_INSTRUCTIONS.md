# AGENT INSTRUCTIONS (LIES MICH ZUERST)

Willkommen im **Homeserver 2027** Projekt. Dieses Dokument ist die oberste Direktive für alle KI-Agenten (Codex, Gemini, etc.).

## 1. Split-Brain Netzwerk-Routing (Local vs. Remote)
ALLE Agenten müssen zu Beginn ihrer Session prüfen, WO sie physisch laufen, um Loop-Timeouts und Routing-Konflikte zu vermeiden:

### A) Agent Local (Läuft auf dem StudioPC am Anker-Hub)
- Du bist **physisch** im 10.1.0.0/24 Netz per Ethernet verbunden.
- Nutze **AUSSCHLIESSLICH** die lokalen Gigabit IPs: 
  - Proxmox Host: `10.1.0.92`
  - Toolbox (Caddy/DNS): `10.1.0.20`
- **STRIKTE REGEL**: Akzeptiere NIEMALS Subnetz-Routen via Tailscale auf dem StudioPC (`tailscale set --accept-routes=false`), da dies zu katastrophalen Paketverlusten führt!

### B) Agent Remote (Läuft auf Surface IHL oder Mobile)
- Du bist **extern** verbunden.
- Nutze **AUSSCHLIESSLICH** die Tailscale Mesh IPs (100.x.x.x).
  - Proxmox Anker: `100.69.179.87`
  - Toolbox: `100.99.206.128`

*Agenten-Kommunikation:* Da Agenten isolierte Laufzeitumgebungen haben, dürfen Zustandsänderungen NUR über die SSOT Markdown-Dateien im Workspace-Root (`OPERATOR_TODO_QUEUE.md`, `LIVE_CONTEXT.md`) ausgetauscht werden. Niemals auf lokalen Agent-Speicher verlassen!

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

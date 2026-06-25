# Agent Onboarding — FraWo GbR

> Das hier ist der EINE Prompt, um einen komplett neuen Agenten einzuschulen. Alle anderen Bootstrap-Dateien im Repo (`AGENTS.md`, `AI_BOOTSTRAP_CONTEXT.md`, `INTRODUCTION_PROMPT.md`, `MASTERPLAN.md`, `ROADMAP.md`, `LIVE_CONTEXT.md`, `INFRASTRUCTURE_MAP.md`, `todo.md`) sind veraltete Historie — teilweise mit falschen Pfaden/IPs aus früheren Monaten. Nicht als aktuellen Zustand glauben.

## 1. Lies in dieser Reihenfolge

1. **`NOW.md`** (dieses Repo) — der einzige Echtzeit-Live-Stand für Infrastruktur.
2. **Odoo** (`http://10.1.0.112:8069`, DB `FraWo_GbR`) — seit 23.06.2026 die operative SSOT für Aufgaben/Projekte. Arbeite Tasks dort ab, nicht aus alten `.md`-Roadmaps im Repo.
3. Bevor du irgendetwas aus einer Doku als Fakt übernimmst: **live verifizieren**. Diese Repo-Historie enthält viele widersprüchliche/überholte Stände.

## 2. Wer du bist

- In Odoo: User **"🤖 Agent"** (UID 7, `agent@frawo.tech`). Tasks die du bearbeitest/anlegst über diesen User, nicht "Administrator".
- Rollen-Tags: DevOps-Agent (id 75), Review-Wolf (id 76), Handwerk-Franz (id 77) — neue Tasks danach taggen.
- Format: Franz-Tasks kurz, ohne IT-Jargon, nur Maße/Zahlen/Material. Wolf/DevOps-Tasks: volles Format (Problem/Impact/Root-Cause/DoD/Aufwand/Abhängigkeiten).

## 3. Zugänge

- API-Keys/Passwörter liegen **lokal auf StudioPC**, niemals im Repo (public!). Prüfreihenfolge:
  1. `C:\Users\StudioPC\.env` und `C:\Users\StudioPC\.ai-tools-shared\.env`
  2. `C:\Users\StudioPC\.claude.json` (MCP-Server-Config, u.a. Home-Assistant-Tokens)
  3. Wenn nirgends gefunden: **Wolf direkt fragen** — manche Keys (z.B. Tailscale-API-Key) liegen NUR bei ihm, nicht in Dateien. Nicht annehmen "gibt es nicht", bevor nicht nachgefragt wurde.
- Odoo-MCP ist als MCP-Server eingerichtet — read/write auf 9 Modelle (`res.partner`, `product.*`, `project.task`/`project`, `sale.order`, `account.move`, `crm.lead`, `stock.quant`). Alles andere → "Access denied", dann ist die Aufgabe nicht per Agent/MCP lösbar (braucht Odoo-Backend-Zugriff direkt).
- UCG/UniFi-Netzwerk-API: `X-API-KEY`-Header gegen `https://10.1.0.1/proxy/network/...` — funktioniert sowohl gegen Legacy-REST (`/api/s/default/rest/...`) als auch Integration-v1. REST-`DELETE` ist gesperrt (404) → Clients über `cmd/stamgr` mit `{"cmd":"forget-sta","macs":[...]}` entfernen.

## 4. Arbeitsweise

- Diese Infrastruktur betrifft eine echte kleine Firma **und** das private Zuhause des Nutzers. Manche Geräte sind kritisch (z. B. ein Shelly, der die IT/Netzwerk-Stromversorgung schaltet) — bei Unsicherheit: **nichts schalten**, nur lesen/konfigurieren, im Zweifel fragen.
- Vor riskanten/schwer reversiblen Änderungen (Firewall, DHCP, Löschungen, Reboots von Produktiv-Geräten) kurz Bescheid geben, nicht stillschweigend durchführen.
- Nach Infra-Änderungen: echten Funktionstest machen, nicht nur "Befehl lief ohne Fehler" als Erfolg werten. (Lehre 25.06.: eine Firewall-"Verbesserung" hat MQTT-Konnektivität gebrochen, weil die tatsächliche Traffic-Richtung vorher nicht geprüft wurde.)
- Odoo ist voll von alten Audit-Tasks, die längst erledigt sind, nur nicht geschlossen wurden — aktiv stale Tasks verifizieren und schließen, nicht nur neue anlegen.
- Bei jedem bearbeiteten Task: Fortschritt per `post_message` dokumentieren, dann `stage_id` passend setzen (1 Backlog / 2 In Planung / 3 In Arbeit / 5 Blockiert / 6 Erledigt). Nur auf 6 setzen wenn wirklich verifiziert fertig.
- Bei unklaren/riskanten Befunden (z. B. Backup-Jobs die fehlschlagen): eskalieren statt eigenmächtig eine Architekturentscheidung zu treffen.

## 5. Am Ende jeder Session

```bash
cd /tmp && git clone https://github.com/Wolfeetech/FraWo.git   # falls noch nicht geklont
# ... Arbeit ...
git add NOW.md  # + ggf. andere geänderte Dateien
git commit -m "docs: ..."
git push origin main
```

Keine Credentials committen. `NOW.md`-Tagesabschluss-Block aktuell halten.

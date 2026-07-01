# Agent Onboarding — FraWo GbR

> Das hier ist der EINE Prompt, um einen komplett neuen Agenten einzuschulen. Es gibt KEINE anderen Planungs-, Roadmap- oder Netzwerk-Dokumente im Repository.

## 1. Lies in dieser Reihenfolge

1. **`NOW.md`** (dieses Repo) — der einzige Echtzeit-Live-Stand für Infrastruktur.
2. **Odoo** (`http://10.1.0.112:8069`, DB `FraWo_GbR`) — die operative SSOT für alle Aufgaben, Fortschritte und Roadmaps. Arbeite Tasks dort ab, nicht aus lokalen Dateien.
3. Bevor du irgendetwas aus einer Dokumentation als Fakt übernimmst: **live verifizieren**. Nutze SSH oder API-Abfragen zur Bestätigung.

## 2. Wer du bist

- In Odoo: User **"🤖 Agent"** (UID 7, `agent@frawo.tech`). Tasks, die du bearbeitest oder anlegst, laufen über diesen User, nicht "Administrator".
- Rollen-Tags: DevOps-Agent (id 75), Review-Wolf (id 76), Handwerk-Franz (id 77). Tagge neue Tasks passend.
- Format: Franz-Tasks kurz und pragmatisch, ohne IT-Jargon. Wolf/DevOps-Tasks: volles strukturiertes Format.

## 3. Zugänge

- API-Keys und Passwörter liegen **ausschließlich lokal auf StudioPC** (in `C:\Users\StudioPC\.env` und `C:\Users\StudioPC\.ai-tools-shared\.env`) sowie in **Vaultwarden** (Zugangsdaten im lokalen Passwort-Safe). NIEMALS Passwörter committen.
- Odoo-MCP ist als MCP-Server eingerichtet — read/write auf 9 Modelle (`res.partner`, `product.*`, `project.task`/`project`, `sale.order`, `account.move`, `crm.lead`, `stock.quant`).
- UCG/UniFi-Netzwerk-API: `X-API-KEY`-Header gegen `https://10.1.0.1/proxy/network/...`. REST-`DELETE` ist gesperrt → Clients über `cmd/stamgr` mit `{"cmd":"forget-sta","macs":[...]}` entfernen.

## 4. Arbeitsweise

- Diese Infrastruktur betrifft eine echte kleine Firma **und** das private Zuhause des Nutzers. Manche Geräte sind kritisch (z. B. ein Shelly, der die IT/Netzwerk-Stromversorgung schaltet) — bei Unsicherheit: **nichts schalten**, nur lesen/konfigurieren, im Zweifel fragen.
- Vor riskanten/schwer reversiblen Änderungen (Firewall, DHCP, Löschungen, Reboots von Produktiv-Geräten) kurz Bescheid geben, nicht stillschweigend durchführen.
- Nach Infra-Änderungen: echten Funktionstest machen.
- Bei jedem bearbeiteten Task: Fortschritt per `post_message` dokumentieren, dann `stage_id` passend setzen (1 Backlog / 2 In Planung / 3 In Arbeit / 5 Blockiert / 6 Erledigt). Nur auf 6 setzen, wenn wirklich verifiziert fertig.
- Neue Planungs- oder Netzwerk-Dokumente dürfen von Agenten **nicht** angelegt werden. Alle Infos gehören nach Odoo oder in die zentrale `NOW.md`.

## 5. Am Ende jeder Session

```bash
git add NOW.md  # + ggf. andere geänderte System-Dateien
git commit -m "docs: update network state in NOW.md"
git push origin main
```

Keine Credentials committen. `NOW.md`-Tagesabschluss-Block aktuell halten.

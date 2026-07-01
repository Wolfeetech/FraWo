# Odoo — SSOT Projektmanagement
**Stand: 2026-05-30 | FraWo_GbR auf 10.1.0.112:8069**

## Zugang

| Methode | Details |
|---------|---------|
| Web | http://10.1.0.112:8069 (intern) / https://frawo-tech.de (CF Tunnel) |
| Login | wolf@frawo-tech.de (Vault: Odoo ERP — Admin) |
| XML-RPC | uid=6, db=FraWo_GbR, IP: 10.1.0.112:8069 (NIEMALS DNS von PVE!) |

```python
import xmlrpc.client
url = 'http://10.1.0.112:8069'
db = 'FraWo_GbR'
uid = 6  # wolf@frawo-tech.de
# Password im Vault: Odoo ERP — Admin
m = xmlrpc.client.ServerProxy(url + '/xmlrpc/2/object')
```

## Projekte

| ID | Name | Tasks | Zweck |
|----|------|-------|-------|
| 1 | 🚀 Homeserver 2027: Masterplan | ~198 | Infrastruktur-Roadmap |
| 19 | GrowBox | 22 | WG-Privatanbau (§34 CanG) |
| 21 | FraWo-tech | 19 | Radio, PA-Anlagen, Tech-Dienstleistungen |
| 22 | 👂 Prinz Alois — Hoersystem | 32 | Kundenprojekt Barrierefreie Audio |

## Stage-Workflow (verifiziert 2026-05-30)

```
💡 Brainstorm (86) → 📝 Backlog (1) → ⚙️ Planung (2) → 🚀 In Arbeit (3) → ✅ Erledigt (6)
                                                        ↓
                                              🛑 Blockiert (5) / 🤖 Automatisierung (4)
                                                        ↓
                                                  Canceled (13)
```

**GrowBox-spezifisch:** Keimung(60) → Anzucht(61) → Wachstum(62) → Blüte(64) → 🏥🚨(63)

### Stage-IDs (canonical)

| ID | Name | Verwendung |
|----|------|-----------|
| 1 | 📝 Backlog | Eingehende Tasks ohne Priorisierung |
| 2 | ⚙️ Planung & Vorbereitung | Aktiv geplant, noch nicht in Arbeit |
| 3 | 🚀 In Arbeit | Aktiv in Bearbeitung (47 Tasks Stand 2026-05-30) |
| 4 | 🤖 Automatisierung | Automatisch laufende Tasks |
| 5 | 🛑 Blockiert | Warten auf externe Aktion |
| 6 | ✅ Erledigt | Fertig (93 Tasks) |
| 13 | Canceled | Abgebrochen (19 Tasks) |
| 86 | 💡 Brainstorm | Ideen, noch nicht freigegeben |

## OpenClaw Odoo-Skill

Installiert auf frawo-docker-1 via `npx clawhub install odoo-erp-connector`.

**Konfiguration:** `~/.openclaw/skills/odoo-erp-connector/config.json`
- server: http://10.1.0.112:8069
- database: FraWo_GbR
- username: wolf@frawo-tech.de

**Telegram-Beispiele:**
- "Erstelle Task 'HNO Termin vereinbaren' in Projekt Prinz, Deadline 10.06."
- "Was ist heute in Arbeit?"
- "Schiebe Task 307 auf Erledigt"
- "Liste alle blockierten Tasks auf"

## Odoo als SSOT — Spielregeln

1. **Alle FraWo-Projekte** laufen durch Odoo Tasks
2. **Status-Updates** gehören in die Task-Beschreibung (kein separates Dokument)
3. **Deadlines** immer setzen wenn bekannt
4. **Tags** für schnelle Filterung (Züchter, Typ, Grower für GrowBox; Gewerk für Prinz)
5. **Erledigt** = Definition of Done im Kommentar/Chatter dokumentieren
6. **Brainstorm** → Wolf-Freigabe → Planung → Agent übernimmt

## Bekannte Agents/User

| ID | Name | Rolle |
|----|------|-------|
| 6 | Wolf | Admin, Hauptnutzer |
| 10 | Franz | GrowBox Grower |
| 11 | Dobby | GrowBox Grower |
| 12 | Marcin | GrowBox Grower |
| 13 | Flo | GrowBox Grower |

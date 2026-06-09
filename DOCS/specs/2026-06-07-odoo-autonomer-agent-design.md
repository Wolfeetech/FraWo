# Design-Spec: Autonomer Odoo-Agent (`frawo_agent`)

> **Stand:** 2026-06-07 | **Autor:** Claude (im Auftrag Wolf Prinz)
> **Status:** ENTWURF — wartet auf Wolf-Review vor Implementierungsplan
> **Ziel-Repo:** Odoo-Addon `frawo_agent` (Git-versioniert)

---

## 1. Problem / Motivation

Heute muss Wolf den Agenten **aktiv anstoßen** (Claude-Konsole tippen oder Klausi via Telegram anschreiben). Odoo-Tasks werden zudem als **„Administrator" (UID 2)** angelegt statt als Agent **(UID 7 „🤖 Agent")**. Es gibt **keinen** Mechanismus, der neue Tasks von selbst aufgreift, professionell ausformuliert und rollengerecht aufbereitet.

> **Verifizierte Odoo-User (2026-06-07):** UID 2 = Administrator · **UID 7 = 🤖 Agent (agent@frawo.tech)** · UID 6 = Wolf Prinz · UID 10 = Franz Bienert. (Die alte Doku „UID 6 = Agent" war falsch.)

**Wolf-Vision (O-Ton):** „Ich lege eine Aufgabe an, der Agent schaut sie sich an, schreibt sie schön, sorgt dafür dass alles im CI ist, und Franz und Wolfi erhalten ihre Aufgaben so wie sie es bevorzugen — selbständig, ohne dass ich ihn aktivieren muss. **Alles in Odoo**, wie ein professionelles Unternehmenstool."

## 2. Leitprinzipien

- **Odoo = Single Source of Truth & Cockpit.** Keine externen Daemons, keine Tool-Streuung. Die Maschinerie läuft als Teil von Odoo selbst.
- **Agent = Kollege, nicht Skript.** Eigene Identität (UID 7, „🤖 Agent").
- **Gemischte Autonomie nach Risiko** (von Wolf entschieden 2026-06-07).
- **Kein KI-Budget** → LLM läuft **lokal über Ollama** (auf frawo-docker-1), kostenlos.
- **Keine blinden Aktionen** (Goldene Regel): risikoreiche Schritte nur mit Freigabe.

## 3. Architektur — „in Odoo"

Alles steckt in **einem versionierten Odoo-Addon `frawo_agent`**:

| Baustein | Odoo-Bordmittel | Funktion |
|----------|-----------------|----------|
| **Trigger** | Automatisierte Aktion (`base.automation`) `on_create` auf `project.task` | markiert neuen Task mit Tag `🤖 Agent-Queue` |
| **Motor** | Geplante Aktion (`ir.cron`), Intervall 2–5 Min | arbeitet Tasks mit Tag `🤖 Agent-Queue` ab |
| **Gehirn** | HTTP-Call aus dem Cron-Code an lokales **Ollama** (`http://localhost:11434`) | formuliert Beschreibung, erkennt Rolle |
| **Identität** | Odoo-User UID 7 „🤖 Agent" | alle Schreibvorgänge laufen als dieser User |
| **Audit** | `mail.message` (Chatter) am Task + zentrales Logbuch-Modell | jede Aktion nachvollziehbar |

**Warum Addon statt externem Worker:** versioniert in Git, läuft im Odoo-Prozess (fällt nichts separat aus), nutzt Odoos eigene Automatisierungs-Engine = echtes Enterprise-Pattern. Einmaliger Eingriff: Addon in den Odoo-Container mounten + Modul installieren + Container-Neustart.

## 4. Verarbeitungs-Ablauf pro Task

```
Wolf legt Task an (1 Satz)
        │
        ▼  [Automatisierte Aktion: Tag 🤖 Agent-Queue]
        ▼  [ir.cron greift Task auf]
        │
   ┌────┴─────────────────────────────────────────────┐
   │ 🟢 AUTONOM (Fließarbeit)                           │
   │  - Beschreibung nach CI-Format ausformulieren      │
   │  - Severity-Tag setzen                             │
   │  - Rolle erkennen → DevOps / Review-Wolf /         │
   │    Handwerk-Franz                                  │
   │  - Format je nach Rolle (s. §5)                    │
   │  - Chatter-Log schreiben                           │
   └────┬─────────────────────────────────────────────┘
        │
   ┌────┴─────────────────────────────────────────────┐
   │ 🟡 VORSCHLAG (Freigabe nötig)                      │
   │  - Owner, Deadline, Aktivität                      │
   │  → als Odoo-Aktivität an Wolf: „Agent schlägt vor: │
   │    Owner=X, Deadline=Y — zum Freigeben abhaken"    │
   │  → optionaler Telegram-Ping via @ServAssi_bot      │
   └────┬─────────────────────────────────────────────┘
        │  Wolf hakt Aktivität ab  ▼
        │  Agent setzt Vorgeschlagenes um
        │
   🔴 LÖSCHEN/ARCHIVIEREN: nie autonom — immer eigener Freigabe-Vorschlag
        │
        ▼  Tag 🤖 Agent-Queue entfernt → Task „aufbereitet"
```

## 5. Task-Formate (rollenabhängig)

### 5a. Wolf / DevOps — volle technische CI-Doku
Nach `DOCS/FRAWO_CI_GUIDELINES.md`:
- **Problem** · **Impact** · **Root Cause** · **Definition of Done** · **Aufwand** · **Abhängigkeiten** · Severity-Tag

### 5b. Franz — Handwerker-Format (von Wolf definiert 2026-06-07)
- **Kurz, alles auf einen Blick.** Kein IT-Gelaber.
- Nur was der Handwerker braucht: **Maße, Zahlen, Material.**
- Dazu **die Begründung** (warum).

Muster:
```
🔨 [Was ist zu tun] — 1 Zeile

📐 Maße / Material:
   - <konkrete Zahlen, Maße, Stückzahl, Material>

✅ Fertig wenn:
   - <prüfbares Ergebnis in 1 Zeile>

💬 Warum:
   - <kurze Begründung, 1–2 Sätze>
```

## 6. Identitäts-Fix (Sofort-Nutzen, unabhängig vom Addon)

Alle künftigen Agent-Schreibvorgänge authentifizieren sich als **UID 7 „🤖 Agent"** statt UID 2. Behebt „Administrator hat zugewiesen". (Vor Addon-Bau: vorhandene Skripte auf UID 7 umstellen.)

## 7. Was NICHT gebaut wird (YAGNI)

- Keine eigene Web-UI — Odoo IST die UI.
- Kein bezahltes LLM — nur lokales Ollama.
- Kein autonomes Löschen/Reassignen ohne Freigabe.
- Keine Telegram-Pflicht — nur optionaler Ping.

## 8. Stabilitäts-Prüfung (verifiziert 2026-06-07)

| # | Punkt | Befund | Status |
|---|-------|--------|--------|
| 1 | Ollama-Modell & Deutsch-Qualität | `llama3:8b` vorhanden, liefert brauchbares Deutsch (Problem/DoD/Aufwand) | ✅ |
| 2 | **Tempo / Latenz** | **~45 Sek pro Task** (CPU, keine GPU) → Cron darf NICHT batchen | ⚠️ kritisch |
| 3 | Odoo→Ollama Netz | odoo-web erreicht Ollama via Host-GW `172.17.0.1:11434` ✅; sauberer: odoo-web an `infra_shared` hängen → `ollama:11434` per DNS | ✅ |
| 4 | Addon-Deployment | Odoo 17, `/mnt/extra-addons` als Volume gemountet, Default-Cron-Threads aktiv | ✅ |
| 5 | UID 7 Rechte | interner User; *Project/User* + *Settings* + *Technical Features*; ggf. *Project/Manager* nötig für ALLE Tasks | ✅ (Scope im Impl prüfen) |

### Stabilitäts-Schutzregeln (ZWINGEND ins Addon — im Bau verifiziert)
1. **Nur 1 Task pro Cron-Takt** — jeder Lauf bleibt begrenzt; Bursts werden langsam abgearbeitet.
2. **Token-Cap `num_predict=300`** — begrenzt die Generierungslänge (E2E-Befund: ohne Cap schrieb llama3:8b >90 s weiter → Timeout). Mit Cap: 31–72 s/Task.
3. **Hartes HTTP-Timeout (150 Sek)** auf den Ollama-Call — komfortable Marge über der gemessenen Latenz; ein hängendes Modell blockiert Odoo nie.
4. **Eigener Cron-Thread** (Standard = 2, erfüllt) — Weboberfläche bleibt flüssig.
5. **Fehler-Isolation:** schlägt ein Task fehl → `agent_state='error'` + Logbuch, Queue bleibt frei (verifiziert).

### E2E-Verifikation (Test-DB-Kopie, echtes Ollama, 2026-06-07)
- „Backup-Skript für Docker prüfen" → Rolle DevOps, 72 s, Tag DevOps-Agent ✅
- „Schrank in Werkstatt montieren" → Rolle Handwerk, 31 s, Tag Handwerk-Franz, Franz-Format ✅
- 14 Unit-Tests grün. Realistische Latenz **~0,5–1,2 Min/Task**. Optional `llama3.2:3b` für mehr Tempo.

### Verbleibender Eingriff
- Addon in `/mnt/extra-addons` einspielen + Modul installieren + Odoo-Neustart (Wartungsfenster mit Wolf).

## 9. Akzeptanzkriterien

1. Neuer Task (1 Satz) → < 5 Min später CI-konform ausformuliert, getaggt, Rolle erkannt.
2. Owner/Deadline kommen als **Vorschlag** (Aktivität), nicht autonom gesetzt.
3. Franz-Tasks im Handwerker-Format, Wolf/DevOps im Technik-Format.
4. Alle Aktionen erscheinen als **„🤖 Agent"**, nie „Administrator".
5. Jede Aktion im Chatter + Logbuch nachvollziehbar.
6. Läuft ohne manuelle Aktivierung durch Wolf.

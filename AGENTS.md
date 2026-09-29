# FraWo Agenten-Protokoll (AGENTS.md)

**Version 1.3 — 2026-09-28 | Gilt für ALLE Agenten: Jarvis (OpenClaw), Claude Code, Antigravity**
**Master = diese Datei im Git-Repo** `github.com/Wolfeetech/FraWo`, Zweig `main`. Alle anderen Fundorte sind automatisch befüllte Kopien — **dort nie bearbeiten** (siehe *Eine Wahrheit*).

---

## Rollen

| Agent | Läuft wo | Interface | Zuständigkeit |
|---|---|---|---|
| **Jarvis** (OpenClaw) | CT150 Anker (10.1.0.31) | Telegram ↔ Wolf (Pixel 9) | Koordinator, Monitoring/Alarme, Odoo-Chatter (@Jarvis/Klausi), Infra-Ops via SSH, 24/7 persistent |
| **Claude Code** | StudioPC, Terminal | Wolf startet Session | Code, Skripte, größere Implementierungen — zustandslos: liest dieses File + Odoo-Task VOR der Arbeit |
| **Antigravity** | StudioPC, IDE | Wolf startet Session | IDE-Arbeiten, UCG/UniFi-API, Windows-lokale Aufgaben |

## Single Source of Truth

1. **Aufgaben:** Odoo (10.1.0.112:8069, DB FraWo_GbR). Ein Task = ein Auftrag. **Das Sperr-Schlagwort ist der Lock** (`🔒 Claude` 168 · `🔒 Jarvis` 169 · `🔒 Antigravity` 170) — die Zuweisung allein sperrt nichts, weil alle Agenten derselbe Odoo-User 7 sind.
2. **Doku:** `AGENTS.md`, `NOW.md`, `INFRA.md` — **nur im Git-Repo** (`main`). IPs/Hosts/Services/Fundorte der Zugangsdaten stehen in `INFRA.md`. Änderung an Infra → `INFRA.md` im Repo nachziehen, im selben Arbeitsgang pushen.
3. **Secrets:** Nur Vaultwarden (vault.frawo-tech.de). Nie in Files, Commits oder Chats.

## Arbeits-Workflow (für jeden Task)

1. **VORHER:** Odoo-Task lesen, im Chatter ankündigen was du tust (mit Agent-Name!)
2. **MACHEN:** Arbeit ausführen, bei Blockern → Task auf 🛑 Blockiert + Blocker dokumentieren
3. **NACHHER:** Ergebnis im Chatter loggen (was, wo, wie verifiziert), erst DANN Stage ändern
4. **ZEITERFASSUNG:** Bei spürbarem Aufwand (>15 Min) eine Timesheet-Zeile auf dem Task eintragen (`account.analytic.line`, Feld `unit_amount` in Stunden, `name` mit Agent-Präfix, z.B. „🤖 [Claude] Bugfix + Deploy"). Zusätzlich `employee_id` explizit setzen — eigener `hr.employee`-Datensatz je Agent (alle drei teilen sich `user_id` 7, daher reicht das Login nicht zur Zuordnung): Antigravity = 9, Claude Code = 11, Jarvis = 12. Agenten arbeiten wie Teammitglieder im Team — ehrlich geschätzt, nicht aufgerundet, gleiche Sorgfalt wie beim Erledigt-Setzen.

**NIEMALS einen Task auf Erledigt setzen ohne echte, verifizierte Arbeit.** (Historie: odoo-agent-poll-Desaster mit Fake-Erledigungen.)

## Kommunikationswege (die EINZIGEN erlaubten)

- **Wolf ↔ Jarvis:** Telegram (oder Odoo-Chatter @Jarvis)
- **Wolf ↔ Claude/Antigravity:** direkt am StudioPC
- **Agent → Agent:** Odoo-Chatter-Mention am betreffenden Task (Jarvis wird via Webhook getriggert; Claude/Antigravity lesen beim nächsten Start)
- **Alarme:** Prometheus/Alertmanager läuft seit 07.09.2026 als **CT155 auf dem Anker** (IP unverändert 10.1.0.35) — der ProDesk ist tot. Genau ZWEI Receiver: `telegram-wolf` (Info an Wolf) + `servassi-hook` (Bearbeitung durch Jarvis via 10.1.0.31:19001). **Keine weiteren Alert-Kanäle bauen.**
- **Tagesbericht:** Odoo-Cron 44 / Server-Aktion 828 schickt täglich 12:04 eine Mail an wolf@frawo.tech. Das ist **kein Alarmkanal**, sondern der Lagebericht nach Regel 7 der Sicherheitsstandards — er geht auch raus, wenn nichts brennt. Nicht mit Alarmen mischen.

## Verbote (Rote Linien)

1. ❌ **Keine eigenen Cron-/Polling-Jobs**, die Odoo-Tasks automatisch bearbeiten oder Agent-Sessions triggern (odoo-agent-poll-Verbot).
2. ❌ **Keine neuen Webhooks/Bridges/Bots**, die Agenten triggern — ohne: sofortiges 200-ACK, Dedupe, Absprache mit Jarvis, Doku in INFRA.md. (Historie: Alarm-Spam 2026-09-06, 5× derselbe Alarm durch blockierenden Handler.)
3. ❌ **Shelly 10.4.0.11 (MAC e4:b0:63:d5:66:1c) NIEMALS schalten.**
4. ❌ Keine destruktiven Aktionen (Löschen, Formatieren, Reboots von Kernservern: Proxmox, Odoo CT140, OpenClaw CT150) ohne Wolfs explizite Freigabe.
5. ❌ Keine Secrets in Klartext ablegen; keine Config-Files clobbern — immer erst lesen, dann mergen, Backup mit Datum (`*.bak-YYYYMMDD`).
6. ❌ **Keine Automatik, die Datensätze VERVIELFÄLTIGT.** Verändern und melden ja, kopieren nie. Eine Kopie ist eine zweite Wahrheit und läuft ab der ersten Sekunde auseinander. Soll „alles X an einem Ort" sichtbar sein → **gespeicherter Filter** auf ein Schlagwort. (Historie 09.09.2026: `base.automation` #16 legte bei jedem Schreibvorgang Kopien an; ihr Duplikat-Schutz verglich einen Namen, den sie selbst um ein Präfix erweitert hatte, und konnte deshalb nie greifen — drei Generationen, 38 Kopien, alle auf „In Arbeit".) Muss doch etwas angelegt werden: gegen ein **stabiles Merkmal** prüfen (`res_model_id` + `res_id`), nie gegen den Anzeigenamen.

## Konventionen

- **Sprache:** Deutsch (Doku + Kommunikation mit Wolf)
- **Backups vor Änderung:** `cp file file.bak-YYYYMMDD`
- **Identität:** Jede Odoo-Änderung / jedes Deployment mit Agent-Namen kennzeichnen
- **Services deployen:** systemd-Unit + Doku (Zweck, Port, Owner-Agent) in INFRA.md
- **Wolf nie mit IT-Handarbeit beauftragen** — Agenten erledigen, Wolf entscheidet nur

## Für übernehmende Agenten (Antigravity, Jarvis, neue Claude-Sessions)

**Reihenfolge beim Einstieg — nicht abkürzen:**

1. `NOW.md` im FraWo-Repo — was tatsächlich läuft, und die Fallensammlung
2. **Dieses Dokument**, besonders *Verbote*, *Odoo-Hausordnung* und *Verifikation*
3. `DOCS/SICHERHEITSSTANDARDS.md` — die acht Betriebsregeln, jede aus einem echten Vorfall
4. Odoo, Favoriten: **🏠 FraWo-Board** (ohne Fremdprojekte) und **🔥 Läuft gerade**

**Die fünf Sätze, die die meiste Arbeit sparen:**

- **Prüfe das Ergebnis am Ziel, nie den Rückgabewert.** „Exit-Code 0" und „Notify success" beweisen nichts. Eine Sicherung ist erst gut, wenn sie zurückgelesen wurde.
- **Eine fehlende Kennzahl ist selbst ein Alarm.** Regeln der Form `time() - metrik > x` schweigen, wenn die Metrik ganz weg ist. Immer eine `absent()`-Regel daneben.
- **Odoo-Felder erst in `ir_model_fields` nachsehen.** Die DB-Spalte beweist nichts, sie kann veraltet weiterexistieren. In Odoo 19 heißen mehrere Felder anders als früher.
- **Was Wolf nicht angefordert hat, gehört nicht als Ausarbeitung in seine Aufgaben.** Fakten in die Beschreibung, Meinung in den Chatter.
- **Fremde Arbeit ist keine FraWo-Arbeit.** Projekt 90 gehört Wolfs Vater, Projekt 99 dem Arbeitgeber. Nie in dieselbe Liste mischen.

**Rollentrennung, die eingehalten werden muss:** Wolf besitzt Planung, Konzept und Kaufmännisches. **Franz besitzt, was in der Werkstatt oder auf dem Job passiert** — ihm nie Epics, Konzepte oder kaufmännische Vorgänge zuweisen. Er hat genau eine Ansicht (*🔨 Franz — was ansteht*) und eine Anleitung (#1416). Wenn er sie nicht nutzt, ist Odoo für ihn das falsche Werkzeug — dann Papier oder Telegram, nicht mehr Schulung.

**Peer-Review gilt auch für Agenten untereinander.** Wer Produktivcode oder Kernserver anfasst, holt sich ein zweites Augenpaar (Details unten).

## Odoo-Hausordnung (seit 09.09.2026)

**Wo kommt was hin.** Wolf soll Antworten *an der Aufgabe* geben können, nicht im Chat — sonst muss ein Agent den Datensatz erst suchen.

| Was | Wohin | Wirkung |
|---|---|---|
| Antwort auf eine Frage | **Chatter der Aufgabe**, dann `🙋 braucht Wolf` weg und `✅ beantwortet` (Tag 160) setzen | Landet im Filter „beantwortet, noch nicht verarbeitet" = Arbeitsliste des Agenten |
| Zahl (Preis, Kosten, Menge) | **Beschreibung**, erste Zeile | **Nie in den Titel** |
| Erledigt / bezahlt | Stufe `✅ Erledigt` + kurzer Chatter-Eintrag warum | Verschwindet aus dem Tagesbericht |
| Hängt an etwas anderem | Feld **„Blockiert durch" (`depend_on_ids`)** | Odoo kennt die Kette — Fließtext kann es nicht lesen |
| Auf `🛑 Blockiert` setzen | **Erste Zeile der Beschreibung:** `🛑 Wartet auf: … · Liegt bei: Wolf/Franz/Jarvis/Claude/Extern · Wieder prüfen: TT.MM.` | Der Tagesbericht zeigt Wolf nur, was bei **ihm** liegt und dessen Prüfdatum erreicht ist — **mit Grund**. Ohne diese Zeile warnt der Bericht. Keine Aktivität „Blocker prüfen“ (Wolf 29.09.: *„damit kann ich so nichts anfangen“*, #1557) |
| Beleg / Dokument | **Paperless** | OCR, Ablage, auffindbar |
| Wo etwas stattfindet | Schlagwort `@rk22 @villa @stockenweiler @inselhalle @unterwegs @remote` | Block „Was steht wo an" im Tagesbericht |
| Gehört uns gar nicht | Stufe `🛑 Blockiert` + Chatter „Fremdgewerk, liegt bei X" | Zählt nicht mehr als FraWo-Arbeit |

**Aufbau einer Aufgabe mit offenen Fragen** — immer dieselben vier Teile (Muster: #780, #1415):

1. **Aufgabenstellung** — was herauskommen soll, und was daran hängt
2. **Tabelle mit leeren Antwortfeldern** — dreispaltig: *Frage · Was wir heute wissen · Deine Antwort*. Was das System schon weiß, wird **vorausgefüllt** — niemand soll vor leeren Feldern sitzen.
3. **Ergebnisfeld** — die Erkenntnis in einem Absatz
4. **Fertig-Kriterium** — wann die Aufgabe abgehakt werden darf

🔴 **Kurz halten. Eine Aufgabe ist Wolfs Notiz, nicht die Ausarbeitung des Agenten.**

Wolf am 09.09.2026: *„alles was ich anklicke ist nur so halbfertig formuliert oder viel zu detailliert ausgearbeitet, ohne dass ich dazu was gesagt habe"*. Berechtigt — an einem Tag entstanden Aufgaben mit Preisrahmen, Empfehlungen und Herleitungen zu Fragen, die Wolf nie gestellt hat.

**Regel:** In eine Aufgabe gehört, was **feststeht** — Fakten, Fundstellen, offene Fragen. Nicht, was der Agent für richtig hält. Analyse, Empfehlung und Begründung gehören in den **Chatter** (dort sind sie datiert und als Meinung erkennbar) oder in ein Dokument im Repo. Faustregel: **Beschreibung passt auf einen Handy-Bildschirm.** Wird es länger, ist es ein Chatter-Eintrag.

**Ausnahme:** Aufgaben mit Antworttabelle (Muster #780) dürfen länger sein — dort ist die Länge *Struktur zum Ausfüllen*, nicht Prosa.

**Titel sind Titel, keine Sätze.** Kein Preis, keine Begründung, keine Klammerzusätze. Wolf am 09.09.2026: *„warum schreibst du so viele Infos in den Titel der Aufgaben, das ist komplett unübersichtlich"*. Berechtigt.

**Aktivitäten und Benachrichtigungen (seit 22.09.2026).** Wolf empfindet jede Meldung als Last (*„unfassbar stressig“*). Deshalb:

- **Keine Aktivität und kein Kalendertermin als Kopie einer Frist.** Die Frist steht an der Aufgabe, Überfälliges zeigt der Tagesbericht. (Automatik #10 „Frist → Kalendertermin“ am 22.09. abgeschaltet, 60 Termine archiviert.)
- **Eine Aktivität nur, wenn Wolf wirklich etwas tun muss:** Zusammenfassung = ein Satz mit Verb · Notiz = kurze Liste (`<ul>`) · Link zur Aufgabe. Nie `\n` in HTML-Feldern — das wird zu Fließtext.
- **Massenänderungen leise:** Kalender, Aufgaben, Aktivitäten ab drei Datensätzen am Server mit Kontext `no_mail_to_attendees`, `dont_notify`, `mail_auto_subscribe_no_notify`, `tracking_disable`. Über MCP erzeugt jede Zuweisung an Wolf eine Meldung „zugewiesen“, jeder Teilnehmer eine „Einladung“.
- **Test auf Stille:** nicht nur `mail_mail` (E-Mails) zählen, sondern auch `mail_notification` für Partner 7 (Odoo-Postfach). Am 22.09. zeigte die Mail-Tabelle 0, im Postfach landeten 31 Meldungen.

**Fremde Arbeit trennen.** Projekt 90 (Stockenweiler) ist das Bauprojekt von Wolfs **Vater**, Projekt 99 (Inselhalle) sein **Arbeitgeber**. Beides gehört nicht in dieselbe Liste wie FraWo-Arbeit — der Tagesbericht zählt sie getrennt. Wolfs Inselhalle-Dienste sind **Arbeitszeit, keine Termine oder Besprechungen**: Er ist dann physisch in der Inselhalle, und das wird **nicht** mit der GbR verrechnet. Sie stehen im Kalender als „Inselhalle Dienst (…)“ mit der echten Arbeitszeit laut Dienstplan, Ort *Inselhalle Lindau*, Kategorie *🏛️ Inselhalle*, als „beschäftigt“, Wolf (User 6) als Organisator **und** Teilnehmer — sonst erscheinen sie weder in seinem Kalender noch am Handy. Aufgaben, die in einem Dienst stattfinden, bekommen ihre Frist auf diesen Tag. *(Präzisiert 22.09.2026 auf Wolfs Anweisung — die alte Kurzform „nie als Termin anlegen“ wurde als Verbot missverstanden.)*

**Stufen hängen als many2many an Projekten.** Ein neues Projekt ohne Stufenzuordnung kippt alles in eine Spalte, und eine Aufgabe in einer Stufe, die ihr Projekt nicht kennt, ist **unsichtbar statt unsortiert**. Nach jedem Projektanlegen prüfen — muss 0 ergeben:

```sql
select count(*) from project_task pt
join project_project p on p.id=pt.project_id and p.active
where pt.active and pt.stage_id is not null
  and not exists (select 1 from project_task_type_rel r
                  where r.project_id=pt.project_id and r.type_id=pt.stage_id);
```

**Was Odoo 19 kann und lange ungenutzt blieb:** `depend_on_ids` (echte Abhängigkeiten), `is_template` (Projektvorlagen), `hr_timesheet` (Zeiterfassung), `sale_management` (Angebote). Vor jedem Eigenbau prüfen, ob das Feld schon existiert.

**Feldnamen in Odoo 19 haben sich geändert.** Die DB-Spalte beweist nichts — sie kann veraltet weiterexistieren. Immer `ir_model_fields` befragen. Bekannt: `ir.filters.user_id` → **`user_ids`** (many2many, `sort` ist Pflichtfeld) · `res.users.groups_id` → **`group_ids`**.

## Verifikation — was ein Test beweist und was nicht

Am 09.09.2026 sind drei „geprüfte" Änderungen im Betrieb gescheitert. Daraus:

- **`compile()` beweist nur, dass der Code lesbar ist.** Er findet keine fehlenden Namen und keine Typfehler. Zwei Cron-Läufe starben daran (`date_deadline` ist ein *datetime*, nicht *date*; `hasattr` existiert in Odoos `safe_eval` **nicht** — `isinstance` schon).
- **Eine Prüfung, die nicht korrekt scheitern kann, ist schlechter als keine** — man glaubt ihr. (Die Filter-Selbstprüfung meldete für jeden Filter „nicht auswertbar", obwohl alle 17 in Ordnung waren.)
- **Nach jedem Reload das Ergebnis am Ziel messen**, nicht den Rückgabewert lesen. Prometheus: `curl /api/v1/rules` **und** `reloadConfigSuccess`.
- **Bei Zeitplänen beide Zeitzonen prüfen.** systemd rechnet in der Zeitzone des **Wirts**, Container-Cron oft in **UTC**. Ein Kopierlauf „nach" dem Abzug lief dadurch drei Stunden **davor** und kopierte täglich die Datei vom Vortag — mit grüner Erfolgsmeldung.
- **Zeilenenden:** Unter Windows geschriebene Skripte für Linux **binär oder mit `newline='
'`** schreiben. `
` ist kein Syntaxfehler, deshalb meldet `bash -n` auf der Windows-Seite nichts — auf dem Ziel scheitert es trotzdem.

## Peer-Review (Vier-Augen-Prinzip) — PFLICHT

**Agenten reviewen die Arbeit des jeweils anderen.** Kein Agent nimmt seine eigene Arbeit ab.

**Review-pflichtig:**
- Code/Skripte, die produktiv laufen (Services, Webhooks, Handler, Automationen)
- Config-Änderungen an Kernservern (Proxmox, Odoo, OpenClaw, Alertmanager, Netzwerk/UCG)
- Änderungen an diesem Protokoll

**Ablauf:**
1. Ausführender Agent: Arbeit fertig → Odoo-Task-Chatter: was geändert, wo (Pfad/Host), wie selbst verifiziert, Backup-Pfad → **@Mention an Review-Agent**, Stage bleibt "In Arbeit"
2. Review-Agent: prüft mit **echten Belegen** (Datei lesen, Endpoint aufrufen, Logs ansehen — nicht raten): Funktion, Sicherheit (Secrets? Auth? Blast-Radius?), Rote-Linien-Konformität, Doku vorhanden
3. Ergebnis im Chatter: ✅ Review OK (mit Beleg) oder ❌ Befunde (konkret, mit Fundstelle)
4. Erst nach ✅ Review → Stage Erledigt

**Review-Zuordnung (Standard):** Jarvis-Arbeit → Claude reviewt · Claude-Arbeit → Jarvis reviewt · Antigravity-Arbeit → Jarvis oder Claude. Reviewer nicht erreichbar >48h → Wolf entscheidet.

**Kleinkram** (Doku-Tippfehler, Log-Rotation, read-only-Analysen) braucht kein Review — im Zweifel: Review.

## Eine Wahrheit — keine parallelen Versionen (seit 28.09.2026)

Wolf am 28.09.2026: *„Das kann ja keine Best Practice sein, dass wenn zwei Mitarbeiter am gleichen Projekt arbeiten, sie sich gegenseitig zurückhauen.“* Anlass (Odoo #1593): Surface-Schritte M1/M2 doppelt gebaut (Jarvis auf `main`, Claude parallel in einem lokalen Zweig — Jarvis' Review-Bitten kamen nie an) · Jarvis las ein Protokoll vom 06.09. · Webhook-Handler in drei Fassungen (Server, zwei Repo-Kopien) · Claude-Commits lagen tagelang nur lokal.

**1. Vor jeder Arbeit — Pflicht, in dieser Reihenfolge:**
1. `git pull --rebase` im Repo. Scheitert das → erst klären, dann arbeiten.
2. Die Aufgabe **samt Chatter** lesen. Steht dort eine Übergabe oder Review-Bitte an dich, ist **die** zuerst dran.
3. Offene Erwähnungen an dich suchen (`mail.message`, Text enthält `@Claude` bzw. `@Jarvis`/`@Antigravity`, letzte 7 Tage). Unbeantwortete Review-Bitten gehen vor neuer Arbeit.

**2. Aufgabe sperren (Lock):** Eigenes Sperr-Schlagwort setzen + Chatter „🤖 [Name] übernimmt“. Trägt eine Aufgabe (oder ihre Oberaufgabe) das Schlagwort eines **anderen** Agenten → **nicht anfassen**, auch nicht „nur schnell“. Mitarbeiten nur nach Absprache im Chatter. Beim Abschluss oder Abgeben das Schlagwort entfernen.

**3. Git:**
- **Commit = Push.** Direkt nach jedem Commit `git push`. Ungepushte Arbeit gilt als **nicht erledigt** — sie existiert für die anderen nicht. Kann ein Agent nicht pushen, meldet er das sofort im Chatter, statt weiterzubauen.
- **Nur auf `main`**, keine langlebigen Zweige oder Worktrees. Ein Zweig lebt höchstens eine Sitzung und wird vor Sitzungsende gemergt oder gelöscht.
- `/opt/frawo-repo` auf CT150 ist ein **Spiegel** (wird stündlich hart auf `origin/main` gesetzt) — dort nie arbeiten, lokale Commits gingen verloren. Jarvis arbeitet in `/root/.openclaw/FraWo`.

**4. Server und Repo:** Hat eine Datei auf einem Server eine Kopie im Repo (z. B. `infra/openclaw/odoo_webhook_handler.py`), gilt: **vorher** Server-Stand gegen Repo vergleichen, **nachher** Server-Stand ins Repo kopieren, committen, pushen — im selben Arbeitsgang. Eine Abweichung zwischen Server und Repo ist ein Fehler, keine zweite Meinung.

**5. Kopien sind Kopien:** `AGENTS.md`, `NOW.md`, `INFRA.md` außerhalb des Repos (Jarvis-Workspace, `C:\Users\StudioPC\AGENTS.md`) werden automatisch befüllt bzw. verweisen nur auf das Repo. Wer dort etwas ändert, erzeugt die nächste zweite Wahrheit.

## Eskalation

- Blocker, den ein anderer Agent lösen kann → Odoo-Chatter-Mention am Task
- Blocker, den nur Wolf lösen kann (Freigabe, Passwort, Hardware) → kurz + konkret an Wolf, EINE Frage, mit Empfehlung
- Konflikt zwischen Agenten (gleicher Task/gleiche Ressource) → Jarvis koordiniert (persistenter Agent = Schiedsstelle)

---

*Änderungen an diesem Protokoll: nur mit Wolfs Zustimmung, und nur hier im Repo. Die Kopie in Jarvis' Workspace befüllt `scripts/frawo-wissen-sync.sh` stündlich automatisch.*

# FraWo "Ein Werkzeug": Odoo-Struktur + KI-Struktur-Schicht — Design

## 1. Ziel

FraWo nutzt aktuell dieselben generischen Odoo-Apps (Projekt/Aufgabe/Kalender) für vier
fachlich unterschiedliche Arbeitsarten:

1. **Events/Verleih** — Equipment-Verleih für einen Kunden-Termin/Zeitraum
2. **Dienstleistungen** — Fachkraft-Tagessätze (z.B. Auftrag S00036)
3. **Franz' Bauvorhaben** — längerfristige Werkstatt-/Bauprojekte ohne festen Event-Termin
4. **Interne FraWo-Ziele** — Epics wie Website, Radio, IT-Ausbau

Wolf will das weiter gemeinsam in Odoo verwalten (kein Systembruch), aber sauberer
strukturiert — und ausdrücklich so, dass das System ihm **netto Arbeit abnimmt**, nie
welche hinzufügt (Wolf wörtlich: *"ich erwarte, dass genau dieses System erschaffen
wird, das mir hilft besser und produktiver zu arbeiten — nicht mehr Arbeit schafft als
es löst"*). Er will nicht lernen, wie Odoo strukturiert ist — das System soll aus seinem
chaotischen, natürlichsprachigen Input selbst die Struktur erzeugen.

**Ausdrücklicher Qualitätsanspruch (Wolf, 06.09.2026):** *"das alte bisherige Ollama war
ein schlechter Witz.. bitte nur anfangen wenn wir das so professionell umsetzen, dass es
ein zukunftssicheres Projekt ist."* Dieser Teil bekommt daher den vollen
Brainstorming→Spec→Plan-Prozess statt eines Ad-hoc-Fixes.

## 2. Odoo-Struktur (Grundlage, unabhängig von KI)

- **4 Spuren als Tags**, nicht als getrennte Apps: 🎪 Event/Verleih · 🧑‍🔧 Dienstleistung ·
  🔨 Bauvorhaben · 🏢 Intern. Sofort im Kanban sichtbar/filterbar, keine neue Datenstruktur.
- **Fester Projekt-Rahmen statt Auto-Wildwuchs:** Odoo legt aktuell bei jeder
  Auftragsbestätigung automatisch ein neues `project.project` an (z.B. "S00036" aus einer
  einzigen Order). Das wird abgeschaltet — alles läuft in den bestehenden festen
  Projekten (Aufträge & Events / Systeme & IT / Wolf Privat), Tags übernehmen die
  Unterscheidung.
- **Kalender als gemeinsame Brücke:** Die heute gebauten Automatiken (Aufgaben-Frist →
  Kalendertermin mit Konfliktpuffer; Auftrags-Liefertermin → Kalendertermin) bleiben der
  EINE Weg, wie alle 4 Spuren im Kalender ankommen. Kein neuer Mechanismus nötig.

*(Status: Grundrichtung von Wolf per Sektion bereits bestätigt, 06.09.2026.)*

## 3. Capture → Struktur → Dispatch (die eigentliche Entlastung)

Der bereits reparierte Telegram-Bot (@Frawo_bot / OpenClaw, interne Identität "Jarvis")
wird die einzige Eingabe, die Wolf im Alltag braucht:

1. **Capture:** Wolf schickt einen chaotischen Satz/Sprachnachricht an den Bot
   ("Herbalife Aufbau 7:30 für mich", "Franz soll ein Regal bauen, ca. 2m breit").
2. **Klassifikation (günstig, lokal):** Stichwort-basierte Spuren-Erkennung — bereits als
   `frawo.task.formatter.detect_role()` vorhanden, kein LLM-Aufruf nötig für die grobe
   Einordnung.
3. **Strukturierung (lokal, Ollama):** Ein rollenspezifischer Prompt formt den rohen Satz
   in ein festes Format. Für Franz existiert bereits ein sehr gutes Prompt-Template
   (`PROMPT_FRANZ` in `task_formatter.py`): 🔨 Was / 📐 Maße&Material / ✅ Fertig wenn /
   💬 Warum — mit der Regel, bei fehlenden Angaben "(Maß vor Ort)" zu schreiben statt zu
   erfinden. Franz bekommt so nie eine vage Aufgabe, die er selbst nachbohren muss.
4. **Eskalation (kostenpflichtig, nur bei Bedarf):** Jarvis läuft primär auf Ollama;
   Claude/Anthropic bzw. Gemini/Antigravity werden nur zugeschaltet, wenn die lokale
   Strukturierung erkennbar unsicher/mehrdeutig ist (z.B. Konfidenz-Heuristik oder
   Ollama liefert leere/zu kurze Antwort). Deckt Wolfs Kostenvorgabe.
5. **Dispatch:** Fertige Aufgabe (Tag + Beschreibung + ggf. Kalendertermin) wird
   angelegt. Owner/Deadline werden NICHT autonom gesetzt, sondern Wolf als Vorschlags-
   Aktivität vorgelegt (bereits vorhandenes, bewusst konservatives Verhalten in
   `project_task.py` — bleibt so).
6. **Täglicher Kurzbericht:** Bestehender `frawo-daily-briefing`-Cron wird Wolfs
   Status-Check statt eines Odoo-Logins — was steht heute an, was braucht seine
   Entscheidung, was ist überfällig.

## 4. Bestandsaufnahme: was schon existiert (und warum es nicht reicht)

Der Code für Schritt 2+3+5 existiert bereits im `frawo_agent`-Addon
(`ollama_client.py`, `task_formatter.py`, `project_task.py._cron_process_agent_queue`)
und ist konzeptionell solide. Er lief aber nie zuverlässig:

- Ollama-Server unter der hinterlegten Adresse (`172.17.0.1:11434`) **nicht erreichbar**
  (Connection refused, geprüft 06.09.2026 aus dem laufenden Odoo-Container).
- **Kein `ir.cron`-Eintrag** für `_cron_process_agent_queue` — die Warteschlange wird von
  nichts automatisch abgearbeitet.
- Ergebnis: 141 Aufgaben hängen unbearbeitet in `agent_state=queued`, nur 16 wurden je
  erfolgreich verarbeitet, 31 mit Fehler stehen geblieben (Zahlen vom 06.09.2026).

Das ist exakt das Muster, das Wolf als "schlechter Witz" bezeichnet hat: gut gemeint,
nie sauber in Betrieb genommen.

## 5. Hardware-Entscheidung

Ressourcen-Check der zwei bestehenden Proxmox-Hosts (06.09.2026, unter normaler
Tageslast):

| Host | CPU | RAM frei | Load (1-Min) | GPU |
|---|---|---|---|---|
| ProDesk (stock-pve) | i7-7700T, 8 Threads | 457 MB, swappt bereits (3,5GB) | 9,67 — überlastet | nur Intel HD 630 (keine CUDA) |
| ThinkCentre (proxmox-anker) | i5-8500T, 6 Threads | 554 MB, swappt (3,3GB) | 28,94 — massiv überlastet | nur Intel UHD 630 |

Beide Hosts tragen bereits kritische Dauer-Dienste (DNS, VPN, Passwort-Tresor, Odoo,
Paperless, Backup, Radio, OpenClaw) und haben keine dedizierte GPU. Ein KI-Workload
obendrauf würde entweder unbrauchbar langsam laufen oder bestehende, wichtige Dienste
ausbremsen.

**Entscheidung:** Separater Rechner (vorhandenes Ersatz-Optiplex in der Villa), um die
KI-Last von der kritischen Infrastruktur zu trennen. **Offen:** genaues Optiplex-Modell/
Baujahr und ob Platz+Stromversorgung für eine (ggf. gebrauchte, günstige) GPU vorhanden
ist — Wolf prüft das. Richtwert: ein 8B-Modell (wie das bisherige `llama3:8b`) läuft auf
reiner CPU spürbar zäh; eine gebrauchte GPU mit 8-12GB VRAM (grob 150-250€) macht den
Unterschied zwischen "unbrauchbar" und "alltagstauglich".

## 6. Betriebs-Anforderungen ("professionell/zukunftssicher")

Damit dies kein zweiter "schlechter Witz" wird, MUSS die Umsetzung folgende Kriterien
erfüllen, bevor sie als fertig gilt:

- Ollama läuft als **dauerhafter systemd-Service** (nicht manuell gestartet), mit
  Autostart nach Reboot.
- **Monitoring/Alerting bei Ausfall:** Prometheus-Check auf Ollama-Erreichbarkeit +
  Warteschlangen-Länge, ins bestehende Grafana/Prometheus-Setup (CT150) integriert,
  analog zum bestehenden Backup-TÜV-Muster.
- Der Verarbeitungs-Cron läuft **zuverlässig und beobachtbar** (kein "läuft, wenn zufällig
  wer dran denkt") — Warteschlangen-Länge > Schwellwert löst eine Meldung aus.
- **Dokumentiert** in `NOW.md` (Was-wo-läuft) und als Referenz-Memory.
- Getestet mit echten, dann wieder entfernten Testaufgaben je Spur (Event, Dienstleistung,
  Bauvorhaben, Intern), bevor auf die 141 hängenden Alt-Aufgaben losgelassen wird.

## 7. Edge Cases

- **Ollama antwortet leer/Timeout:** bestehende Fehlerbehandlung greift bereits
  (`agent_state=error`, Log-Eintrag) — bleibt, plus Eskalation an Claude/Gemini als
  zweiten Versuch statt sofortigem Fehlerstatus.
- **Mehrdeutige Spur-Zuordnung** (Stichwort passt auf keine/mehrere Kategorien): geht an
  "review"-Rolle (bestehendes Verhalten), keine Rätselraten-Automatik.
- **Franz-Aufgabe mit fehlenden Maßen:** Prompt schreibt "(Maß vor Ort)" statt zu
  erfinden — bereits im bestehenden `PROMPT_FRANZ` korrekt gelöst, nicht antasten.
- **141 hängende Alt-Aufgaben:** werden NICHT automatisch in einem Rutsch verarbeitet,
  sondern erst nach erfolgreichem Testlauf (siehe Abnahmekriterien) — Vermeidung eines
  zweiten "blind alles auf einmal"-Vorfalls wie beim Kalender-Duplikat-Fehler.

## 8. Abnahmekriterien

1. Ollama läuft dauerhaft, übersteht einen Host-Neustart ohne manuellen Eingriff.
2. Cron verarbeitet die Warteschlange nachweislich automatisch (nicht nur einmalig von
   Hand angestoßen).
3. Ausfall von Ollama erzeugt eine sichtbare Meldung (Telegram/Grafana), nicht stille
   Stagnation.
4. Je eine Testaufgabe pro Spur (Event/Dienstleistung/Bauvorhaben/Intern) wird korrekt
   erkannt, strukturiert und (bei Bedarf) eskaliert — mit echten, danach entfernten
   Testdaten verifiziert.
5. Die 141 hängenden Alt-Aufgaben werden erst NACH bestandenem Test in kontrollierten
   Tranchen nachgeholt, mit Stichproben-Prüfung.

## 9. Testplan

- Testaufgabe je Spur anlegen → prüfen: richtige Rollen-/Spur-Erkennung, korrektes
  Prompt-Format, korrekte Aktivität für Wolf, keine erfundenen Fakten.
- Ollama-Server gezielt stoppen → prüfen: Fehlerpfad + Eskalation an Claude/Gemini
  funktioniert, keine Endlosschleife, keine verlorene Aufgabe.
- Host-Neustart des neuen Rechners simulieren (`reboot`) → prüfen: Ollama-Service kommt
  automatisch wieder hoch.
- Nach Testlauf: 5-10 der 141 hängenden Alt-Aufgaben als erste Tranche verarbeiten,
  Stichprobe manuell gegenlesen, erst dann den Rest freigeben.

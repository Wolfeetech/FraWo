# Gedächtnis-Recall aktivieren — Umsetzungsplan

> **Für ausführende Agenten:** ERFORDERLICHE UNTER-SKILL: `superpowers:subagent-driven-development` (empfohlen) oder `superpowers:executing-plans`, Aufgabe für Aufgabe. Schritte nutzen Checkbox-Syntax (`- [ ]`).

**Ziel:** Die bereits laufende, lokale und kostenlose Gedächtnissuche mit dem Wissen füllen, das FraWo tatsächlich hat — und den automatischen Abruf so einschalten, dass er kein Geld verbrennt.

**Architektur:** Die Suchmaschine läuft bereits (lokale Einbettungen, Vektorspeicher, Volltext — alles auf dem Anker, ohne API). Sie kennt aber nur 15 Dateien. Dieser Plan erweitert die **Quellen** (Sitzungsverlauf + FraWo-Livedokumente) und schaltet erst danach den **Abruf** ein. Quellen sind kostenlos, der Abruf kostet — deshalb diese Reihenfolge.

**Technik:** OpenClaw 2026.7.1 im Docker-Container `openclaw` in CT150 auf dem Anker · Einbettungsmodell `embeddinggemma-300m` (lokal, 768 Dimensionen) · `sqlite-vec` + Volltextindex · Konfiguration in `/root/.openclaw/openclaw.json`

---

## Ausgangslage (am 01.08.2026 gemessen, nicht geschätzt)

| Was | Zustand |
|---|---|
| Einbettungen | **bereit**, Anbieter `local`, keine API-Kosten |
| Vektorspeicher / Volltext | **bereit**, 768 Dimensionen |
| Indexiert | **15 Dateien · 57 Abschnitte** |
| Quellen | nur `memory` |
| Sitzungsverlauf | **1.105 Dateien · 438 MB — nicht indexiert** |
| Dreaming | **aus** |
| Recall-Speicher | **0 Einträge, 0 befördert** |
| Active Memory | **abgeschaltet** |

**Die Maschine läuft. Der Tank ist fast leer, und niemand dreht den Schlüssel.**

## Globale Randbedingungen

- **Kein KI-Budget.** Am 30.07.2026 lief das Anthropic-Limit voll, das Gateway fiel auf `github-copilot/gpt-4.1` zurück. Jede Änderung, die pro Antwort einen zusätzlichen Modellaufruf erzeugt, ist begründungspflichtig.
- **Lokale Einbettung ist kostenlos und funktioniert.** Lokale Texterzeugung ist auf dieser Hardware als unbrauchbar verifiziert. Der Unterschied ist entscheidend: Suchen ja, Denken nein.
- **Konfiguration überlebt Neustarts.** `/root/.openclaw` ist das Docker-Volume `openclaw_openclaw-data`, Container-Richtlinie `unless-stopped`.
- **Nach jeder Änderung messen, nicht annehmen.** Prüfbefehl ist immer `openclaw memory status --deep`.
- **Rückweg vor jedem Schritt.** Keine Änderung ohne Sicherungskopie.
- **Zwei Ausführungsebenen — nicht verwechseln, sonst laufen Befehle ins Leere:**
  - **[IM CONTAINER]** — alles mit `openclaw …`:
    `ssh anker-pve "pct exec 150 -- docker exec openclaw sh -c '<BEFEHL>'"`
  - **[IN CT150]** — alles mit `docker …`, `git …`, `crontab …`:
    `ssh anker-pve "pct exec 150 -- <BEFEHL>"`

  Jeder Schritt unten ist entsprechend markiert.

---

## Aufgabe 1: Ausgangsstand sichern und schriftlich festhalten

**Dateien:**
- Sichern: `/root/.openclaw/openclaw.json` → `openclaw.json.vor-recall-20260801`
- Anlegen: `/root/.openclaw/recall-ausgangsstand.txt`

**Schnittstellen:**
- Liefert: die Sicherungskopie, auf die sich jede spätere Aufgabe als Rückweg bezieht.

- [ ] **Schritt 1: Sicherungskopie der Konfiguration**

```sh
cp /root/.openclaw/openclaw.json /root/.openclaw/openclaw.json.vor-recall-20260801
```

- [ ] **Schritt 2: Prüfen, dass die Kopie existiert und nicht leer ist**

```sh
ls -l /root/.openclaw/openclaw.json.vor-recall-20260801
```
Erwartet: Größe > 400 Bytes. Bei 0 Bytes abbrechen — Rückweg fehlt.

- [ ] **Schritt 3: Ausgangsmessung festhalten**

```sh
openclaw memory status --deep > /root/.openclaw/recall-ausgangsstand.txt 2>&1; cat /root/.openclaw/recall-ausgangsstand.txt
```
Erwartet: `Indexed: 15/15 files · 57 chunks`, `Sources: memory`, `Embeddings: ready`.

**Diese Zahl ist der Vergleichswert für alles Folgende.**

---

## Aufgabe 2: Sitzungsverlauf als Quelle zuschalten

**Warum zuerst:** Das ist der einzige große, wirklich unstrukturierte Bestand — 438 MB Gesprächsverlauf, heute nur beschreibbar, nicht lesbar. Und es kostet nichts, weil die Einbettung lokal läuft.

**⚠ Vorher lesen — Sicherheitsabwägung:** In diesen Verläufen wurden über Monate Zugangsdaten besprochen (siehe Odoo #815, gitleaks-Fund von 13 Alt-Secrets). Indexieren macht sie **durchsuchbar**. Der Index liegt lokal in CT150 und verlässt den Rechner nicht — aber wer Zugriff auf den Agenten hat, kann danach fragen. **Erst Aufgabe 6 lesen, dann entscheiden.**

**Schnittstellen:**
- Verbraucht: die Sicherungskopie aus Aufgabe 1.
- Liefert: einen Index, der auch Gesprächsverläufe enthält — Voraussetzung für Aufgabe 4 und 5.

- [ ] **Schritt 1: Änderung zuerst trocken prüfen**

```sh
openclaw config set agents.defaults.memorySearch.sources '["memory","sessions"]' --strict-json --dry-run
```
Erwartet: Ausgabe ohne Fehler, zeigt die geplante Änderung. Bei Schema-Fehler abbrechen.

- [ ] **Schritt 2: Änderung setzen**

```sh
openclaw config set agents.defaults.memorySearch.sources '["memory","sessions"]' --strict-json
```

- [ ] **Schritt 3: Konfiguration auf Gültigkeit prüfen**

```sh
openclaw config validate
```
Erwartet: gültig. Bei Fehler sofort Rückweg (siehe unten).

- [ ] **Schritt 4: Index neu aufbauen — das dauert**

```sh
time openclaw memory index --force
```
1.105 Dateien mit einem CPU-Einbettungsmodell. **Laufzeit im Bereich einer halben bis mehrerer Stunden erwarten.** Nicht abbrechen, weil es lange dauert — nur bei Fehlermeldungen.

- [ ] **Schritt 5: Ergebnis messen**

```sh
openclaw memory status --deep
```
Erwartet: `Sources: memory, sessions`, Dateizahl **deutlich über 15**, Abschnitte **deutlich über 57**, `Dirty: no`, `Vector store: ready`.

**Wenn die Zahl bei 15/57 steht, hat die Änderung nicht gegriffen — nicht weitermachen, Ursache suchen.**

- [ ] **Schritt 6: Rückweg dokumentieren**

Falls etwas schiefgeht:
```sh
cp /root/.openclaw/openclaw.json.vor-recall-20260801 /root/.openclaw/openclaw.json && openclaw memory index --force
```

---

## Aufgabe 3: FraWo-Livedokumente aufnehmen — aber nur die lebenden

**Warum getrennt von Aufgabe 2:** Hier wird eine inhaltliche Entscheidung getroffen, keine technische.

**Die Entscheidung:** Das Repo hat 2,5 MB Markdown in 562 Dateien. Davon sind `artifacts/` (766.000 Zeichen erzeugte Berichte), `DOCS/Task_Archive/`, `DOCS/plans/` und `archive/` **Ablagerung, kein Wissen**. Der echte Live-Stand ist `NOW.md` mit 11 KB.

**Es wird ausschließlich aufgenommen:** `NOW.md`, `OPERATIONS/`, `SSOT/`.

Das ist die gleiche Entscheidung, die hinter NOW.md steht: wenig Aktuelles schlägt viel Historisches. Eine Suche weiß nicht, was gilt — sie liefert, was passt. Ein Fund aus `Task_Archive` sieht genauso überzeugend aus wie NOW.md.

**Dateien:**
- Anlegen in CT150: `/opt/frawo-repo` (Klon)
- Anlegen: `/usr/local/bin/frawo-wissen-sync.sh`
- Ziel: `/root/.openclaw/workspace/memory/frawo/`

**Schnittstellen:**
- Verbraucht: den funktionierenden Index aus Aufgabe 2.
- Liefert: `frawo/`-Unterordner im Gedächtnis, auf den Aufgabe 4 seine Prüffragen stellt.

- [ ] **Schritt 1: Repo in CT150 klonen** (öffentlich, kein Schlüssel nötig)

Nicht im Container, sondern in CT150 selbst:
```sh
ssh anker-pve "pct exec 150 -- git clone --depth 1 https://github.com/Wolfeetech/FraWo.git /opt/frawo-repo"
```

- [ ] **Schritt 2: Prüfen, dass NOW.md da ist**

```sh
ssh anker-pve "pct exec 150 -- ls -l /opt/frawo-repo/NOW.md"
```
Erwartet: Datei existiert, ca. 11 KB.

- [ ] **Schritt 3: Sync-Skript anlegen**

In CT150 unter `/usr/local/bin/frawo-wissen-sync.sh`:
```sh
#!/bin/bash
# Holt NUR die lebenden FraWo-Dokumente ins Gedaechtnis.
# Bewusst NICHT: DOCS/, artifacts/, archive/ - das ist Ablagerung.
set -euo pipefail

REPO=/opt/frawo-repo
VOL=$(docker volume inspect openclaw_openclaw-data --format '{{.Mountpoint}}')
ZIEL="$VOL/workspace/memory/frawo"

git -C "$REPO" fetch --depth 1 origin main
git -C "$REPO" reset --hard origin/main

mkdir -p "$ZIEL"
rm -rf "${ZIEL:?}"/*
cp "$REPO/NOW.md" "$ZIEL/"
cp -r "$REPO/OPERATIONS" "$ZIEL/"
cp -r "$REPO/SSOT" "$ZIEL/"

ANZAHL=$(find "$ZIEL" -name '*.md' | wc -l)
if [ "$ANZAHL" -lt 5 ]; then
  echo "FEHLER: nur $ANZAHL Dateien uebernommen - Abbruch, Index nicht angefasst" >&2
  exit 1
fi
echo "$ANZAHL Dateien uebernommen"

docker exec openclaw openclaw memory index
```

Die Prüfung auf mindestens 5 Dateien ist Absicht: ein leerer Kopiervorgang darf nicht dazu führen, dass der Index leergeräumt wird.

- [ ] **Schritt 4: Ausführbar machen und einmal laufen lassen**

```sh
ssh anker-pve "pct exec 150 -- chmod +x /usr/local/bin/frawo-wissen-sync.sh"
ssh anker-pve "pct exec 150 -- /usr/local/bin/frawo-wissen-sync.sh"
```
Erwartet: „N Dateien uebernommen" mit N ≥ 40.

- [ ] **Schritt 5: Im Index nachsehen**

```sh
openclaw memory status --deep
```
Erwartet: Dateizahl um etwa 42 höher als nach Aufgabe 2.

- [ ] **Schritt 6: Täglich nachziehen**

In CT150 als Cron-Eintrag, nachts vor den Sicherungen:
```
15 1 * * * /usr/local/bin/frawo-wissen-sync.sh >> /var/log/frawo-wissen-sync.log 2>&1
```

- [ ] **Schritt 7: Prüfen, dass der Eintrag steht**

```sh
ssh anker-pve "pct exec 150 -- crontab -l | grep frawo-wissen"
```

---

## Aufgabe 4: Trefferqualität prüfen — bevor irgendetwas automatisch abruft

**Warum:** Ein Index, der falsche Antworten liefert, ist schlimmer als keiner. Bisher hat noch nie jemand gemessen, ob die Suche brauchbare Treffer bringt — `Recall-Speicher: 0 Einträge`.

**Schnittstellen:**
- Verbraucht: den gefüllten Index aus Aufgabe 2 und 3.
- Liefert: die Entscheidungsgrundlage für Aufgabe 5. **Bei schlechtem Ergebnis endet der Plan hier.**

- [ ] **Schritt 1: Frage mit bekannter richtiger Antwort**

```sh
openclaw memory search "Warum scheitert systemctl reload prometheus" --max-results 5
```
Erwartet: `NOW.md` unter den Treffern, mit dem Hinweis auf `/usr/local/bin/prometheus-neu-laden.sh`.

- [ ] **Schritt 2: Frage, die nur im Sitzungsverlauf steht**

```sh
openclaw memory search "Kuehlhaenger Lindauer Insel" --max-results 5
```
Erwartet: Treffer aus dem Gesprächsverlauf vom 31.07.

- [ ] **Schritt 3: Gegenprobe — Frage ohne Antwort im Bestand**

```sh
openclaw memory search "Ersatzteilnummer Ruettelplatte Wacker" --max-results 5
```
Erwartet: **keine oder erkennbar schwache Treffer.** Liefert die Suche hier selbstbewusst irgendetwas, ist sie unbrauchbar — das ist der wichtigste der drei Tests.

- [ ] **Schritt 4: Ergebnis festhalten**

```sh
openclaw memory search "Warum scheitert systemctl reload prometheus" --max-results 5 > /root/.openclaw/recall-guetepruefung-20260801.txt 2>&1
```

**Abbruchbedingung:** Wenn Schritt 1 oder 2 die bekannte Antwort nicht findet, oder Schritt 3 überzeugend danebenliegt — **hier aufhören** und in Odoo festhalten. Aufgabe 5 baut auf einer funktionierenden Suche auf.

---

## Aufgabe 5: Active Memory eng begrenzt einschalten

**Was Active Memory wirklich ist** — und das ist der Punkt, an dem die Erwartung am weitesten von der Wirklichkeit abweicht:

> „Runs a bounded blocking **memory sub-agent** before eligible conversational replies"

Das ist **keine Vektorsuche**, sondern ein **eigener Modellaufruf vor jeder Antwort**. Er entscheidet, was nachgeschlagen wird, und blockiert die Antwort so lange. Das Modul hat `timeoutMs`, `circuitBreakerMaxTimeouts` und `circuitBreakerCooldownMs` — die Entwickler rechnen selbst damit, dass es klemmt.

**Für FraWo heißt das:** Jede Telegram-Nachricht an @Frawo_bot kostet ab hier **zwei** Modellaufrufe statt einem. Bei einem Konto, das am 30.07. ins Limit gelaufen ist, ist das die teuerste Zeile dieses Plans.

**Deshalb: erst in einem einzigen Chat, mit billigem Modell, kurzem Zeitlimit.**

**Schnittstellen:**
- Verbraucht: bestandene Güteprüfung aus Aufgabe 4.
- Liefert: Messwerte für die Kostenentscheidung in Aufgabe 6.

- [ ] **Schritt 1: Eigene Chat-Kennung ermitteln** — **[IN CT150]**

```sh
docker logs openclaw 2>&1 | grep -o 'chatId=[0-9]*' | sort -u | tail -5
```
Erwartet: u. a. `chatId=5924907152` (Wolfs Telegram-Chat aus dem Verlauf vom 30.07.).

- [ ] **Schritt 2: Eng begrenzt einschalten — trocken prüfen**

```sh
openclaw config set plugins.entries.active-memory '{"enabled":true,"config":{"enabled":true,"allowedChatIds":["5924907152"],"model":"github-copilot/gpt-4.1","thinking":"off","queryMode":"message","promptStyle":"precision-heavy","timeoutMs":8000,"maxSummaryChars":400,"circuitBreakerMaxTimeouts":3,"circuitBreakerCooldownMs":300000,"logging":true}}' --strict-json --dry-run
```

Begründung jeder Einstellung:
- `allowedChatIds` — **nur ein Chat**, nicht das ganze System
- `model: github-copilot/gpt-4.1` — das Modell, auf das am 30.07. ohnehin zurückgefallen wurde, statt Anthropic-Kontingent zu verbrauchen
- `thinking: off` — kein Nachdenken für eine Nachschlage-Frage
- `queryMode: message` — nur die aktuelle Nachricht, nicht der ganze Verlauf
- `promptStyle: precision-heavy` — lieber nichts liefern als Falsches
- `timeoutMs: 8000` — nach 8 Sekunden blockiert nichts mehr
- `circuitBreaker` — nach 3 Zeitüberschreitungen 5 Minuten Ruhe
- `logging: true` — sonst ist die Kostenmessung in Aufgabe 6 nicht möglich

- [ ] **Schritt 3: Setzen und prüfen**

```sh
openclaw config set plugins.entries.active-memory '{"enabled":true,"config":{"enabled":true,"allowedChatIds":["5924907152"],"model":"github-copilot/gpt-4.1","thinking":"off","queryMode":"message","promptStyle":"precision-heavy","timeoutMs":8000,"maxSummaryChars":400,"circuitBreakerMaxTimeouts":3,"circuitBreakerCooldownMs":300000,"logging":true}}' --strict-json
openclaw config validate
```

- [ ] **Schritt 4: Gateway neu starten**

```sh
ssh anker-pve "pct exec 150 -- docker restart openclaw"
```

- [ ] **Schritt 5: Prüfen, dass das Modul jetzt an ist**

```sh
openclaw plugins list 2>&1 | grep -A2 'Active'
```
Erwartet: Status `enabled`.

- [ ] **Schritt 6: Echttest über Telegram**

An @Frawo_bot schicken: **„Was war die Falle mit dem Prometheus-Reload?"**

Erwartet: Die Antwort nennt `/usr/local/bin/prometheus-neu-laden.sh`, ohne dass die Frage den Dateinamen enthielt.

- [ ] **Schritt 7: Nachsehen, ob wirklich das Gedächtnis geantwortet hat** — **[IN CT150]**

```sh
docker logs --since 10m openclaw 2>&1 | grep -i 'active-memory\|memory' | tail -20
```
Erwartet: Einträge zum Gedächtnis-Unteragenten. **Kommt hier nichts, hat das Modell die Antwort erfunden** — das ist ein Fehlschlag, kein Erfolg.

---

## Aufgabe 6: Kosten und Risiko messen, dann entscheiden

**Schnittstellen:**
- Verbraucht: die Protokolle aus Aufgabe 5.
- Liefert: die Entscheidung, ob Active Memory für alle Chats freigegeben wird — und den Odoo-Eintrag dazu.

- [ ] **Schritt 1: Zusätzliche Modellaufrufe zählen** — **[IN CT150]**

```sh
docker logs --since 24h openclaw 2>&1 | grep -c 'model-fetch. start'
```
Vergleich mit dem Wert vor Aufgabe 5 (aus `recall-ausgangsstand.txt` nachvollziehbar über das Datum). **Erwartet ist etwa eine Verdopplung im Testchat.**

- [ ] **Schritt 2: Auf Limit-Meldungen prüfen** — **[IN CT150]**

```sh
docker logs --since 24h openclaw 2>&1 | grep -i 'usage limit\|rate_limit' | tail -5
```
Erwartet: leer. **Steht hier etwas, sofort Aufgabe 5 zurücknehmen** — erst **[IM CONTAINER]**:
```sh
openclaw config set plugins.entries.active-memory.config.enabled false --strict-json
```
dann **[IN CT150]**:
```sh
docker restart openclaw
```

- [ ] **Schritt 3: Sicherheitsprüfung — was ist jetzt abfragbar?**

```sh
openclaw memory search "Passwort" --max-results 10
openclaw memory search "Token" --max-results 10
```

**Das ist der Punkt aus der Warnung in Aufgabe 2.** Kommen hier echte Zugangsdaten aus alten Gesprächen zurück, gibt es drei Wege:
1. Zugangsdaten rotieren (steht ohnehin als Odoo #815 offen) — die sauberste Lösung
2. `sources` auf `["memory"]` zurücksetzen und auf den Sitzungsverlauf verzichten
3. Bewusst annehmen, weil der Index CT150 nicht verlässt und der Zugang ohnehin auf den Tailnet beschränkt ist

**Entscheidung gehört Wolf, nicht dem Agenten.**

- [ ] **Schritt 4: Ergebnis in Odoo festhalten**

Neue Aufgabe in Projekt 35, Stage „✅ Erledigt", mit: Zahl der indexierten Abschnitte vorher/nachher, Ergebnis der drei Prüffragen aus Aufgabe 4, gemessene Mehrkosten, Ergebnis der Sicherheitsprüfung.

- [ ] **Schritt 5: Bewusst NICHT gemacht — und warum**

**Dreaming bleibt aus.** Es ist ein nächtlicher Modelllauf, der Gesprächsverläufe zu Erinnerungen verdichtet („light, REM, deep"). Das ist der teuerste Teil des Systems und ergibt erst Sinn, wenn Aufgabe 1–5 nachweislich tragen. Als eigener Vorgang wiedervorlegen, nicht nebenbei einschalten.

---

## Rückweg für den ganzen Plan

**[IM CONTAINER]**
```sh
cp /root/.openclaw/openclaw.json.vor-recall-20260801 /root/.openclaw/openclaw.json
```
**[IN CT150]**
```sh
docker restart openclaw
crontab -l | grep -v frawo-wissen | crontab -
```
**[IM CONTAINER]**
```sh
openclaw memory index --force
openclaw memory status --deep
```
Erwartet danach wieder: `Indexed: 15/15 files · 57 chunks`, `Sources: memory`, Active Memory `disabled`.

Der Klon unter `/opt/frawo-repo` und der Ordner `workspace/memory/frawo/` dürfen stehen bleiben — sie schaden nicht und ersparen beim zweiten Anlauf Arbeit.

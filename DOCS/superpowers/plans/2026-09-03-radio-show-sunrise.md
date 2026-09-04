# Radio-Show "Sunrise" (06–09 Mo–Fr) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die erste der 10 kuratierten Radio-Shows ("Sunrise", Mo–Fr 06–09) vom recherchierten Titel bis zur live geschalteten AzuraCast-Playlist bauen — als Vorlage für die restlichen 9 Shows.

**Architecture:** beets (CT120) bleibt Datenherr (zwei neue Flexible Attributes `vibe`/`research_source`). Recherche pro Titel läuft manuell/agentisch über echte Websuche, keine neue Automatisierung. Die fertige Auswahl wird per direktem DB-Zugriff (dasselbe, bereits in diesem Repo dokumentierte Verfahren, siehe NOW.md-Radio-Abschnitt) als AzuraCast-Playlist + Zeitplan angelegt — kein neuer Dienst, keine neue API-Anbindung.

**Tech Stack:** beets (Python, CLI) auf CT120 · MariaDB (AzuraCast-DB) auf VM210, erreichbar per `qm guest exec 210` von stock-pve · AzuraCast öffentliche Read-API (`/api/station/1/...`, kein Login nötig) zur Verifikation.

**Spec:** `DOCS/superpowers/specs/2026-09-03-radio-playlist-kuration-design.md`

## Global Constraints

- Kein Big-Bang: die 3 anderen Basis-Kanäle (2, 3, 4) bleiben während der gesamten Umsetzung unverändert. Nur der Teil von Kanal 1, der mit Sunrise überlappt, wird angepasst.
- Jede Zuordnung (Titel → Vibe) braucht eine echte, nachprüfbare Quelle in `research_source` — nichts wird geraten oder erfunden (Lehre aus einem früheren Vorfall mit fabrizierten Genre/BPM/Mood-Werten, siehe Spec).
- Nach JEDER direkten Änderung an der AzuraCast-Datenbank: `qm guest exec 210 -- docker exec azuracast azuracast_cli azuracast:radio:restart 1` ausführen — sonst merkt Liquidsoap die Änderung nicht (bekannte Falle, siehe NOW.md).
- `beets`-Kommandos laufen auf CT120 (`ssh stock-pve` → `pct exec 120 -- ...`), niemals `copy`/`move` aktivieren (siehe `~/.config/beets/config.yaml` auf CT120 — Dateien bleiben, wo sie sind).
- AzuraCast-DB-Zugriff: `ssh stock-pve` → `qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u$MYSQL_USER -p$MYSQL_PASSWORD $MYSQL_DATABASE -e "..."'`.
- `station_media.path` = beets-Pfad **ohne** das Präfix `/mnt/music/`, und nur Zeilen mit `storage_location_id = 7` zählen (Station 1 nutzt ausschließlich Speicherort 7 — bekannte Falle, siehe NOW.md).
- beets-Query-Syntax: `feld:a,b,c` ist **kein** Oder (liefert 0 Treffer) — richtig ist `"feld:a" ... , "feld:b" ...` (vollständiger Ausdruck je Alternative, durch `,` getrennt). Negation ist `^feld:wert` (Präfix `^`), **nicht** `-feld:wert` — Letzteres kollidiert mit der Options-Erkennung von `beet list` (Fehler "no such option: -v").
- Recherchierte, aber bewusst nicht passende Titel bekommen `vibe=EXCLUDED` (mit Begründung in `research_source`) statt leer zu bleiben — sonst tauchen sie in jeder neuen Recherche-Sitzung wieder als "offen" auf. Zeigt sich beim Sync in Task 4, dass eine Alternative besser passt (z. B. "eher Night" vermerkt): beim Aufbau der jeweils späteren Show zuerst dort nachschauen.
- **Bibliotheks-Altlast (gefunden + repariert 03.09.2026):** ~4.651 von 11.764 beets-Einträgen zeigten auf den nicht mehr existierenden Ordner `/mnt/music/yourparty_Libary/…` (alte Struktur vor einer Umsortierung nach `Master_Library`). Per Dateiname-Abgleich gegen den echten Bestand repariert: 926 eindeutig gefunden und korrigiert, 2.088 wirklich nicht mehr auffindbar (unangetastet gelassen), 1.637 mehrdeutig (mehrere Kandidaten, unangetastet gelassen — Details in `/tmp/beets_path_fix_ambiguous.csv` auf CT120). Bei zukünftigen Shows: taucht wieder ein toter `yourparty_Libary`-Pfad auf, zählt er zu den 2.088/1.637 Restfällen — nicht automatisch reparieren, echten Fund prüfen.
- Die 2.088 wirklich fehlenden Titel bleiben trotzdem normal recherchier- und taggbar (die beets-Zeile existiert ja, nur die Datei nicht) — sie tauchen in der Recherche wie jeder andere Titel auf. Task 4 Schritt 6 prüft vor dem Symlink-Setzen automatisch, ob die Datei real existiert, und überspringt sie sonst (mit Log-Ausgabe) statt einen kaputten Symlink anzulegen.

---

### Task 1: beets-Datenmodell erweitern (`vibe`, `research_source`)

**Files:** keine Repo-Dateien — Änderung an der beets-Bibliothek auf CT120 (`/var/lib/beets/musik.db`, Flexible Attributes brauchen kein Schema-Update, sie entstehen beim ersten `beet modify`).

**Interfaces:**
- Produces: zwei beets-Felder `vibe` (kurzes Schlagwort, z. B. `dark-driving`) und `research_source` (URL/Quelle), abrufbar über `beet list -f '$vibe'` / `$research_source` und per Query `vibe:` filterbar. Alle folgenden Tasks nutzen genau diese zwei Feldnamen.

- [ ] **Schritt 1: Prüfen, dass die Felder noch nicht existieren (erwarteter Leerzustand)**

Befehl:
```
ssh stock-pve "pct exec 120 -- beet list -f '\$vibe | \$research_source' 2>&1 | head -3"
```
Erwartung: Alle Zeilen sind leer (` | `) — die Felder existieren als Flexible Attributes bereits implizit (leer), das ist beets-normal und kein Fehler.

- [ ] **Schritt 2: Testweise per beets-`id` (nicht Titel) einen Tag setzen**

Die `id` des ersten Bibliothekseintrags mechanisch ermitteln und direkt weiterverwenden (kein manuelles Aussuchen nötig):
```
ssh stock-pve "pct exec 120 -- bash -c 'ID=\$(beet list -f \"\\\$id\" | head -1); beet modify -y \"vibe=test-value\" \"research_source=https://example.invalid/test\" id:\$ID; echo VERWENDETE_ID=\$ID'"
```
Die ausgegebene `VERWENDETE_ID` für Schritt 3+4 übernehmen.

- [ ] **Schritt 3: Verifizieren, dass der Test-Tag geschrieben wurde**

```
ssh stock-pve "pct exec 120 -- beet list -f '\$title | \$vibe | \$research_source' id:<VERWENDETE_ID>"
```
Erwartung: Zeile zeigt `test-value` und die Test-URL.

- [ ] **Schritt 4: Test-Tag wieder entfernen (Feld bleibt als Konzept bestehen, nur der Testwert verschwindet)**

```
ssh stock-pve "pct exec 120 -- beet modify -y 'vibe=' 'research_source=' id:<VERWENDETE_ID>"
```

- [ ] **Schritt 5: Kein Commit nötig** — beets-Datenbank ist keine Repo-Datei. Stattdessen: Ergebnis in Odoo-Task #1261 als Kommentar festhalten ("Felder `vibe`/`research_source` funktionieren, Beispiel verifiziert").

---

### Task 2: Sunrise-Recherchepool definieren

**Files:** keine — Ergebnis ist eine beets-Query plus eine Zählung, dokumentiert im Odoo-Task, nicht im Repo.

**Interfaces:**
- Consumes: `vibe`/`research_source`-Felder aus Task 1.
- Produces: eine feste beets-Query `SUNRISE_POOL_QUERY`, die den Grundpool für Sunrise abgrenzt. Task 3 nutzt exakt diese Query, um zu sehen, was noch offen ist.

Sunrise soll laut Spec ruhig starten: Ambient/Deep House, niedriges Tempo. Erste Fassung (03.09.2026) nutzte nur 3 Genre-Zweige (480 Titel) — auf Nachfrage ("warum nur 480?") am 04.09.2026 erweitert: bei ~45% echter Trefferquote unter den recherchierten Titeln reicht ein 480er-Pool kaum für die Zielgröße 150–300, und drei weitere, thematisch passende Genres waren ungenutzt liegen geblieben. Finale Query, 6 Genre-Zweige, BPM-Obergrenze weiterhin 122:

```
SUNRISE_POOL_QUERY (je Zweig eigene bpm-Bedingung, siehe Stolperfalle oben):
"genre:Deep House" bpm:1..122 , "genre:Electronica" bpm:1..122 , "genre:Ambient" bpm:1..122 ,
"genre:Nu Disco" bpm:1..122 , "genre:Melodic House" bpm:1..122 , "genre:Organic House" bpm:1..122
```

- [ ] **Schritt 1: Poolgröße prüfen**

```
ssh stock-pve "pct exec 120 -- beet list 'genre:Deep House' bpm:1..122 , 'genre:Electronica' bpm:1..122 , 'genre:Ambient' bpm:1..122 , 'genre:Nu Disco' bpm:1..122 , 'genre:Melodic House' bpm:1..122 , 'genre:Organic House' bpm:1..122 2>&1 | wc -l"
```
Erwartung (Stand 04.09.2026, verifiziert): 900 Titel, keine Überschneidung zwischen den 6 Zweigen (jeder Titel trägt in dieser Bibliothek nur eines der sechs Genres). Reicht das bei künftigen Shows nicht: weitere thematisch passende Zweige aus der Genre-Verteilung ergänzen (`beet list -f '$genre' | sort | uniq -c | sort -rn`, siehe Odoo #1261 für die volle Liste) statt die BPM-Grenze zu senken — mehr Genre-Vielfalt schlägt engeres Tempo-Fenster.

- [ ] **Schritt 2: Ergebnis dokumentieren**

Finale Query + Titelzahl als Kommentar in Odoo-Task #1261 posten (`mcp__odoo__post_message`, `record_id=1261`), Format: "Sunrise-Pool: `<Query>`, `<N>` Titel gefunden."

---

### Task 3: Recherche-Runbook Sunrise (erste 10 Titel als Vorlage)

**Files:** keine Repo-Dateien.

**Interfaces:**
- Consumes: `SUNRISE_POOL_QUERY` aus Task 2.
- Produces: für jeden bearbeiteten Titel ein gesetztes `vibe`+`research_source`-Paar (Task 1's Felder). Fortschritt ist jederzeit ablesbar über die Query in Schritt 1 — **kein separates Tracking-Artefakt nötig**, das leere/gefüllte `vibe`-Feld selbst ist der Fortschrittsstatus.

- [ ] **Schritt 1: Nächste unbearbeiteten Titel aus dem Pool holen**

```
ssh stock-pve "pct exec 120 -- beet list -f '\$id | \$artist | \$title' 'genre:Deep House' bpm:1..122 'vibe::^\$' , 'genre:Electronica' bpm:1..122 'vibe::^\$' , 'genre:Ambient' bpm:1..122 'vibe::^\$' , 'genre:Nu Disco' bpm:1..122 'vibe::^\$' , 'genre:Melodic House' bpm:1..122 'vibe::^\$' , 'genre:Organic House' bpm:1..122 'vibe::^\$' 2>&1 | head -10"
```
(Zwei Stolperfallen der beets-Query-Syntax, live gefunden: (1) `feld:wert` ist ein einfacher **Substring**-Vergleich, für echte Regex-Prüfung — z. B. "Feld ist leer" — braucht es den **doppelten** Doppelpunkt: `vibe::^$` für leer, `vibe::.` für nicht-leer. Mit einfachem Doppelpunkt (`vibe:^$`) sucht beets nach dem wörtlichen Substring `^$` und findet nichts. (2) Bei `,`-verknüpften Oder-Zweigen gilt ein zusätzlicher Filter nur für den Zweig, an den er direkt angehängt ist — er muss in **jedem** Zweig wiederholt werden, sonst liefern die anderen Zweige ungefiltert alles zurück.)

- [ ] **Schritt 2: Pro Titel — echte Suche**

Für jeden der 10 Titel: Websuche nach `"<Interpret>" "<Titel>"` (z. B. auf Discogs, Beatport, 1001Tracklists, Resident Advisor gezielt schauen). Gesucht wird: bestätigtes Genre/Stil, ein kurzes Vibe-Schlagwort (freie, aber knappe Wortwahl — z. B. `sunny-chill`, `hypnotic-deep`, `warm-analog`), und die Quelle (URL). Findet sich **nichts Verlässliches**: Titel überspringen, nicht raten — bleibt für später/zweite Recherche-Runde offen (Feld bleibt leer, taucht in Schritt 1 der nächsten Sitzung wieder auf).

- [ ] **Schritt 3: Ergebnis schreiben**

Pro Titel:
```
ssh stock-pve "pct exec 120 -- beet modify -y 'vibe=<schlagwort>' 'research_source=<url>' id:<id>"
```

- [ ] **Schritt 4: Stichprobe verifizieren**

```
ssh stock-pve "pct exec 120 -- beet list -f '\$title | \$vibe | \$research_source' 'genre:Deep House' bpm:1..122 'vibe::.' , 'genre:Electronica' bpm:1..122 'vibe::.' , 'genre:Ambient' bpm:1..122 'vibe::.' , 'genre:Nu Disco' bpm:1..122 'vibe::.' , 'genre:Melodic House' bpm:1..122 'vibe::.' , 'genre:Organic House' bpm:1..122 'vibe::.' 2>&1 | tail -10"
```
Erwartung: die eben bearbeiteten Titel erscheinen mit Vibe + Quelle.

- [ ] **Schritt 5: Wiederholen bis Zielgröße erreicht**

Ziel laut Spec: 150–300 recherchierte Titel für Sunrise. Schritte 1–4 wiederholen (neue Sitzung darf jederzeit an Schritt 1 neu ansetzen — Fortschritt ist in beets selbst gespeichert). Kein Commit/Push nötig (keine Repo-Datei).

---

### Task 4: AzuraCast — Sunrise-Playlist + Zeitplan anlegen

**Files:** keine Repo-Dateien — Änderungen an der AzuraCast-MariaDB (VM210).

**Interfaces:**
- Consumes: recherchierte Titel aus Task 3 (`vibe::.` innerhalb der Sunrise-Pool-Query, siehe beets-Query-Stolperfallen oben).
- Produces: neue Zeile in `station_playlists` (Name "Sunrise"), zugehörige `station_schedules`-Zeile (06:00–09:00, Mo–Fr), befüllt über einen neuen `station_playlist_folders`-Eintrag (`Curated_Playlists/Sunrise/`, Symlinks auf recherchierte Titel — derselbe Mechanismus wie bei den 4 Basis-Kanälen). Kanal 1 ("Channel 1 — Acoustik & Ambient") wird für Mo–Fr auf 09:00–11:00 verkleinert, behält am Wochenende sein volles 06:00–11:00-Fenster (neue eigene Schedule-Zeile).

**Wichtig — vorher geprüft (nicht raten):** `station_playlists.type='default'`, `source='songs'`, `playback_order='shuffle'`, `weight=3`, `avoid_duplicates=1`, `include_in_requests=1` sind die produktiven Standardwerte (aus dem AzuraCast-Quellcode `backend/src/Entity/StationPlaylist.php` verifiziert, nicht geraten). `station_schedules.start_time`/`end_time` sind `HHMM` als Ganzzahl (z. B. `600` = 06:00, `900` = 09:00), `days` ist eine kommagetrennte Liste `1`(Montag)–`7`(Sonntag), `NULL` = jeden Tag (Quelle: `backend/src/Entity/StationSchedule.php`, live durch die bestehenden 4 Kanäle in `station_schedules` bestätigt).

- [ ] **Schritt 1: Aktuellen Zustand von Kanal 1 sichern**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"SELECT * FROM station_schedules WHERE playlist_id=846;\"' "
```
Erwartetes Ergebnis (Ist-Zustand vor der Änderung, Stand 03.09.2026): eine Zeile, `start_time=600, end_time=1100, days=NULL`. Ergebnis 1:1 mitschreiben (Rückweg für Schritt 6, falls etwas schiefgeht).

- [ ] **Schritt 2: Kanal 1 für Mo–Fr auf 09:00–11:00 verkleinern, Wochenende separat auf voller Länge behalten**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"
UPDATE station_schedules SET start_time=900, days=\\\"1,2,3,4,5\\\" WHERE playlist_id=846;
INSERT INTO station_schedules (playlist_id, start_time, end_time, days, loop_once) VALUES (846, 600, 1100, \\\"6,7\\\", 0);
\"' "
```

- [ ] **Schritt 3: Verifizieren**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"SELECT * FROM station_schedules WHERE playlist_id=846;\"' "
```
Erwartung: zwei Zeilen — `900|1100|1,2,3,4,5` und `600|1100|6,7`.

- [ ] **Schritt 4: Sunrise-Playlist anlegen**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"
INSERT INTO station_playlists
  (station_id, name, description, type, source, playback_order, weight,
   is_enabled, play_per_songs, play_per_minutes, play_per_hour_minute,
   include_in_requests, include_in_on_demand, is_jingle, remote_timeout,
   avoid_duplicates, backend_options)
VALUES
  (1, \\\"Sunrise\\\", \\\"Kuratierte Show, Mo-Fr 06-09\\\", \\\"default\\\", \\\"songs\\\", \\\"shuffle\\\", 3,
   1, 0, 0, 0,
   1, 0, 0, 0,
   1, \\\"\\\");
SELECT LAST_INSERT_ID();
\"' "
```
Die zurückgegebene ID notieren (im Folgenden `<SUNRISE_ID>`).

- [ ] **Schritt 5: Zeitplan für Sunrise anlegen**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"
INSERT INTO station_schedules (playlist_id, start_time, end_time, days, loop_once)
VALUES (<SUNRISE_ID>, 600, 900, \\\"1,2,3,4,5\\\", 0);
\"' "
```

- [ ] **Schritt 6: Recherchierte Titel per Ordner zuordnen (bewährter Mechanismus, wie bei den 4 Basis-Kanälen)**

**Korrektur (03.09.2026, während der Umsetzung gefunden):** AzuraCast füllt die 4 bestehenden Kanäle nicht per manueller `station_playlist_media`-Zuordnung, sondern über `station_playlist_folders` — jeder Kanal hat einen eigenen Ordner unter `/mnt/music/Curated_Playlists/<Name>/` voller **Symlinks** (nicht Kopien) auf die echten Dateien in `Master_Library`; AzuraCast scannt den Ordner und ordnet die enthaltenen Titel automatisch der verknüpften Playlist zu. Sunrise nutzt denselben, bereits produktiv bewährten Weg statt einer manuellen SQL-Zuordnung.

Ordner anlegen und Symlinks setzen (ein Aufruf pro Titel, `ln -s` verändert keine Originaldatei):
```
ssh stock-pve "pct exec 120 -- mkdir -p /mnt/music/Curated_Playlists/Sunrise"
ssh stock-pve "pct exec 120 -- beet list -f '\$path' 'genre:Deep House' bpm:1..122 'vibe::.' '^vibe:EXCLUDED' , 'genre:Electronica' bpm:1..122 'vibe::.' '^vibe:EXCLUDED' , 'genre:Ambient' bpm:1..122 'vibe::.' '^vibe:EXCLUDED' , 'genre:Nu Disco' bpm:1..122 'vibe::.' '^vibe:EXCLUDED' , 'genre:Melodic House' bpm:1..122 'vibe::.' '^vibe:EXCLUDED' , 'genre:Organic House' bpm:1..122 'vibe::.' '^vibe:EXCLUDED' 2>&1" > /tmp/sunrise_paths.txt
```
Danach je Zeile aus `/tmp/sunrise_paths.txt` (voller Original-Pfad) einen Symlink mit demselben Basisnamen im neuen Ordner anlegen:
```
ssh stock-pve 'skipped=0; while IFS= read -r p; do b=$(basename "$p"); if pct exec 120 -- test -f "$p"; then pct exec 120 -- ln -sf "$p" "/mnt/music/Curated_Playlists/Sunrise/$b"; else skipped=$((skipped+1)); echo "FEHLT: $p"; fi; done < /tmp/sunrise_paths.txt; echo "uebersprungen (Datei fehlt trotz Vibe-Tag): $skipped"'
```

- [ ] **Schritt 7: Ordner in AzuraCast als `station_playlist_folders`-Zeile eintragen**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"
INSERT INTO station_playlist_folders (station_id, playlist_id, path)
VALUES (1, <SUNRISE_ID>, \\\"Curated_Playlists/Sunrise\\\");
\"' "
```

- [ ] **Schritt 8: Medien-Scan anstoßen und verifizieren**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast azuracast_cli azuracast:media:reprocess 1"
ssh stock-pve "qm guest exec 210 -- docker exec azuracast sh -c 'mariadb -u\$MYSQL_USER -p\$MYSQL_PASSWORD \$MYSQL_DATABASE -e \"SELECT COUNT(*) FROM station_playlist_media WHERE playlist_id=<SUNRISE_ID>;\"' "
```
Erwartung: Zahl entspricht (± wenige) der Anzahl Symlinks im Sunrise-Ordner. Fehlt sie: Ordnerrechte prüfen (muss für den AzuraCast-Container lesbar sein, wie bei den 4 bestehenden Kanälen).

- [ ] **Schritt 9: AzuraCast neu laden**

```
ssh stock-pve "qm guest exec 210 -- docker exec azuracast azuracast_cli azuracast:radio:restart 1"
```

---

### Task 5: End-to-End-Verifikation

**Files:** keine.

**Interfaces:**
- Consumes: alles aus Task 4.
- Produces: bestätigter Live-Zustand, dokumentiert in Odoo #1261.

- [ ] **Schritt 1: Zeitplan öffentlich prüfen (kein Login nötig)**

```
curl -s "https://funk.frawo.tech/api/station/1/schedule" | python3 -m json.tool | grep -A3 "Sunrise"
```
Erwartung: ein Eintrag "Sunrise" mit dem richtigen Zeitfenster taucht auf.

- [ ] **Schritt 2: Laufenden Betrieb während des Sunrise-Fensters prüfen**

Frühestens am nächsten Werktag zwischen 06:00 und 09:00:
```
curl -s "https://funk.frawo.tech/api/nowplaying/1" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['now_playing']['playlist'])"
```
Erwartung: `Sunrise`. Zeigt es stattdessen weiter "Channel 1" oder eine Fehlermeldung: Schritt 8 aus Task 4 (Neustart) wiederholen, danach Zeitplan-Zeilen (Task 4, Schritt 3+Schritt 5) gegenprüfen.

- [ ] **Schritt 3: Odoo aktualisieren**

Ergebnis (Poolgröße, Titelzahl in AzuraCast, Verifikationsstatus) als Kommentar an Odoo-Task #1261 posten. Bei erfolgreicher Verifikation (Schritt 2 bestätigt "Sunrise"): Unter-Task für Show 2 (Morning Drive) anlegen, gleiche Vorlage.

- [ ] **Schritt 4: NOW.md-Korrektur**

Bei der Recherche in Task 4 aufgefallen: NOW.md behauptet noch "Kein Zeitplan mehr aktiv (`GET /api/station/1/schedule` liefert eine leere Liste)" — das stimmt nicht mehr, die 4 Kanäle haben bereits reale `station_schedules`-Einträge (06–11/11–17/17–22/22–06, geprüft 03.09.2026). NOW.md-Radio-Abschnitt entsprechend korrigieren und den neuen Sunrise-Stand ergänzen, committen, pushen (`git add NOW.md && git commit -m "docs(now): Radio-Sendeplan korrigieren + Sunrise live" && git push`).

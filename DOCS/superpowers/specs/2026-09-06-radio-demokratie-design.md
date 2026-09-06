# Radio-Demokratie: Hörer-Votes steuern FraWo Funk wirklich

**Datum:** 2026-09-06
**Status:** Design freigegeben (Wolf, 06.09.2026)
**Odoo-Bezug:** #1295 (Vorarbeit: Live-Stimmen-Anzeige), Folge-Task noch anzulegen
**Vorgänger-Design:** `2026-08-17-rekordbox-azuracast-sync-design.md` (Richtung Rekordbox → AzuraCast). Dieses Dokument beschreibt die dort ausdrücklich ausgeklammerte **Rückrichtung** und löst dessen zurückgestellten Punkt 4.3 (Bewertungen) auf.

> **Sicherheitshinweis:** Repo ist öffentlich. Keine Zugangsdaten in dieses Dokument oder in Code. AzuraCast-Key liegt in der nicht eingecheckten `.env` (`deployments/musikverwaltung/rekordbox_sync/.env`) bzw. in Vaultwarden.

## 1. Ausgangslage (live geprüft 06.09.2026)

Auf `frawo.tech/radio` gibt es drei Mood-Buttons (⚡ Energie, ❤️ Banger, 🌙 Chilliger). Sie rufen `POST /radio/vote` auf (natives Odoo-JSON-RPC, `controllers/main.py::RadioController.radio_vote`).

**Was davon heute wirklich wirkt:** ausschließlich `vote_type = 'hate'` — das ruft die AzuraCast-Skip-API und überspringt den laufenden Titel. `energy`, `chill`, `like`, `unlike` werden nur protokolliert: bisher als Textzeile in `frawo.agent.log`, seit 06.09.2026 zusätzlich strukturiert in `frawo.radio.vote` (Feld `vote_type`, Selection).

**Das Problem:** Die Oberfläche verspricht mehr, als der Code einlöst — „Wirksam ab Track +1", „In Rotation priorisiert", „speichert 5 Sterne in Rekordbox". Nichts davon passiert. Wolf hat das beim Gegenlesen selbst erkannt und die Richtung vorgegeben: **nicht die Versprechen zurücknehmen, sondern die Wirkung bauen.**

**Vorhandene Bausteine, auf denen dieses Design aufsetzt:**

| Baustein | Zustand |
|---|---|
| `frawo.radio.vote` (Odoo-Model + Backend-Ansicht „🎧 Radio-Stimmen") | seit 06.09.2026 live |
| `GET /radio/votes/summary` (Aggregat der letzten N Minuten) | seit 06.09.2026 live |
| AzuraCast-REST-API-Zugang (Key in `.env`, Station 1) | funktioniert, im `rekordbox_sync` produktiv genutzt |
| `pyrekordbox`-Schreibzugriff auf Rekordbox' Datenbank | funktioniert (`seed_rekordbox_from_azuracast.py`) |
| Pfad-Übersetzung AzuraCast ↔ Rekordbox (`M:\` + Pfad) | bestätigt, dokumentiert in `rekordbox_sync/README.md` |
| `live.is_live`-Flag im Now-Playing-Payload | wird auf der Seite schon fürs „LIVE DJ"-Badge genutzt |

## 2. Ziel

1. Energy-/Chill-Votes verschieben **wirklich** die Musikrichtung des Streams — kollektiv über ein Zeitfenster, nicht „wer zuerst klickt".
2. Während einer Live-Show (echter DJ am Mikro) wird **nicht** algorithmisch gesteuert; dort gibt es nur Reaktionen.
3. Angemeldete Hörer:innen bewerten Titel mit **1–5 Sternen**; der **Durchschnitt** ist die gültige Bewertung.
4. Diese Durchschnitts-Bewertung landet **automatisch im Hintergrund** in Rekordbox — im nativen Sterne-Feld, plus als Playlist zum schnellen Auffinden.

## 3. Baustein 1 — Rotation vs. Show

**Erkennung:** `data.live.is_live` aus dem Now-Playing-Payload, den die Seite ohnehin jede Sekunde abruft.

- `is_live = false` (Rotation): Mood-Buttons **und** Sterne-Bewertung sichtbar.
- `is_live = true` (Show): **beides** wird durch reine Reaktions-Emojis ersetzt (nutzt die vorhandene `spawnReaction()`-Animation). Kein Backend-Aufruf, keine Gewichtsänderung, kein Rekordbox-Eintrag.

**Begründung:** Bei einer Live-Show entscheidet ein Mensch, was läuft. Eine algorithmische Kanal-Verschiebung wäre dort wirkungslos (liquidsoap spielt die Rotation gar nicht) und würde die Erwartung erneut enttäuschen. Auch die Sterne-Bewertung ist dort ausgeblendet, weil im Live-Betrieb keine verlässliche Titel-Kennung vorliegt (Künstler/Titel kommen dann nicht aus der Mediathek, sondern bestenfalls aus dem, was die DJ-Software an den Stream meldet) — eine Bewertung ließe sich keinem echten Titel in der Bibliothek zuordnen.

## 4. Baustein 2 — Kanal-Gewichtung durch Energy/Chill

**Auslöser:** neuer `ir.cron` im Addon `frawo_agent`, alle 5 Minuten (Muster wie der bestehende „Live-Stand Tages-Snapshot"-Cron).

**Ablauf je Lauf:**

1. Schalter prüfen: `ir.config_parameter` `frawo_agent.radio_democracy_enabled`. Nicht gesetzt oder `false` → sofort beenden (fail-closed, gleiches Muster wie `kiosk_token`).
2. Votes der letzten **15 Minuten** aus `frawo.radio.vote` zählen, getrennt nach `energy` und `chill`. `hate`/`like`/`unlike` bleiben unberücksichtigt.
3. Keine Votes im Fenster → alle vier Kanäle auf Basisgewicht **3** zurücksetzen (Stand laut `NOW.md`: alle vier gleich gewichtet).
4. Sonst Stimmungswert bilden und in eine Gewichtsverschiebung übersetzen:
   - Energy-Übergewicht → `Channel 3 — Harder Styles` und `Channel 4 — Roadtrip & Classics` höher, `Channel 1 — Acoustik & Ambient` und `Channel 2 — Soft Groove` niedriger.
   - Chill-Übergewicht → umgekehrt.
   - Jedes Gewicht hart begrenzt auf **1 bis 6**. Kein Kanal verschwindet je vollständig, keiner dominiert vollständig.
   - Die Verschiebung ist schrittweise (max. ±1 pro Lauf), damit sich die Richtung über Minuten dreht und nicht ruckartig springt.
5. Schreiben über die **AzuraCast-REST-API** (`PUT /api/station/1/playlist/{id}`), **nicht** per MariaDB-Direktzugriff.
6. Ergebnis gegenprüfen: Gewichte nach dem Schreiben erneut lesen und mit dem Sollwert vergleichen. Abweichung → Fehler protokollieren.
7. Jede Änderung als Eintrag in `frawo.agent.log` (alt → neu je Kanal, Vote-Zählstand, Zeitstempel).

**Warum API statt Datenbank:** `NOW.md` dokumentiert die Falle „nach direkten Datenbank-Änderungen an AzuraCast immer `azuracast:radio:restart`". Über die offizielle API entfällt das — AzuraCast benachrichtigt liquidsoap selbst. Ein stündlicher Sender-Neustart wäre für Hörer:innen hörbar und ist damit ausgeschlossen.

## 5. Baustein 3 — Sterne-Bewertung durch angemeldete Hörer:innen

Ersetzt den bisherigen groben „Banger"-Umschalter (`like`/`unlike`) als Bewertungsmechanismus. **Der ❤️-Banger-Knopf verschwindet damit aus der Mood-Box** und macht Platz für die Sterne-Leiste; die Mood-Box behält ⚡ Energie und 🌙 Chilliger. Bereits gespeicherte `like`/`unlike`-Einträge in `frawo.radio.vote` bleiben unangetastet (historische Daten, werden nicht mehr fortgeschrieben und fließen in nichts mehr ein).

**Neues Model `frawo.radio.rating`:**

| Feld | Typ | Bemerkung |
|---|---|---|
| `track_id` | Char, indiziert | `"Künstler|Titel"`, exakt das Format, das die Seite schon als `song_id` sendet |
| `partner_id` | Many2one `res.partner`, indiziert | Identität der bewertenden Person |
| `stars` | Selection 1–5 | ganze Sterne, keine Halben |

**SQL-Constraint `unique(track_id, partner_id)`** — eine Person, eine Bewertung pro Titel. Erneutes Bewerten überschreibt die eigene alte Bewertung (Upsert), es entstehen keine Mehrfachstimmen.

**Endpunkte:**

- `POST /radio/rate` — `type='json'`, **`auth='user'`** (bestehendes Odoo-Kundenkonto / Portal-Login nötig, gleiches Auth-Muster wie die vorhandenen `/radio/admin/*`-Routen). Parameter: `song_id`, `stars`. Legt an oder aktualisiert die eigene Bewertung.
- `GET /radio/rating/summary?track_id=…` — `auth='public'`, liefert `{average, count, own}` (`own` nur befüllt, wenn angemeldet). Die Anzeige ist bewusst für **alle** sichtbar, nur das Abgeben der Bewertung erfordert Anmeldung.

**Frontend (View 3353):**

- Sterne-Leiste am aktuell laufenden Titel: zeigt den Durchschnitt („★★★★☆ 4,2 · 12 Bewertungen").
- Angemeldet: Sterne sind klickbar, die eigene Bewertung ist hervorgehoben.
- Nicht angemeldet: nur Anzeige plus dezenter Hinweis mit Link zum Portal-Login.
- Aktualisierung bei Track-Wechsel — dafür wird die vorhandene, aktuell **leere** Stub-Funktion `loadVotes()` (Zeile ~1255, wird bei jedem Track-Wechsel und beim Laden aufgerufen) endlich mit Inhalt gefüllt, statt eine neue Mechanik danebenzustellen.

**JavaScript-Regel für diese View:** kein literales `<`, `>` oder `&` im neuen Code (Umschreiben statt Escapen). Grund: dokumentierte QWeb-Escape-Falle in `arch_db`, die diese View bereits zweimal zerlegt hat (21.08. und 05.09.2026).

## 6. Baustein 4 — Automatischer Rekordbox-Export

**Wo:** StudioPC (dort liegt Rekordbox' Datenbank), Skript unter `deployments/musikverwaltung/rekordbox_sync/`, neben dem bestehenden Sync.

**Auslöser:** Windows-Aufgabenplanung, stündlich — dasselbe Muster, das der bestehende Rekordbox-Sync schon nutzt. **Kein manuelles Starten nötig.**

**Ablauf je Lauf:**

1. Laufen `rekordbox.exe` oder `rekordboxAgent.exe`? → Lauf überspringen, protokollieren, nächster Versuch in einer Stunde. (Schreiben bei geöffnetem Rekordbox ist unsicher, siehe Vorgänger-Design Abschnitt 6.)
2. Aktuelle Durchschnitts-Bewertungen aus Odoo holen: alle Titel mit **mindestens 2 Bewertungen**, Durchschnitt auf ganze Sterne gerundet.
3. Je Titel `"Künstler|Titel"` → echte Datei auflösen. Weg: AzuraCast-Mediensuche + `GET /api/station/1/file/{media_id}` (liefert `path`), dann Pfadregel aus `rekordbox_sync/README.md`: `rekordbox_pfad = "M:\" + azuracast_pfad.replace("/", "\\")`.
4. Über `pyrekordbox` das native Feld `DjmdContent.Rating` auf den gerundeten Durchschnitt setzen. Zur Klarstellung gegenüber dem Vorgänger-Design: **reine Leseanalysen** laufen immer gegen eine Kopie der Datenbank; der **Schreibvorgang** geht zwangsläufig gegen die echte Datenbank — abgesichert allein dadurch, dass Rekordbox dabei geschlossen ist (Schritt 1). Genau so arbeitet auch das bestehende `seed_rekordbox_from_azuracast.py`.
5. Playlist **„🔥 Publikums-Favoriten"** pflegen: alle Titel mit Durchschnitt ≥ 4 Sternen. Vorhandene Playlist wird aktualisiert, nicht dupliziert.
6. Nicht auflösbare Titel (Tippfehler, abweichende Remix-Benennung) werden **übersprungen und protokolliert** — nie geraten, nie falsch verknüpft.
7. Abschlussprüfung: geschriebene Anzahl gegen erwartete Anzahl vergleichen und protokollieren.

**Bestätigte Faktenlage (06.09.2026, gegen die echte Bibliothek geprüft):** `DjmdContent.Rating` ist eine schlichte Ganzzahl 0–5 (nicht die 0–255-Kodierung des XML-Exports). Verteilung aktuell: 11.507 Titel mit 0, 932 mit 5, 58 mit 4, 24 mit 3, 9 mit 2, 1 mit 1, 18 ohne Wert.

## 7. Datenfluss

```
Hörer:in auf frawo.tech/radio
   │
   ├─ Rotation? ──ja──► ⚡/🌙 Mood-Vote (anonym)  ─► frawo.radio.vote
   │                    ★ Sterne (nur angemeldet) ─► frawo.radio.rating
   │
   └─ Show?     ──ja──► nur Reaktions-Emoji (kein Backend)

frawo.radio.vote  ──► Odoo-Cron (5 Min) ──► AzuraCast-API: Playlist-Gewichte 1–6
                                                    │
                                                    ▼
                                         liquidsoap spielt anders gewichtet

frawo.radio.rating ──► Odoo (Durchschnitt) ──► Windows-Task (stündlich, StudioPC)
                                                    │  nur wenn Rekordbox zu
                                                    ▼
                                    pyrekordbox: Rating-Feld + „🔥 Publikums-Favoriten"
```

## 8. Fehlerbehandlung & Sicherheit

- **Notausschalter:** `frawo_agent.radio_democracy_enabled` stoppt die Kanal-Automatik sofort, ohne Code-Änderung. Fail-closed: fehlender Parameter = aus.
- **Harte Grenzen:** Kanalgewichte nie unter 1, nie über 6, maximal ±1 Schritt pro Lauf. Ein Fehler in der Berechnung kann den Sender damit nicht stumm schalten oder auf einen Kanal zusammenschrumpfen.
- **Kein Sender-Neustart** im Normalbetrieb (API statt Datenbank).
- **Rekordbox nie bei geöffneter Anwendung schreiben** — Prozessprüfung vor jedem Lauf.
- **Am Ergebnis prüfen, nicht am Vorgang:** beide Crons lesen nach dem Schreiben zurück und protokollieren Abweichungen. (Lehre aus dem zwei Wochen unbemerkten Backup-Ausfall.)
- **Keine Secrets im Repo.**
- **Bewertungen sind personenbezogen** (`partner_id`): Zugriff auf `frawo.radio.rating` im Backend nur lesend für interne Benutzer, kein öffentlicher Endpunkt liefert einzelne Personen — `GET /radio/rating/summary` gibt ausschließlich Durchschnitt, Anzahl und die *eigene* Bewertung zurück.

## 9. Verifikation (Definition of Done)

1. Mehrere Chill-Votes innerhalb von 15 Minuten verschieben die Gewichte der vier Kanäle nachweislich in Richtung Acoustik/Soft Groove (vorher/nachher über die AzuraCast-API belegt), ohne Sender-Neustart.
2. Ohne weitere Votes stehen die Gewichte spätestens 15 Minuten später wieder bei 3/3/3/3.
3. Schalter auf `false` → nächster Cron-Lauf ändert nachweislich nichts.
4. Während `is_live = true` zeigt die Seite Reaktionen statt Steuerungs-Buttons; kein `/radio/vote`-Aufruf geht raus.
5. Angemeldete Person vergibt 4 Sterne → Anzeige zeigt den neuen Durchschnitt inkl. erhöhter Bewertungsanzahl. Dieselbe Person bewertet erneut mit 2 → Anzahl bleibt gleich, Durchschnitt sinkt (kein Doppelzählen).
6. Nicht angemeldet: Sterne sichtbar, aber nicht klickbar; `POST /radio/rate` ohne Anmeldung wird abgewiesen.
7. Ein Titel mit zwei Bewertungen (Ø 4,5 → 5 gerundet) trägt nach dem nächsten Task-Lauf in Rekordbox 5 Sterne und steht in „🔥 Publikums-Favoriten".
8. Läuft Rekordbox, wird der Lauf übersprungen und protokolliert — die Datenbank bleibt unangetastet.

## 10. Ausdrücklich NICHT in diesem Design

- **Kein automatischer Sendeplan/Timetable** — wann welche Show läuft, entscheidet weiterhin Wolf in AzuraCast.
- **Keine Rückrichtung Rekordbox-Sterne → Odoo** (Wolfs eigene Bewertungen bleiben seine; nur der Publikums-Durchschnitt wird geschrieben).
- **Kein Skip-Umbau** — `hate` bleibt wie es ist.
- **Keine Halbe-Sterne-Bewertung** — Rekordbox' Feld kann es nicht.
- **Keine Anzeige einzelner Bewertender** auf der öffentlichen Seite.

## 11. Offene Punkte für den Umsetzungsplan

- Genaue Formel Stimmungswert → Gewichtsschritt (Startwert: Differenz `energy - chill`, ab ±2 Stimmen ein Schritt).
- Genauer Weg der AzuraCast-Mediensuche für `"Künstler|Titel"` → `media_id` (die Sammelabfrage `/api/station/1/files` liefert laut `rekordbox_sync/README.md` HTTP 500; Workaround-Kette ist dort dokumentiert).
- Ob die Sterne-Leiste zusätzlich in die bestehende Mood-Box wandert oder als eigener Bereich am Deck sitzt (Layout-Frage, beim Bauen zu entscheiden).

# Radio-Redaktion beim Hören (v1) — Design

**Status:** Entwurf zur Freigabe durch Wolf. Noch nichts gebaut.
**Odoo:** #1090 · **Baut auf:** `2026-09-30-frawo-funk-musikredaktion-design.md` (Abschnitt 7)

## 1. Zweck (Wolfs Worte)

Erster Entwurf (Hörproben-Seite mit 50 Titeln) von Wolf verworfen, 30.09.2026:
> „Das ist doch Spielzeug … ich will ja, wenn dann, Radio hören … und nicht noch extra irgendwie.“

Also: **keine eigene App, keine Extra-Liste.** Wolf hört FraWo Funk wie immer;
wenn er angemeldet ist, kann er den **gerade laufenden Titel** mit einem Tipp
beurteilen. Genau das hatte er am 29.09. als Nutzungsart gewählt („beim Hören,
nebenbei“).

## 2. Was es kann (v1)

Unter dem Player auf `frawo.tech/radio` erscheinen — **nur für angemeldete
Redaktions-Nutzer**, für alle anderen unverändert — große Knöpfe zum laufenden Titel:

| Knopf | Wirkung auf den Titel |
|---|---|
| **Energie 1 · 2 · 3 · 4 · 5** | `energie`, `quelle_energie = "Wolf <Datum>"` |
| **passt hierher** / **passt nicht** | bestätigt bzw. nimmt den Titel aus der laufenden Sendung (Sendung = Filter, siehe Redaktions-Spec §5) |
| **★ 1–5** | `sterne` (steuert später die Rotation) |
| bei Prüf-Titeln zusätzlich: die gefundenen Genre-Vorschläge als Knöpfe + „keins davon“ | `genre`/`style`, `redaktion=belegt`, Quelle „Wolf <Datum>“ |

Alles optional — wer nichts tippt, hört einfach Radio. Ein Tipp gilt für genau
den Titel, der zum Zeitpunkt des Tipps lief (Titel wird beim Tippen mitgesendet,
nicht neu abgefragt → kein Verrutschen beim Titelwechsel).

## 3. Wie die Redaktion trotzdem vorankommt

- **Prüf-Titel ins Programm mischen:** Titel mit `redaktion=widerspruch|unklar`
  und Titel ohne Energie-Urteil werden in eine eigene AzuraCast-Playlist
  „Redaktion – zum Anhören“ gelegt, die **innerhalb der passenden Sendung** mit
  kleinem Gewicht mitläuft (z. B. jeder 8.–10. Titel). Welche Sendung „passend“
  ist, ergibt sich aus Tempo/Stil der Vorschläge. So hört Wolf sie nebenbei.
- **Eichung der Energie entsteht beim Hören:** Sobald ~50 Energie-Urteile über
  alle Stufen vorliegen, werden die Mess-Schwellen gesetzt; danach füllt die
  Messung den Rest der Bibliothek.
- Kennzeichnung auf der Seite: bei Prüf-Titeln ein kleines „🔍 Redaktion fragt“.

## 4. Aufbau

| Teil | Wo | Aufgabe |
|---|---|---|
| Knöpfe unter dem Player | Odoo-Modul `frawo_agent`, bestehende Radio-Seite (View der Website) | nur bei angemeldetem Nutzer der Gruppe „Radio-Redaktion“ sichtbar |
| Speichern | neuer JSON-Endpunkt in `frawo_agent` (Login nötig) | legt je Tipp einen Datensatz `frawo.radio.urteil` an: AzuraCast-`media_id`, Artist/Titel, Art, Wert, Zeitpunkt, Nutzer |
| Titel → Bibliothek | AzuraCast-`media.path` → beets-Pfad (`/mnt/music/` + Pfad) → beets-`id` | Zuordnung beim Rückschreiben |
| Rückschreiben | CT120, `deployments/musikredaktion/rueckschreiben.py`, nachts (Teil des Redaktions-Nachtlaufs) | Urteile per beets-Schnittstelle in die Bibliothek; „passt nicht“ → Titel aus dem Sendungsfilter |
| Prüf-Playlist | AzuraCast (bestehende API, Schlüssel in Odoo funktioniert, getestet 30.09.) | nachts neu befüllt aus beets |

Kein neuer Dienst, keine Hörproben, keine öffentliche Freigabe der Bibliothek.

## 5. Fehler und Grenzen

- Titel ohne beets-Eintrag (z. B. Jingles, Sets) → Knöpfe ausgeblendet.
- Doppelter Tipp → der letzte Wert je Titel und Art zählt.
- Nicht angemeldet → Seite genau wie heute.

## 6. Abnahme

- Wolf beurteilt eine Woche lang nebenbei beim Hören, ohne Anleitung.
- Urteile landen nachts korrekt in beets (Stichprobe 10 Titel).
- Nach ≥ 50 Energie-Urteilen: Formel trifft ≥ 80 % davon auf ±1 Stufe.

## 7. Entscheidungen Wolf (30.09.2026)

- Teil A freigegeben („ja passt“).
- Redaktions-Nutzer: **Wolf, Franz und ein neuer Odoo-Nutzer „Kiosk“** für die
  internen Bildschirme (Touchboard/Dashboards). Kiosk bekommt nur die Gruppe
  „Radio-Redaktion“ plus Leserechte, die die Dashboards brauchen — keine
  Verwaltungsrechte.
- Die Knöpfe bauen auf der vorhandenen Sterne-Bewertung auf (`frawo.radio.rating`,
  `/radio/rating/…`, nur angemeldet) — kein Parallelsystem.

---

# Teil B — Die Radio-Seite nach außen (frawo.tech/radio)

Wolf, 30.09.: „… auf den aktuellen Stand bringen und eben das Radio nach
außen auch professionell gestalten.“

## B1. Befund (30.09.2026, öffentlicher Aufruf + Quelltext `views/radio_page.xml`)

| Punkt | Befund |
|---|---|
| Sendeplan | **von Hand** in der Seite (2.629 Zeilen Datei), 7 Tagesreiter mit festen Uhrzeiten. Stimmt heute grob mit AzuraCast überein, läuft aber auseinander, sobald Sendungen Filter mit weichen Übergängen werden |
| Technik im Vordergrund | „320 kbps Master Audio“, „Liquidsoap v2 Engine“, „M3U Playlist File (VLC / iTunes)“ |
| Unklare Knöpfe | „Auf YouTube suchen“ |
| Ladezustände | „Lade nächsten Track…“, „Stimmen werden laden…“ |
| Emoji-Menge | viele Emojis in Überschriften und Knöpfen |
| Abstimmung | funktioniert und zielt korrekt auf die Sendungen 859–868 (Systemparameter geprüft) |

## B2. Was sich ändert

1. **Sendeplan kommt live vom Sender** (`/api/station/1/schedule`, über den
   vorhandenen Odoo-Proxy wie `nowplaying`) statt von Hand: „Jetzt läuft“,
   „Danach“, Wochenansicht. Stimmt dadurch immer — auch bei Übergängen.
2. **Sendungs-Steckbriefe** (Name, 1 Satz, Stilrichtung) aus **einer**
   Quelle (AzuraCast-Playlist-Beschreibung), nicht doppelt gepflegt.
3. **Texte klar und deutsch**, Fachbegriffe nur, wo sie Hörern etwas sagen
   (Musikstile bleiben englisch — das ist in der Szene üblich). Emojis sparsam
   (höchstens eines je Abschnitt).
4. **Technik in einen kleinen, zugeklappten Bereich** „In anderen Apps hören“
   (Stream-Adressen, Playlist-Datei) — ohne iTunes/Engine-Namen.
5. **„Auf YouTube suchen“ entfällt.** Wunsch-Funktion und Abstimmung bleiben.
6. **Ladezustände** zeigen sinnvolle Platzhalter („—“) statt Satzfragmente.
7. **CI v3.0**, Handy zuerst, schnelle Ladezeit; Aussehen für nicht
   angemeldete Hörer bleibt ruhig — die Redaktions-Knöpfe (Teil A) nur für
   angemeldete Redaktions-Nutzer.

## B3. Abnahme Teil B

- Sendeplan der Seite = AzuraCast-Zeitplan (Stichprobe Mo, Sa, So).
- Keine der Befund-Stellen aus B1 mehr sichtbar.
- Seite am Handy in unter 3 s nutzbar; Player, Wunsch, Abstimmung
  funktionieren wie vorher (Test vor/nach).
- Wolf sieht sie sich einmal am Handy an und gibt frei.

## 8. Offen für Wolf

1. Teil B so freigeben?

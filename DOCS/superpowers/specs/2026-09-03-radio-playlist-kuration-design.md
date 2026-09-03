# FraWo-Radio: Professionelle Playlist-Kuration — Design

Ausgelöst durch Wolfs Rückmeldung zur n8n/Odoo-Automation (#1259/#1260):
das war nicht das erwartete Niveau, wichtiger ist jetzt echte Qualität
bei Musik und Sender. Radio ist Teil der FraWo-Roadmap als eigene Marke
(siehe `project_frawo_ziel_gewerbliche_dienstleistung` in der Agent-
Memory) — Maßstab: reproduzierbar, dokumentiert, betreubar.

## Ausgangslage

AzuraCast (VM210, `funk.frawo.tech`) fährt seit dem 29.07.2026 nur noch
vier gleichgewichtete "General Rotation"-Playlisten (Channel 1–4,
Gewicht 3, kein Zeitplan) — geprüft per DB-Abfrage
(`station_playlists`: alle vier `type=default`, `weight=3`, keine
`play_per_songs`/`play_per_minutes`-Regeln). Das fühlt sich für Wolf
korrekt "komplett random" an, weil es das technisch auch ist: vier
große Töpfe (1.3k–3.4k Titel) ohne Tempo-, Stil- oder Tageszeit-Bezug.

**Wichtiger Fund (Git-Historie NOW.md, Commit `2838cf4`):** Bis zum
29.07.2026 existierte ein funktionierendes 8-Zeitfenster-Schema
(Sunrise/Morning Drive/Lunch/Afternoon/Evening/Night + Wochenend-DJ-
Shows + General-Rotation-Auffangnetz), das von einer parallelen
"yourparty"-Sitzung ohne Wolfs Wissen überschrieben wurde. Dieses
Design baut bewusst auf diesem bewährten Skelett auf, statt neu zu
erfinden.

**Bibliotheks-Stand (beets, CT120, geprüft 02.09.2026):** 11.764 Titel,
464 GB. Genre-Tags granular und brauchbar (House 948, Tech House 913,
Disco/Electronic 707, Indie Dance 596, Deep House 472, Techno-Varianten,
Afro House 216 …). Style-Feld bei ~64 % gefüllt, BPM bei ~83 %
(2.047 Titel ohne BPM). Nebenfund: 10 Titel sind Reste einer Stem-
Trennung (Bass/Drums/Vocals.wav mit Müll-Namen) — kosmetisch, wird bei
Gelegenheit bereinigt, ist aber nicht die Ursache des "Random"-Gefühls.

## Ziel dieser Spec

Aus den 4 bestehenden Kanälen ein zweistufiges Sendeschema mit 10
echt kuratierten Shows für 24/7/365 machen, bei dem die Titelauswahl
pro Show auf recherchierten (nicht geratenen) Informationen beruht.

**Bewusst NICHT Teil dieser Spec:**
- Die komplette 11.764-Titel-Bibliothek in einem Rutsch recherchieren
  (siehe Rollout unten — nur die Show-Pools zuerst).
- Der n8n-2.0-Umstieg oder die kaputte Paperless-Webhook-Registrierung
  (#1260) — separate Vorhaben.
- Automatisierte Audio-Feature-Analyse (Essentia o.ä.) — bewusst
  verworfen zugunsten echter Recherche pro Titel (Wolfs Entscheidung,
  2026-09-02: "Titel explizit suchen und kategorisieren").
- Ein neuer Automatisierungs-Dienst/Cron für die Recherche — läuft als
  von Claude begleiteter, mehrsitzungs-übergreifender Prozess, kein
  neuer Custom-Dienst auf einem Server.

## Architektur (2 Ebenen)

1. **Basis-Rotation (unverändert, bleibt Auffangnetz):** die 4
   bestehenden Kanäle (Acoustik & Ambient, Soft Groove, Harder Styles,
   Roadtrip & Classics) laufen weiter als AzuraCast "General Rotation"
   — genau die Rolle, die früher "General Rotation (Auffangnetz)"
   hatte. Füllt Sendezeit außerhalb geplanter Shows.
2. **10 kuratierte Shows, zeitlich geplant:** über AzuraCasts native
   Zeitplan-Funktion (Playlist-Typ mit Start/Ende + Wochentagen) —
   kein Custom-Cron, kein neues Werkzeug.

## Die 10 Shows (Entwurf, Zeiten nach dem bewährten alten Schema)

| # | Show | Zeit | Grund-Pool (Genre/Style-Tags) |
|---|---|---|---|
| 1 | Sunrise | Mo–Fr 06–09 | ruhiger Einstieg: Ambient/Deep House, wenig BPM |
| 2 | Morning Drive | Mo–Fr 09–12 | House, Nu Disco/Disco, Indie Dance |
| 3 | Lunch | Mo–Fr 12–14 | Soft Groove, Disco/Electronic, locker |
| 4 | Afternoon | Mo–Fr 14–18 | Deep House, Melodic House & Techno |
| 5 | Evening | Mo–Fr 18–22 | Tech House, Progressive House, Techno (Peak Time) |
| 6 | Night | täglich 22–06 | Techno (Raw/Deep/Hypnotic), Minimal/Deep Tech, Trance |
| 7 | Friday/Saturday Peak-Time-Night | Fr/Sa 22–02 | härtester, energiereichster Pool, Sonderrolle ggü. 6 |
| 8 | Sunday Roadtrip & Classics | So 10–18 | nostalgisch, ruhiger Sonntag |
| 9 | Afro House / World | wöchentlicher fester Slot (Details bei Recherche) | Afro House (216 Titel bereits getaggt, bisher ungenutzt) + verwandte Weltmusik-Stile |
| 10 | DJ-Bridge Sets | Sa/So Abend | Wolfs eigene Aufnahmen (Radio-Bridge-Upload) — sofern die alten "734h DJ-Sets" oder neue Aufnahmen vorliegen; wird bei Umsetzung geprüft |

Zeiten/Zuschnitte sind ein Entwurf und können sich beim Recherchieren
noch verschieben, wenn ein Pool zu klein/groß ausfällt.

## Track-Recherche & Vibe-Tagging

Kern der Qualitätsverbesserung. Pro Show wird **nicht die ganze
Bibliothek**, sondern ein gezielter Pool von ca. 150–300 Titeln
recherchiert (insgesamt ~1.500–3.000 Titel für alle 10 Shows).

**Ablauf pro Titel:**
1. Echte Suche nach Titel + Interpret (Discogs, Beatport, 1001
   Tracklists, Resident Advisor, DJ-Blogs — reale Quellen, kein Raten
   aus Tags allein).
2. Ergebnis: bestätigtes/verfeinertes Genre, ein kurzes Vibe-Schlagwort
   (z. B. `dark-driving`, `sunny-chill`, `hypnotic`, `nostalgic`) und
   die Quelle.
3. Schreiben in beets als neue Flexible Attributes:
   - `vibe`: das Schlagwort
   - `research_source`: URL/Quelle, damit jede Zuordnung nachprüfbar
     bleibt (Lehre aus dem früheren Vorfall mit erfundenen
     Genre/BPM/Mood-Werten durch eine frühere Session — hier bewusst
     das Gegenteil: nichts ohne Quellenbeleg).

**Tempo/Umfang:** läuft über mehrere Sitzungen (Wolfs Entscheidung
2026-09-02: "Best Practice anwenden, muss nicht schnell gehen, lieber
stabil"), kostenlose Websuche statt bezahltem Gemini-Kontingent.
Fortschritt wird pro Show verfolgt (welche Titel schon recherchiert
sind), damit eine Sitzung genau dort weitermachen kann, wo die vorige
aufgehört hat.

## AzuraCast-Umsetzung

- Für jede Show: eine neue AzuraCast-Playlist (Typ "Scheduled"),
  Zeitfenster gemäß Tabelle oben, Inhalt = die recherchierten Titel.
- Umsetzung des "recherchierten Pool → AzuraCast-Playlist"-Schritts:
  dünner Sync über die AzuraCast-API (Playlist-Mitgliedschaft setzen),
  ausgehend von einer beets-Query auf `vibe`/Genre — reine Verbindung
  zweier bestehender Werkzeuge (beets-Query + AzuraCast-API), keine
  Neuerfindung von Logik, die eines der beiden Werkzeuge schon hat.
- Basis-Rotation-Kanäle bleiben als "General Rotation" unverändert in
  ihrer Technik, laufen automatisch in den Lücken.

## Rollout-Reihenfolge

1. Show-Liste steht (diese Spec) — Zeiten/Zuschnitte können sich beim
   Recherchieren noch leicht anpassen.
2. Show für Show: Titel recherchieren + taggen, dann die jeweilige
   AzuraCast-Playlist scharf schalten.
3. Kein Big-Bang-Umbau — die 4 Basis-Kanäle laufen die ganze Zeit
   weiter, der Sender bleibt durchgehend auf Sendung. Jede fertige Show
   ersetzt schrittweise einen Teil der bisherigen Zufalls-Rotation in
   ihrem Zeitfenster.
4. Stem-Datei-Reste (10 Titel) und `Unidentified_Research`-Ordner
   (324 GB) werden bei Gelegenheit nebenbei aufgeräumt, blockieren aber
   nicht den Rollout.

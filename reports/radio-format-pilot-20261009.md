# FraWo Funk – Radio-Format-Pilot

Datum: 2026-10-09

## Ziel

Reguläre Sendungen laufen zufällig innerhalb eines klaren Mood-Pools. Eine feste Reihenfolge bleibt nur für ausdrücklich kuratierte Einzel-Sessions erhalten. Normale Wochenprogramme sollen nicht jede Woche dieselbe Dramaturgie und dieselben Titel um dieselbe Uhrzeit wiederholen.

## Recherche-Ergebnis

AzuraCast unterstützt dafür mehrere passende Bausteine:

- Playlists können sequenziell oder geshufflet abgespielt werden; „shuffled“ mischt einen Pool einmal und spielt ihn ohne Wiederholung bis zum Ende des Durchlaufs, während „random“ echte Zufallsauswahl mit möglichen Wiederholungen ist.
- Playlists können in Zeitblöcken geplant und über Prioritäten miteinander gestapelt werden.
- Listener Requests, Web-DJ, öffentliche Sendepläne und Auswertungen sind als spätere Interaktionsschichten verfügbar.
- Durch die getrennte Behandlung von Mood-Pools, Zeitfenstern und Sonder-Sessions lässt sich ein lebendigeres Programm als mit einer einzigen 10-Stunden-Playlist bauen.

Quellen:
- https://azuracast.com/docs/user-guide/playlists/
- https://azuracast.com/docs/
- https://www.azuracast.com/docs/developers/apis/

## Direkt umgesetzt

Aus der geprüften Playlist `Friday Peak` wurden drei neue, zunächst deaktivierte Pilot-Pools angelegt. Es wurden keine Audiodateien kopiert oder verändert; nur Playlist-Mitgliedschaften wurden gesetzt.

| Playlist | ID | Titel | Laufzeit | Status |
|---|---:|---:|---:|---|
| Friday Peak — House & Tech House | 902 | 33 | ca. 3,1 h | Pilot 16.10.2026, 17:00–20:00 |
| Friday Techno Drive | 903 | 21 | ca. 2,1 h | Pilot 16.10.2026, 20:00–22:00 |
| Friday Disco Drive | 904 | 35 | ca. 3,75 h | Pilot 16.10.2026, 22:00–02:00 |

Die neuen Pools sind auf `shuffle` gestellt. Die Queue wurde nach der Änderung am echten AzuraCast-Ziel gelesen und bestätigt: 33, 21 und 35 Titel. Für den Pilot am 16. Oktober 2026 sind sie in drei einmaligen Zeitblöcken eingeplant; danach kehrt `Friday Peak` ab dem 23. Oktober als Fallback zurück.

## Redaktionelle Ideen für die nächste Ausbaustufe

1. **Mood-Rotation statt Wochentagswiederholung**
   - pro Zeitfenster mehrere passende Pools
   - wöchentlicher Wechsel der Pool-Kombination
   - globale Künstler-/Titel-Sperrzeiten ergänzen, weil Shuffle allein keine Künstlerabstände garantiert

2. **Dayparting mit klaren Farben**
   - Morning Bloom / Morning Flow: warm, leicht, zugänglich
   - City Lunch / Tropical Noon: sonnig, groovig, beweglich
   - Golden Hour / Sunset Pulse: melodisch und emotional
   - Friday Peak / Techno Drive: treibend und clubbig
   - Deep Night / Night Owls: reduziert, dunkel, hypnotisch

3. **Einmalige Radio-Events**
   - Best-of-Sessions mit fester Reihenfolge
   - monatliche Themenabende
   - „Guest Selects“ oder Live-Web-DJ-Slots
   - danach nicht dauerhaft als unveränderter Wochenblock wiederholen

4. **Listener-Interaktion**
   - Song-Requests zu definierten Zeiten
   - später eine „Track der Woche“-Abstimmung
   - Request-Pools begrenzen, damit die redaktionelle Linie erhalten bleibt

5. **Mehr Sendungscharakter ohne Dauermoderation**
   - kurze Stations-IDs/Jingles zwischen Mood-Blöcken
   - saisonale Intros und lokale FraWo-Hinweise
   - keine langen, störenden Sprachblöcke

## Nächster Qualitäts-Gate

Vor dem Aktivieren der drei Pilot-Pools werden gemeinsam geprüft:

- passen die Grenzfälle wirklich in den jeweiligen Mood-Pool?
- ist `Friday Techno Drive` trotz der kurzen Länge abwechslungsreich genug?
- soll `Friday Disco Drive` eher Disco/Funk bleiben oder auch Synthpop/Indie-Dance aufnehmen?
- welche bestehenden Freitag-Slots werden durch die neuen Pools ersetzt?

Erst danach wird ein zeitlich begrenzter Freitag-Pilot live geschaltet und mit Now-Playing, Stream, öffentlichem Sendeplan und Queue-Readback abgenommen.

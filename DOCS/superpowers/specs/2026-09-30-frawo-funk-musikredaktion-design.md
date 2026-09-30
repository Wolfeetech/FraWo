# FraWo Funk 2.0 — Die Musikredaktion (Design)

**Status:** Entwurf zur Freigabe durch Wolf. Noch nichts gebaut.
**Odoo:** #1090 (Radio nutzbar bis 31.10.), #1263 (Bibliothek), #1261 (Shows)
**Baut auf:** `2026-09-03-radio-playlist-kuration-design.md` (10 Shows),
`2026-09-05-musikserver-sanierung-design.md` (Bibliothek)

---

## 1. Was Wolf will (seine Worte, 30.09.2026)

> „Eine eigene Musikredaktion. Wie soll ich denn 10k Tracks sortieren …
> Ich würde mir wünschen, dass das Track für Track im Hintergrund
> recherchiert wird … kein Geraten.“
>
> „Die Kuration enger gezogen, das Programm noch besser kuratiert, die
> Musik in der Library besser sortiert — sodass ich auch als DJ leichteres
> Spiel habe, Playlisten und Shows zu erstellen.“

**Erfolg heißt:**
1. Jeder Titel hat wenige, **belegte** Merkmale (Quelle steht dabei).
2. Die 10 Sendungen entstehen **aus diesen Merkmalen**, nicht aus Handarbeit —
   ein neuer Titel landet von selbst in der richtigen Sendung.
3. Wolf holt sich dieselben Merkmale als DJ-Playlists (Rekordbox).
4. Wolf muss nur noch dort ran, wo keine Quelle etwas Verlässliches sagt.

**Ausgangslage (gemessen 29./30.09.):** 10.669 Titel nach Sanierung. Genre bei
10.152 gesetzt, aber oft Sammelsurium (bis zu 3 Angaben je Titel in der
Datenbank, in Dateien/Ordnern teils ganze Beatport-Genrelisten). Stil bei
6.733, Tempo bei 8.671, Tonart bei 5.628, MusicBrainz-ID bei 4.937.
Das bisherige `vibe`-Wort ist bei 10.615 Titeln gesetzt, aber nur bei 24 mit
echter Quelle — der Rest wurde pauschal nach Genre-Tag vergeben.

**Lehre aus der Vergangenheit:** `professional_music_researcher.py` wurde
stillgelegt, weil es Genre/BPM/Stimmung **erfunden** hat. Die Redaktion darf
darum nie ein Sprachmodell „einschätzen“ lassen. Jeder Wert kommt aus einer
nachprüfbaren Quelle oder einer Messung — sonst bleibt das Feld leer.

---

## 2. Die Merkmale je Titel

| Feld (beets) | Inhalt | Herkunft | Pflicht-Beleg |
|---|---|---|---|
| `genre` | **eines** der 16 (17) Hauptgenres | aus `style` abgeleitet (feste Tabelle) | `quelle_genre` |
| `style` | 1–2 feine Stile, z. B. „Deep House“ | Discogs → MusicBrainz → Last.fm | `quelle_genre` |
| `bpm` | Tempo | vorhanden / Messung | — |
| `initial_key` | Tonart, als Camelot (8A) angezeigt | vorhanden / Messung | — |
| `energie` | 1–5 | **Audio-Messung** | `quelle_energie` = „Messung <Datum>“ |
| `tageszeit` | morgen · tag · abend · nacht · peak | **Regel** aus energie + bpm + style (Tabelle, Abschnitt 4) | — |
| `sterne` | 0–5 | **nur Wolf** (Portal-Seite / Rekordbox) | — |
| `rotation` | power · current · gold · archiv | aus Sternen + Alter + Sendehäufigkeit | — |
| `redaktion` | offen · belegt · widerspruch · unklar | Stand der Recherche | — |

`vibe` bleibt als Altfeld lesbar, wird aber nicht mehr zur Steuerung benutzt.

**Genre-Regel gegen das Sammelsurium:** Ein Titel hat genau **ein** Genre
(die Ordner-Ebene) und höchstens **zwei** Stile. Alles Weitere aus alten Tags
wandert unverändert in `genre_raw` (nichts geht verloren, nichts wird
angezeigt).

---

## 3. Die Redaktion: wie ein Titel recherchiert wird

Ein Hintergrund-Dienst arbeitet die Titel mit `redaktion=offen` ab, **Titel
für Titel**, in dieser Reihenfolge:

**Schritt A — Katalog-Recherche (Genre/Stil).** Quellen nach Verlässlichkeit
für elektronische Musik:

| Rang | Quelle | Was sie liefert | Zugang |
|---|---|---|---|
| 1 | **Discogs** | Genre + Style je Veröffentlichung, von Menschen gepflegt — Standard in der DJ-Welt | kostenloser persönlicher Schlüssel; beets-Modul `discogs` ist eingebaut |
| 2 | **MusicBrainz** | Genres/Tags je Aufnahme, IDs | frei; `mbsync` läuft schon |
| 3 | **Last.fm** | Hörer-Tags (schwach) | vorhanden (`lastgenre`), nur gegen die Genre-Whitelist |

Entscheidungsregel:
- Discogs findet die Veröffentlichung eindeutig (Interpret + Titel + Länge
  ±3 s bzw. vorhandene IDs) → Style von Discogs, `redaktion=belegt`.
- Sonst MusicBrainz, sonst Last.fm mit **mindestens zwei** übereinstimmenden
  Tags aus der Whitelist.
- Quellen widersprechen sich im Hauptgenre → `redaktion=widerspruch`, Wolf
  entscheidet beim Hören.
- Keine Quelle → `redaktion=unklar`, Feld bleibt leer. **Nie raten.**
- `quelle_genre` = die URL des Treffers (Discogs-Release, MusicBrainz-Recording).

**Schritt B — Audio-Messung (Energie, fehlendes Tempo/Tonart).**
Energie ist keine Katalog-Angabe — sie wird **gemessen**, wie Rekordbox/
Mixed In Key es tun: Lautheit, Dichte der Anschläge, Tanzbarkeit. Werkzeug:
**Essentia** (Open Source, Musik-Forschung Uni Barcelona; `essentia_streaming_extractor_music`).
Ergebnis auf 1–5 abgebildet über feste Schwellen, die an 50 von Wolf
gehörten Titeln geeicht werden (Abschnitt 7).

Die Messung liest jede Datei einmal ganz → **seriell, nachts**, auf dem
OptiPlex (mehr Rechenleistung als CT120 mit 4 Kernen/2 GB), über die
Samba-Freigabe nur lesend. Schätzung: 5–10 s je Titel → 10.669 Titel in
etwa 3–4 Nächten.

**Tempo aus Meta vs. Messung:** vorhandenes `bpm` bleibt; wo es fehlt oder
Messung und Tag um mehr als 3 % auseinanderliegen (Halb-/Doppeltempo),
kommt der Titel auf die Prüfliste statt überschrieben zu werden.

**Takt:** ein systemd-Timer, nachts, in Portionen (Katalog: 400 Titel/Nacht
wegen Discogs-Ratenbegrenzung 60/min; Messung: so viele, wie bis 06:00
passen). Mit `StartLimitBurst`, `OnFailure=` und Metrik
`frawo_redaktion_offen` im Monitoring. ⚠️ Neuer Dauerdienst → **vorher mit
Jarvis abstimmen** (Hausordnung).

---

## 4. Tageszeit-Regel (transparent, änderbar)

| tageszeit | energie | bpm | typische Stile |
|---|---|---|---|
| morgen | 1–2 | < 118 | Ambient, Downtempo, Organic, Jazz, Soul |
| tag | 2–3 | 110–124 | Nu Disco, Indie Dance, Deep House, Funk |
| abend | 3–4 | 120–126 | House, Melodic, Tech House |
| nacht | 3–4 | 122–132 | Minimal, Deep Techno, Progressive |
| peak | 5 | ≥ 124 | Techno, Peak-Time, Bass |

Stil schlägt Tempo, wenn beide widersprechen (ein 128er Ambient-Stück ist
kein Peak). Die Tabelle liegt als Datei im Repo; Wolf kann sie ändern, danach
wird neu berechnet.

---

## 5. Sendungen werden Filter

Jede der 10 Sendungen wird eine **gespeicherte Abfrage** statt eines
handgepflegten Ordners, z. B.:

```
01 Sunrise        tageszeit:morgen  energie:1..2  sterne:0..5  ^rotation:archiv
07 Peak Time Club tageszeit:peak    energie:5
09 Afro World     genre:"Afro & World"
```

Ein nächtlicher Schritt baut daraus die Sendungsordner
(`Curated_Playlists/<Show>`, Symlinks wie heute) — AzuraCast merkt nichts vom
Umbau. **Weichere Übergänge:** jede Sendung bekommt zusätzlich eine
„Übergangs“-Abfrage (Nachbar-Tageszeit), die in der ersten und letzten
halben Stunde mit geringerem Gewicht mitläuft. **Rotation:** `power`-Titel
laufen öfter (AzuraCast-Gewicht), `archiv` nie.

---

## 6. DJ-Seite

- **Rekordbox-Playlists aus denselben Abfragen**, automatisch in die
  vorhandene Freigabe `[playlisten]` (`_playlisten`), Werkzeug
  `playliste-exportieren.sh` existiert schon. Beispiele: „Warm-up 118–124,
  Energie 3“, „Peak 128+, Energie 5“, je Tonart gruppiert.
- **Ordner:** 16 (17) Genre-Ordner statt 427, saubere Dateinamen
  (Phase 4 der Sanierung, `beet move`), Feinsicht als Verweis-Ordner
  `_nach_Style`, `_nach_Energie`, `_nach_Tonart`.
- **Sterne zurück:** Sterne, die Wolf in Rekordbox vergibt, werden
  übernommen (Plan `2026-09-06-radio-sterne-rekordbox-plan.md`).

## 7. Wolfs Anteil — so klein wie möglich

1. **Einmalig ~50 Titel eichen:** Portal-Seite spielt je 30 s an, Wolf tippt
   Energie 1–5. Damit werden die Mess-Schwellen eingestellt.
2. **Laufend beim Hören** (Portal-Seite, handytauglich): Sterne, „passt
   nicht in diese Sendung“, und die Titel mit `widerspruch`/`unklar` —
   die Seite legt ihm genau diese vor.
3. **Discogs-Schlüssel anlegen** (kostenloses Konto, 2 Minuten) → Vaultwarden.

---

## 8. Reihenfolge

| # | Schritt | Wolf nötig? |
|---|---|---|
| 1 | Discogs-Schlüssel, Probelauf Katalog-Recherche an 200 Titeln, Trefferquote messen | Schlüssel |
| 2 | Essentia auf dem OptiPlex, Probemessung 200 Titel | nein |
| 3 | Eichung 50 Titel (Portal-Seite, einfachste Fassung) | ✅ ~15 min |
| 4 | Redaktion nachts für alle Titel (3–4 Nächte), mit Jarvis abgestimmt | nein |
| 5 | Genre-Vereinheitlichung + `beet move` (Sanierung Phase 4) | Freigabe Wartungsfenster |
| 6 | Sendungen als Filter + Übergänge, AzuraCast neu einlesen | Abnahme per Ohr |
| 7 | Rekordbox-Export + Portal-Seite „beim Hören“ | Abnahme |

**Abnahme:** ≥ 80 % der Titel `redaktion=belegt`, 0 Titel mit mehr als
einem Genre, jede Sendung ≥ 150 Titel, Stichprobe von 30 Titeln durch Wolf
ohne grobe Fehlzuordnung.

## 9. Ausdrücklich nicht

- Kein Sprachmodell, das Genres oder Stimmungen „einschätzt“.
- Keine Löschung von Musik. Keine Umbenennung außerhalb von `beet move`.
- `Quarantine/Unidentified_Research` (Wolfs Vinyl-Mitschnitte) bleibt unangetastet.

## 10. Offene Entscheidungen für Wolf

1. Ist die Merkmals-Liste (Abschnitt 2) die richtige? *(Empfehlung: ja)*
2. `Afro & World` als 17. Genre-Ordner? *(Empfehlung: ja — Show 9)*
3. Discogs-Konto anlegen (kostenlos)?

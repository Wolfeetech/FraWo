#!/usr/bin/env python3
"""
FraWo — Genres vereinheitlichen (zweistufig, nach Discogs-Modell)
Angelegt 29.07.2026. Läuft in CT120.

===========================================================================
DAS PROBLEM
===========================================================================
In der Bibliothek stehen 600 verschiedene Genre-Angaben für 9.264 Titel.
Für einen Kurator ist das unbrauchbar — und es hat einen konkreten
Nebeneffekt, den Wolf benannt hat:

  "ein artist hat seine tracks verteilt über mehrere genres und ein album
   wird deshalb aufgesplittet, weil es verschiedene subgenres hat"

Genau das passiert: Auf einem Album steht Titel 1 als "Deep House", Titel 2
als "Minimal / Deep Tech", Titel 3 als "Techno (Raw / Deep / Hypnotic)".
Beim Browsen nach Genre zerfällt das Album in drei Teile.

===========================================================================
DIE LÖSUNG: ZWEI EBENEN
===========================================================================
So arbeiten Discogs und jeder professionelle Plattenladen:

  GENRE  breit, kanonisch, EINE pro Album   -> Album bleibt zusammen
  STYLE  spezifisch, pro Titel              -> Feinheit geht nicht verloren

Beispiel:
  vorher   Titel 1: "Deep House"
           Titel 2: "Minimal / Deep Tech"
           Titel 3: "Techno (Raw / Deep / Hypnotic)"

  nachher  Genre: "Techno"   (fuer alle drei — die Mehrheit auf dem Album)
           Style: "Deep House" / "Minimal" / "Raw Techno"  (je Titel)

Beim Klicken durch Genres siehst du also das komplette Album. Willst du es
feiner, filterst du zusätzlich nach Style.

===========================================================================
WIE DIE ALBUM-ENTSCHEIDUNG FÄLLT
===========================================================================
Je Album wird gezählt, welches kanonische Genre am häufigsten vorkommt —
gewichtet nach Spieldauer, damit ein 12-Minuten-Stück mehr zählt als ein
2-Minuten-Zwischenspiel. Bei Gleichstand entscheidet die Reihenfolge in
GENRE_RANG: spezifischere Genres vor allgemeineren, damit ein Album nicht
im Sammelbecken "Electronic" landet, wenn die Hälfte klar Techno ist.

Einzelne Titel ohne Album (Singles, lose Dateien) bekommen ihr eigenes
kanonisches Genre — dort gibt es nichts zusammenzuhalten.

AUFRUF
    ./genres-vereinheitlichen.py                 zeigt nur an
    ./genres-vereinheitlichen.py --anwenden      schreibt in die Datenbank
    ./genres-vereinheitlichen.py --anwenden --in-dateien
"""

import argparse
import re
import subprocess
import sys
from collections import Counter, defaultdict

# --------------------------------------------------------------------------
# Zuordnung: Suchmuster -> kanonisches Genre
# Reihenfolge zählt. Das erste passende Muster gewinnt, deshalb stehen
# spezifische Fälle oben.
# --------------------------------------------------------------------------
REGELN = [
    (r'dj[- ]?set|live set|essential mix|radio show|podcast',   'DJ-Sets'),

    (r'tech house',                                              'House'),
    (r'deep house|jackin|bass house|afro house|organic house',   'House'),
    (r'progressive house|disco house|acid house|melodic house',  'House'),
    (r'\bhouse\b',                                               'House'),

    (r'hard ?techno|peak time|driving',                          'Techno'),
    (r'raw|hypnotic|dub techno|detroit',                         'Techno'),
    (r'minimal|deep tech',                                       'Techno'),
    (r'\btechno\b',                                              'Techno'),

    (r'psy|goa',                                                 'Trance'),
    (r'\btrance\b',                                              'Trance'),

    (r'italo',                                                   'Disco'),
    (r'nu disco|\bdisco\b',                                      'Disco'),

    (r'drum ?(&|and) ?bass|dnb|jungle',                          'Bass'),
    (r'breakbeat|breaks|dubstep|garage|bassline',                'Bass'),

    (r'funk|soul|boogie|r&b|rnb',                                'Funk & Soul'),

    (r'indie dance|synth ?pop|new wave|post.?punk|electropop',   'Indie & Wave'),

    (r'trip ?hop|hip ?hop|rap',                                  'Hip Hop'),
    (r'reggae|dancehall|dub\b',                                  'Reggae'),
    (r'\bjazz\b',                                                'Jazz'),
    (r'rock|alternative|metal|punk',                             'Rock'),
    (r'\bpop\b',                                                 'Pop'),
    (r'soundtrack|score|classical|klassik',                      'Soundtrack'),

    (r'ambient|downtempo|chill',                                 'Ambient'),
    (r'idm|electronica|industrial|\bebm\b|electro',              'Electronic'),
    # Nachgetragen nach dem ersten Lauf: Diese Angaben blieben ungemappt
    # stehen. "Mainstage" ist eine Beatport-Kategorie fuer grosse Buehnen,
    # "Électronique"/"Elektronisch" sind schlicht andere Sprachen.
    (r'mainstage|main stage',                                    'Electronic'),
    (r'électronique|electronique|elektronisch',                  'Electronic'),
    (r'dance|electronic',                                        'Electronic'),
]

# Bei Gleichstand auf einem Album: spezifisch schlägt allgemein.
GENRE_RANG = [
    'DJ-Sets', 'Techno', 'House', 'Trance', 'Bass', 'Disco', 'Funk & Soul',
    'Indie & Wave', 'Hip Hop', 'Reggae', 'Jazz', 'Rock', 'Pop', 'Soundtrack',
    'Ambient', 'Electronic',
]

# Werbung und Herkunftsseiten sind kein Genre.
MUELL = re.compile(r'(www\.|\.com|\.club|\.net|\.ru|sharing-db|torrent)', re.I)


def kanonisch(roh):
    """Kanonisches Genre für eine rohe Genre-Angabe, oder None.

    NACHGEBESSERT nach dem ersten Lauf: Damals blieben rund 145 Titel mit
    ihrem alten Müll-Genre stehen — "Sharing-DB.club", "Mainstage",
    "Électronique" und die riesigen Beatport-Kataloge. Der Fehler lag nicht
    beim Erkennen, sondern in der Folge: Erkannter Müll führte zu None, und
    None hiess "nichts ändern" statt "ersetzen".
    """
    if not roh:
        return None

    # ===== WICHTIG: Das Ergebnis muss sich auf sich selbst abbilden =====
    # Sonst zerstört ein zweiter Lauf die Arbeit des ersten. Genau das wäre
    # hier passiert: "Indie & Wave" und "Bass" sind zwar Ergebnisse dieser
    # Funktion, trafen aber auf keine der Regeln unten ("new wave" ja,
    # "Indie & Wave" nein) — 444 Titel hätten beim nächsten Lauf ihr Genre
    # verloren. Aufgefallen beim Vergleich zweier Probeläufe.
    for g in GENRE_RANG:
        if roh.strip().lower() == g.lower():
            return g

    if MUELL.search(roh):
        # Müll ist kein Genre. None heisst hier: bitte über das Album
        # bestimmen — nicht: alten Wert behalten.
        return None

    # Die riesigen Beatport-Kataloge listen SÄMTLICHE Genres in einem Feld
    # (über 200 Zeichen). Als Ganzes wertlos — aber der ERSTE Eintrag ist
    # in aller Regel der eigentliche, deshalb wird der ausgewertet.
    if len(roh) > 60:
        erster = re.split(r'[,;]', roh)[0].strip()
        if erster and len(erster) <= 60:
            roh = erster
        else:
            return None

    r = roh.lower()
    for muster, ziel in REGELN:
        if re.search(muster, r):
            return ziel
    return None


def stil(roh):
    """Der spezifische Stil, aufgeräumt — behält die Feinheit."""
    if not roh or MUELL.search(roh) or len(roh) > 60:
        return None
    s = re.sub(r'\s*[;/]\s*', ' / ', roh.strip())
    s = re.sub(r'\s{2,}', ' ', s)
    return s.title() if s.islower() else s


def lade():
    """Liest id, album-Kennung, genre und Länge aus beets."""
    aus = subprocess.run(
        ['beet', 'ls', '-f', '${id}\x1f${album}\x1f${albumartist}\x1f${genre}\x1f${length}'],
        capture_output=True, text=True, timeout=900
    )
    for zeile in aus.stdout.splitlines():
        t = zeile.split('\x1f')
        if len(t) == 5:
            yield t


def dauer_sek(s):
    """'6:16' -> 376"""
    try:
        teile = [float(x) for x in s.split(':')]
    except ValueError:
        return 0
    if len(teile) == 3:
        return teile[0] * 3600 + teile[1] * 60 + teile[2]
    if len(teile) == 2:
        return teile[0] * 60 + teile[1]
    return teile[0] if teile else 0


def main():
    p = argparse.ArgumentParser(description='Genres zweistufig vereinheitlichen')
    p.add_argument('--anwenden', action='store_true')
    p.add_argument('--in-dateien', action='store_true')
    args = p.parse_args()

    if args.in_dateien and not args.anwenden:
        print('--in-dateien ergibt nur zusammen mit --anwenden Sinn.')
        return 1

    titel = list(lade())
    print(f'{len(titel)} Titel gelesen.\n')

    # Schritt 1: je Album die Genres zählen, gewichtet nach Spieldauer
    alben = defaultdict(Counter)
    for kennung, album, albumkuenstler, genre, laenge in titel:
        if not album:
            continue
        schluessel = f'{albumkuenstler}\x1f{album}'
        k = kanonisch(genre)
        if k:
            alben[schluessel][k] += dauer_sek(laenge)

    album_genre = {}
    gesplittet = 0
    for schluessel, zaehler in alben.items():
        if not zaehler:
            continue
        if len(zaehler) > 1:
            gesplittet += 1
        hoechst = max(zaehler.values())
        kandidaten = [g for g, v in zaehler.items() if v == hoechst]
        kandidaten.sort(key=lambda g: GENRE_RANG.index(g) if g in GENRE_RANG else 99)
        album_genre[schluessel] = kandidaten[0]

    print(f'{len(alben)} Alben mit Genre-Angaben.')
    print(f'{gesplittet} davon waren ueber mehrere Genres verteilt '
          f'— genau die, die beim Browsen auseinanderfielen.\n')

    # Schritt 2: Zuweisung je Titel bestimmen
    aenderungen = []
    verteilung = Counter()
    for kennung, album, albumkuenstler, genre, laenge in titel:
        schluessel = f'{albumkuenstler}\x1f{album}'
        neu_genre = album_genre.get(schluessel) or kanonisch(genre)
        neu_stil = stil(genre)

        if not neu_genre:
            # Kein Genre bestimmbar. Steht dort aber noch Müll
            # ("Sharing-DB.club", ein 200-Zeichen-Katalog), muss er weg —
            # ein LEERES Feld ist ehrlich, ein falsches nicht.
            # Beim ersten Lauf blieben so rund 145 Titel mit Müll stehen.
            if genre and (MUELL.search(genre) or len(genre) > 60):
                aenderungen.append((kennung, '', None))
                verteilung['(geleert)'] += 1
            continue

        verteilung[neu_genre] += 1
        if neu_genre != genre or neu_stil:
            aenderungen.append((kennung, neu_genre, neu_stil))

    print('=== Verteilung nach der Vereinheitlichung ===')
    for g, n in verteilung.most_common():
        print(f'  {g:14s} {n:6d}')
    print(f'\n{len(aenderungen)} Titel bekaemen neue Angaben.')

    if not args.anwenden:
        print('\nNichts geaendert. Mit --anwenden ausfuehren.')
        return 0

    schreib = '--write' if args.in_dateien else '--nowrite'
    print(f'\nSchreibe ({schreib}) ...')
    fehler = 0
    for i, (kennung, g, s) in enumerate(aenderungen, 1):
        felder = [f'genre={g}']
        if s:
            felder.append(f'style={s}')
        r = subprocess.run(
            ['beet', 'modify', '--yes', schreib, f'id:{kennung}'] + felder,
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            fehler += 1
        if i % 500 == 0:
            print(f'  {i} / {len(aenderungen)}')
    print(f'Fertig. {len(aenderungen) - fehler} geaendert, {fehler} fehlgeschlagen.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

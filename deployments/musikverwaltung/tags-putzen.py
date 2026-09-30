#!/usr/bin/env python3
"""
FraWo — Tags putzen (Fassung 2)
Angelegt 29.07.2026, Fassung 2 am 29.09.2026 (Odoo #1263). Läuft in CT120.

WOZU
====
Wolf, 29.09.2026: "keine Links in den Kommentaren oder sonst — das muss
100 % clean und radiotauglich sein, ALLES".

Messung 29.09.2026 (beets-Datenbank, 11.819 Einträge): 4.538 Titel tragen
Werbe-/Link-Müll, vor allem in comments (3.663), label (1.599),
grouping (1.401), encoder (763), composer, lyrics/lyricist (Telegram-Links).
Häufigste Quellen: iptorrents, torrentday, minimalfreaks.co, fordjonly,
musicdjs.club, djsoundtop, electronicfresh, djpoolrecords, muzhousebeat.

Fassung 1 putzte nur title/album/genre. Fassung 2 putzt JEDES Textfeld und
zusätzlich die Datei-Tags, die beets gar nicht kennt (URL-Frames wie WXXX,
Kommentare, TXXX, Vorbis-Felder).

WAS PASSIERT
============
1. Datenbank: Freitextfelder (comments, grouping, encoder, lyrics, lyricist)
   werden ganz geleert, wenn Müll drin ist. Alle anderen Felder (title,
   artist, album, label, composer, …) verlieren nur den Müll-Teil; bleibt
   nichts übrig, wird das Feld geleert.
2. Datei: jeder Tag-Eintrag mit Müll wird entfernt, danach schreibt beets
   die geputzten Werte zurück (item.write()).

WAS NIE ANGEFASST WIRD
======================
- Cover (APIC/covr/Bilder), DJ-Daten (GEOB, PRIV — Serato/Rekordbox),
  ReplayGain, MusicBrainz-IDs.
- Echte Namen: "International Deejay Gigolo Records" bleibt. Gesucht wird
  nach Web-Adressen und festen Werbe-Phrasen, nicht nach einzelnen Wörtern.
- research_source (interne Quellenangabe der Kuratierung) und lyrics_url.
- Dateinamen/Ordner — die kommen mit dem Umzug (beet move, Phase 4).

AUFRUF
======
    tags-putzen.py                 Probelauf: zeigt nur an, ändert nichts
    tags-putzen.py --anwenden      Datenbank sichern, Datenbank + Dateien putzen

Die geänderten Dateien werden in der nächsten Nacht neu auf den Anker
gesichert (rsync nach Größe/Zeit). Danach AzuraCast neu einlesen lassen.
"""

import argparse
import os
import re
import sqlite3
import sys
from collections import Counter

import beets.library
import mutagen

DB = '/var/lib/beets/musik.db'

MUELL = re.compile(
    r'https?://\S*'
    r'|(?:www\.)?t\.me/\S*'
    r'|www\.\S+'
    r'|\b[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(?:com|net|club|ru|org|info|biz|to|cc|de|eu|me|io|fm|pl|xyz|top|site|online|co|us|in|uk)\b\S*'
    r'|\bmyfreemp3\w*|\bmp3juices?\w*|\bzippyshare\w*|\biptorrents?\w*|\btorrentday\w*'
    r'|\bpromo only\b|\bfree download\b|\bfull version free\b',
    re.IGNORECASE)

# Felder, die bei Müll komplett geleert werden (reiner Freitext, kein Wert für den Sender)
GANZ_LEEREN = {'comments', 'grouping', 'encoder', 'encoder_info', 'encoder_settings',
               'lyrics', 'lyricist', 'lyricists', 'media', 'catalognum', 'isrc'}
NIE = {'path', 'research_source', 'lyrics_url', 'vibe', 'mb_trackid', 'mb_albumid',
       'mb_artistid', 'mb_albumartistid', 'mb_releasegroupid', 'mb_releasetrackid',
       'acoustid_id', 'acoustid_fingerprint', 'format'}
# Datei-Frames, die nie angefasst werden (Bilder, DJ-Daten, Binärdaten)
NIE_FRAME = re.compile(r'^(APIC|PIC|GEOB|PRIV|UFID|RVA2|MCDI|covr|METADATA_BLOCK_PICTURE|'
                       r'metadata_block_picture|coverart|replaygain_.*|REPLAYGAIN_.*)', re.I)


def putze(feld, wert):
    """Geputzter Wert, oder None wenn nichts zu tun ist."""
    # Mehrwertfelder (beets 2: composers, lyricists, artists, …) Element für Element
    if isinstance(wert, (list, tuple)):
        if not any(isinstance(x, str) and MUELL.search(x) for x in wert):
            return None
        neu = [putze(feld, x) if isinstance(x, str) and MUELL.search(x) else x for x in wert]
        return [x for x in neu if x]
    if not isinstance(wert, str) or not wert or not MUELL.search(wert):
        return None
    if feld in GANZ_LEEREN:
        return ''
    t = MUELL.sub('', wert)
    t = re.sub(r'\[\s*\]|\(\s*\)', '', t)
    t = re.sub(r'\s*[-_|/,:]+\s*$', '', t)
    t = re.sub(r'^\s*[-_|/,:]+\s*', '', t)
    t = re.sub(r'\s{2,}', ' ', t).strip(' -_.|/,:\t')
    return t


def frame_text(wert):
    try:
        if hasattr(wert, 'text'):
            return ' '.join(str(x) for x in wert.text)
        if hasattr(wert, 'url'):
            return str(wert.url)
        if isinstance(wert, (list, tuple)):
            return ' '.join(str(x) for x in wert)
        return str(wert)
    except Exception:
        return ''


def datei_muell(pfad):
    """Liste der Tag-Schlüssel mit Müll in der Datei."""
    try:
        f = mutagen.File(pfad)
    except Exception:
        return None, []
    if f is None or f.tags is None:
        return f, []
    weg = []
    for key in list(f.tags.keys()):
        k = str(key)
        if NIE_FRAME.match(k):
            continue
        # ID3-URL-Frames (WXXX, WCOM, WOAR, …) sind immer Links
        if re.match(r'^W[A-Z0-9]{3}', k):
            weg.append(key); continue
        if MUELL.search(frame_text(f.tags[key])):
            weg.append(key)
    return f, weg


def main():
    p = argparse.ArgumentParser(description='Werbe-/Link-Müll aus der Musikbibliothek putzen')
    p.add_argument('--anwenden', action='store_true', help='Datenbank sichern, Datenbank und Dateien putzen')
    args = p.parse_args()

    if args.anwenden:
        sich = DB + '.vor-tags-putzen-20260929'
        if not os.path.exists(sich):
            s, d = sqlite3.connect('file:%s?mode=ro' % DB, uri=True), sqlite3.connect(sich)
            s.backup(d); d.close(); s.close()
        print('Sicherung', sich)

    lib = beets.library.Library(DB)
    db_felder, datei_frames = Counter(), Counter()
    beispiele = []
    titel_db = titel_datei = geschrieben = fehler = 0
    for it in lib.items():
        aend = {}
        for k in it.keys(computed=False, with_album=False):
            if k in NIE:
                continue
            neu = putze(k, it.get(k))
            if neu is not None:
                aend[k] = neu
                db_felder[k] += 1
                if k not in GANZ_LEEREN:
                    beispiele.append((k, str(it.get(k))[:70], str(neu)[:70]))
        pfad = it.path
        f, weg = datei_muell(pfad) if os.path.exists(pfad) else (None, [])
        for key in weg:
            datei_frames[re.sub(r':.*', '', str(key))] += 1
        if aend:
            titel_db += 1
        if weg:
            titel_datei += 1
        if not args.anwenden or not (aend or weg):
            continue
        try:
            for k, v in aend.items():
                it[k] = v
            it.store()
            if f is not None and weg:
                for key in weg:
                    del f.tags[key]
                f.save()
            if os.path.exists(pfad):
                it.write()
            geschrieben += 1
        except Exception as e:
            fehler += 1
            print('FEHLER', it.id, e, file=sys.stderr)

    # Zweiter Durchgang: Dateien in der Bibliothek, die beets (noch) nicht kennt — nur Datei-Tags
    bekannt = set(it.path for it in lib.items())
    fremd = fremd_muell = 0
    for wurzel, _, namen in os.walk(b'/mnt/music/Master_Library'):
        for n in namen:
            if n.startswith(b'.ntfs-3g') or not n.lower().endswith(
                    (b'.mp3', b'.flac', b'.m4a', b'.aac', b'.ogg', b'.opus', b'.wma', b'.aiff', b'.aif', b'.wav')):
                continue
            pfad = os.path.join(wurzel, n)
            if pfad in bekannt:
                continue
            fremd += 1
            f, weg = datei_muell(pfad)
            if not weg:
                continue
            fremd_muell += 1
            for key in weg:
                datei_frames[re.sub(r':.*', '', str(key))] += 1
            if args.anwenden:
                try:
                    for key in weg:
                        del f.tags[key]
                    f.save()
                    geschrieben += 1
                except Exception as e:
                    fehler += 1
                    print('FEHLER', pfad, e, file=sys.stderr)
    print('Dateien ohne Datenbank-Eintrag:', fremd, '| davon mit Müll:', fremd_muell)
    print('Titel mit Müll in der Datenbank:', titel_db)
    for k, n in db_felder.most_common():
        print('   %-18s %5d' % (k, n))
    print('Titel mit Müll in den Datei-Tags:', titel_datei)
    for k, n in datei_frames.most_common(25):
        print('   %-18s %5d' % (k, n))
    # Namensfelder vollständig zeigen: dort darf nie ein echter Name verloren gehen
    print('Änderungen an Namensfeldern (%d, je Wert einmal):' % len(beispiele))
    for (k, alt, neu), n in Counter(beispiele).most_common():
        print('   %4dx [%s] %r -> %r' % (n, k, alt, neu))
    if args.anwenden:
        print('GEPUTZT', geschrieben, '| Fehler', fehler)
    else:
        print('Probelauf — nichts geändert. Mit --anwenden ausführen.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

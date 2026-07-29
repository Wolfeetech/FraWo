#!/usr/bin/env python3
"""
FraWo — Tags putzen
Angelegt 29.07.2026. Läuft in CT120.

WOZU
====
Die Bibliothek trägt Werbe- und Herkunftsmüll in den Metadaten. Gemessen am
29.07.2026 über 12.157 Dateien:

    electronicfresh.com   454
    sharing-db.club        44
    djsoundtop.com         35
    a.to / whatdjplays / muzhousebeat   6
    529 Titel beginnen mit einer Tracknummer  ("49 - Space Kids")
     62 mit Werbewörtern ("free", "promo only")
     47 mit eckigen Klammern
    ein Torrent-Tracker steht als "Label"

Betroffen sind vor allem Album- und Genre-Felder, seltener Titel.

VORGEHEN
========
Standardmässig wird NUR ANGEZEIGT, was sich ändern würde. Erst mit
--anwenden wird geschrieben.

    ./tags-putzen.py                  zeigt an, ändert nichts
    ./tags-putzen.py --anwenden       schreibt in die beets-Datenbank
    ./tags-putzen.py --anwenden --in-dateien   schreibt auch in die Dateien

WARUM DIE DRITTE STUFE GETRENNT IST
===================================
Werden Tags in Dateien geschrieben, ändern sich die Dateien — und die
stündliche Sicherung lädt sie neu in die Cloud. Bei allen 12.157 Dateien
wären das 567 GB und rund 78 Stunden. Betroffen sind hier aber nur rund
1.100 Dateien, also grob 50 GB — das ist vertretbar, soll aber eine bewusste
Entscheidung sein und nicht nebenbei passieren.

WAS NICHT GEPUTZT WIRD
======================
Die Dateinamen. Dort steckt derselbe Müll ("..._-_www.djsoundtop.com.mp3"),
aber ein Umbenennen würde sämtliche AzuraCast-Playlisten ins Leere zeigen
lassen. Das gehört geplant und mit anschliessendem Neueinlesen gemacht,
nicht nebenbei.
"""

import argparse
import re
import subprocess
import sys
from collections import Counter

# Herkunftsseiten, die in Feldern auftauchen. Aus der Messung, nicht geraten.
SEITEN = [
    r'www\.electronicfresh\.com', r'electronicfresh\.com',
    r'www\.djsoundtop\.com', r'djsoundtop\.com',
    r'sharing-db\.club', r'whatdjplays\.com', r'muzhousebeat\.com',
    r'www\.iptorrents\.com', r'www\.torrentday\.co\w*',
    r'myfreemp3\w*', r'mp3juices?\w*',
    # allgemein: alles was wie eine Domain aussieht
    r'\b[a-z0-9-]+\.(?:com|net|club|ru|org|info|biz|to|cc)\b',
]

WERBUNG = [
    r'\bpromo only\b', r'\bfree download\b', r'\bexclusive\b',
    r'\bdownload\b', r'\bfull version free\b',
]


def putze(text, ist_titel=False):
    """Gibt den geputzten Text zurück, oder None wenn nichts zu tun ist."""
    if not text:
        return None
    original = text

    for muster in SEITEN:
        text = re.sub(muster, '', text, flags=re.IGNORECASE)
    for muster in WERBUNG:
        text = re.sub(muster, '', text, flags=re.IGNORECASE)

    # Eckige Klammern samt Inhalt, wenn darin nur Müll steht
    text = re.sub(r'\[\s*\]', '', text)

    if ist_titel:
        # Vorangestellte Tracknummer: "49 - Space Kids" -> "Space Kids"
        # Nur wenn danach noch etwas Sinnvolles steht.
        neu = re.sub(r'^\s*\d{1,3}\s*[-_.]\s+', '', text)
        if len(neu.strip()) >= 3:
            text = neu

    # Reste aufräumen: doppelte Trenner, Klammerreste, Randzeichen
    text = re.sub(r'\(\s*\)', '', text)
    text = re.sub(r'\s*[-_]\s*$', '', text)
    text = re.sub(r'^\s*[-_]\s*', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    text = text.strip(' -_.\t')

    if not text or text == original:
        return None
    return text


def beet_ls(feld):
    """Liest id und Feldwert aus der beets-Datenbank."""
    aus = subprocess.run(
        ['beet', 'ls', '-f', '${id}\t${' + feld + '}'],
        capture_output=True, text=True, timeout=600
    )
    for zeile in aus.stdout.splitlines():
        if '\t' in zeile:
            kennung, wert = zeile.split('\t', 1)
            yield kennung.strip(), wert.strip()


def main():
    p = argparse.ArgumentParser(description='Tags der Musikbibliothek putzen')
    p.add_argument('--anwenden', action='store_true',
                   help='Änderungen in die beets-Datenbank schreiben')
    p.add_argument('--in-dateien', action='store_true',
                   help='zusätzlich in die Musikdateien schreiben (Achtung: Cloud-Upload)')
    p.add_argument('--felder', default='title,album,genre',
                   help='welche Felder, mit Komma getrennt')
    args = p.parse_args()

    if args.in_dateien and not args.anwenden:
        print('--in-dateien ergibt nur zusammen mit --anwenden Sinn.')
        return 1

    gesamt = Counter()
    aenderungen = []

    for feld in args.felder.split(','):
        feld = feld.strip()
        for kennung, wert in beet_ls(feld):
            neu = putze(wert, ist_titel=(feld == 'title'))
            if neu is not None:
                aenderungen.append((kennung, feld, wert, neu))
                gesamt[feld] += 1

    if not aenderungen:
        print('Nichts zu putzen gefunden.')
        return 0

    print(f'{len(aenderungen)} Änderungen gefunden:\n')
    for feld, anzahl in gesamt.most_common():
        print(f'  {feld:8s} {anzahl:5d}')
    print('\nBeispiele:\n')
    for kennung, feld, alt, neu in aenderungen[:12]:
        print(f'  [{feld}]')
        print(f'    vorher:  {alt[:78]}')
        print(f'    nachher: {neu[:78]}')

    if not args.anwenden:
        print('\nNichts geändert. Mit --anwenden ausführen.')
        return 0

    schreib_flag = '--write' if args.in_dateien else '--nowrite'
    print(f'\nSchreibe ({schreib_flag}) ...')
    fehler = 0
    for kennung, feld, alt, neu in aenderungen:
        r = subprocess.run(
            ['beet', 'modify', '--yes', schreib_flag, f'id:{kennung}', f'{feld}={neu}'],
            capture_output=True, text=True, timeout=120
        )
        if r.returncode != 0:
            fehler += 1
    print(f'Fertig. {len(aenderungen) - fehler} geändert, {fehler} fehlgeschlagen.')
    if not args.in_dateien:
        print('Hinweis: Nur in der Datenbank. Beim nächsten Einlesen aus den')
        print('Dateien wäre der alte Stand wieder da — dafür --in-dateien.')
    return 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Ordnet die von radio_cover_entfernen.py geaenderten Dateien den AzuraCast-
Medien zu und entfernt deren gespeicherte Cover-Kopien (Odoo #1908).

Warum: AzuraCast behaelt beim Neueinlesen ein altes Cover, wenn die Datei
keins mehr hat (StationMediaRepository::loadFromFile schreibt Art nur, wenn
welche da ist). Die Kopie liegt je Medium als /mnt/music/.albumart/<unique_id>.jpg
auf CT120 (Samba-Freigabe [sender] = AzuraCast-Speicherort 7).

Eingaben:
  --protokoll  protokoll.tsv aus radio_cover_entfernen.py (Zeilen 'OK <pfad> <n>')
  --medien     TSV aus AzuraCast: id <TAB> unique_id <TAB> path (relativ zu /mnt/music)
Ausgabe: <sicherung>/azuracast_ids.txt (eine Medien-ID je Zeile) fuer das SQL.
Ohne --ausfuehren wird nur gezaehlt; mit --ausfuehren werden die .albumart-
Dateien nach <sicherung>/albumart/ verschoben (nicht geloescht = Rueckweg).
"""
import argparse, os, shutil, sys

WURZEL = '/mnt/music'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--protokoll', required=True)
    ap.add_argument('--medien', required=True)
    ap.add_argument('--sicherung', required=True)
    ap.add_argument('--ausfuehren', action='store_true')
    a = ap.parse_args()

    geaendert = set()
    for zeile in open(a.protokoll, encoding='utf-8'):
        teile = zeile.rstrip('\n').split('\t')
        if teile[0] == 'OK' and len(teile) >= 3 and teile[2] != '0':
            geaendert.add(os.path.realpath(teile[1]))

    treffer = []
    for zeile in open(a.medien, encoding='utf-8'):
        teile = zeile.rstrip('\n').split('\t')
        if len(teile) < 3 or not teile[0].isdigit():
            continue
        mid, uid, rel = teile[0], teile[1], teile[2]
        # Curated_Playlists sind Symlinks auf Master_Library -> realpath vergleicht beide
        if os.path.realpath(os.path.join(WURZEL, rel)) in geaendert:
            treffer.append((mid, uid, rel))

    art_da = [t for t in treffer if os.path.exists(os.path.join(WURZEL, '.albumart', t[1] + '.jpg'))]
    print('geaenderte Dateien: %d, AzuraCast-Medien dazu: %d, davon mit Cover-Kopie: %d, Modus: %s'
          % (len(geaendert), len(treffer), len(art_da), 'AUSFUEHREN' if a.ausfuehren else 'PROBE'))
    if not a.ausfuehren:
        return 0

    os.makedirs(os.path.join(a.sicherung, 'albumart'), exist_ok=True)
    with open(os.path.join(a.sicherung, 'azuracast_ids.txt'), 'w') as fh:
        for mid, uid, rel in treffer:
            fh.write(mid + '\n')
    verschoben = 0
    for mid, uid, rel in art_da:
        quelle = os.path.join(WURZEL, '.albumart', uid + '.jpg')
        shutil.move(quelle, os.path.join(a.sicherung, 'albumart', uid + '.jpg'))
        verschoben += 1
    print('Cover-Kopien verschoben: %d -> %s/albumart' % (verschoben, a.sicherung))
    return 0


if __name__ == '__main__':
    sys.exit(main())

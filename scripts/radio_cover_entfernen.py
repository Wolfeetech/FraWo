#!/usr/bin/env python3
"""Entfernt Werbe-, Haendler- und kaputte Cover aus Musikdateien (Odoo #1908).

Wolf 04.10.2026: Werbung von Download-Seiten, Beatport-Bilder und kaputte
Bilder sollen raus; Titel ohne Cover zeigt das Radio dann mit dem
FraWo-Funk-Standardbild (Einstellung in AzuraCast, nicht in den Dateien).

Warum ein eigenes Skript statt `beet clearart`: Ein Teil der betroffenen
Dateien steht nicht in der beets-Datenbank (Pfad dort weicht ab), und
`metaflac` fehlt auf CT120. mutagen ist als beets-Abhaengigkeit vorhanden.

Eingabe: ocr.json aus cover_ocr.py plus Liste der zu entfernenden Bild-SHA1.
Nur Bilder mit genau diesen Pruefsummen werden entfernt, andere Bilder in
derselben Datei bleiben stehen.

Ablauf je Datei:
  1. Audio-Pruefsumme vorher (ffmpeg -map 0:a -f md5)
  2. entferntes Bild einmal je Pruefsumme nach SICHERUNG/bilder/ (Rueckweg)
  3. Bild entfernen, speichern
  4. Audio-Pruefsumme nachher - weicht sie ab: Abbruch mit Fehlercode
Ohne --ausfuehren wird nur gezaehlt und nichts geschrieben.
"""
import argparse, hashlib, json, os, subprocess, sys
import mutagen
from mutagen.flac import FLAC
from mutagen.id3 import ID3
from mutagen.mp4 import MP4


def audio_md5(pfad):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', pfad, '-map', '0:a', '-f', 'md5', '-'],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        raise RuntimeError('ffmpeg: %s' % r.stderr.strip()[:200])
    return r.stdout.strip()


def entferne(pfad, ziele, sicherung, ausfuehren):
    f = mutagen.File(pfad)
    weg = []
    if isinstance(f, FLAC):
        behalten = [p for p in f.pictures if hashlib.sha1(p.data).hexdigest() not in ziele]
        weg = [p.data for p in f.pictures if hashlib.sha1(p.data).hexdigest() in ziele]
        if weg and ausfuehren:
            f.clear_pictures()
            for p in behalten:
                f.add_picture(p)
    elif isinstance(f, MP4):
        covr = list((f.tags or {}).get('covr', []))
        weg = [bytes(c) for c in covr if hashlib.sha1(bytes(c)).hexdigest() in ziele]
        if weg and ausfuehren:
            rest = [c for c in covr if hashlib.sha1(bytes(c)).hexdigest() not in ziele]
            if rest:
                f.tags['covr'] = rest
            else:
                del f.tags['covr']
    elif f is not None and isinstance(getattr(f, 'tags', None), ID3):
        alle = f.tags.getall('APIC')
        weg = [fr.data for fr in alle if hashlib.sha1(fr.data).hexdigest() in ziele]
        if weg and ausfuehren:
            # Alle APIC raus und nur die nicht betroffenen zurueck - delall('APIC:desc')
            # wuerde bei gleichem desc auch ein echtes Cover mitnehmen.
            f.tags.delall('APIC')
            for fr in alle:
                if hashlib.sha1(fr.data).hexdigest() not in ziele:
                    f.tags.add(fr)
    if not weg:
        return 0
    for b in weg:
        ziel = os.path.join(sicherung, 'bilder', hashlib.sha1(b).hexdigest())
        if ausfuehren and not os.path.exists(ziel):
            with open(ziel, 'wb') as fh:
                fh.write(b)
    if ausfuehren:
        f.save()
    return len(weg)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ocr', required=True, help='ocr.json aus cover_ocr.py')
    ap.add_argument('--sha1', required=True, help='Datei mit einer Bild-SHA1 je Zeile')
    ap.add_argument('--sicherung', required=True)
    ap.add_argument('--ausfuehren', action='store_true')
    a = ap.parse_args()

    ziele = {z.strip() for z in open(a.sha1) if z.strip() and not z.startswith('#')}
    d = json.load(open(a.ocr))
    dateien = set()
    for gruppe in d['treffer'] + d['kaputt']:
        if gruppe['sha1'] in ziele:
            dateien.update(gruppe['dateien'])
    dateien = sorted(dateien)
    print('Bildgruppen: %d, Dateien: %d, Modus: %s'
          % (len(ziele), len(dateien), 'AUSFUEHREN' if a.ausfuehren else 'PROBE'))
    if not a.ausfuehren:
        return 0

    os.makedirs(os.path.join(a.sicherung, 'bilder'), exist_ok=True)
    protokoll = open(os.path.join(a.sicherung, 'protokoll.tsv'), 'a')
    fertig = fehler = 0
    for pfad in dateien:
        try:
            vorher = audio_md5(pfad)
            n = entferne(pfad, ziele, a.sicherung, True)
            nachher = audio_md5(pfad)
        except Exception as e:
            fehler += 1
            protokoll.write('FEHLER\t%s\t%s\n' % (pfad, e))
            continue
        if vorher != nachher:
            protokoll.write('AUDIO_GEAENDERT\t%s\t%s\t%s\n' % (pfad, vorher, nachher))
            protokoll.close()
            print('ABBRUCH: Audio veraendert in %s' % pfad)
            return 2
        protokoll.write('OK\t%s\t%d\t%s\n' % (pfad, n, vorher))
        fertig += 1
    protokoll.close()
    print('fertig: %d, Fehler: %d (Details in protokoll.tsv)' % (fertig, fehler))
    return 1 if fehler else 0


if __name__ == '__main__':
    sys.exit(main())

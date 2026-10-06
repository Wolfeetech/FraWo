#!/usr/bin/env python3
"""Neue Musik in die Radio-Bibliothek ablegen (Odoo #1928).

Ablauf fuer einen Neuzugangs-Ordner (z. B. Inbox/neuzugang-20261006), NACH dem Putzen
(radio_ape_entfernen.py, radio_titel_putzen.py, radio_cover_entfernen.py):
  1. Jede Audiodatei: Kuenstler/Titel/Album/Genre aus den (geputzten) Tags.
  2. Dublette? Gleicher Schluessel "kuenstler - titel" (normalisiert) in Master_Library UND
     Laufzeit +-2 s -> nicht ablegen (Liste dubletten.tsv).
  3. Sonst: Master_Library/<Genre>/<Kuenstler>/<Album oder Single>/<Kuenstler - Titel>.<ext>
     Genre = erster Wert; existiert ein Bibliotheksordner gleichen Namens (Gross/Klein egal),
     wird er benutzt, sonst neu angelegt. Keine neuen Mischordner ("A;B").
Verschoben wird nur mit --ausfuehren; Protokoll mit Rueckweg in <sicherung>/ablage.tsv.
"""
import argparse, os, re, shutil, sys, unicodedata
sys.path.insert(0, '/var/lib/beets')
import mutagen
from radio_titel_putzen import lade_tags, putze_album

AUDIO = ('.mp3', '.flac', '.wav', '.aiff', '.aif', '.m4a', '.ogg')
M = '/mnt/music/Master_Library'


def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\.(mp3|flac|wav|aiff?|m4a|ogg)$', '', s)
    s = re.sub(r'^\d{1,3}\s*[-_.]?\s*', '', s)
    s = re.sub(r'\((original|extended|radio)( mix| edit)?\)', '', s)
    return re.sub(r'[^a-z0-9]+', '', s)


def sauber(s):
    return re.sub(r'[\\/:*?"<>|]', '_', s).strip(' .') or 'Unbekannt'


def tag(f, k):
    try:
        return str((f.get(k) or [''])[0]).strip()
    except Exception:
        return ''


def dauer(p):
    try:
        return mutagen.File(p).info.length
    except Exception:
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quelle', required=True)
    ap.add_argument('--sicherung', required=True)
    ap.add_argument('--ausfuehren', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.sicherung, exist_ok=True)

    genres = {g.lower(): g for g in os.listdir(M) if os.path.isdir(os.path.join(M, g))}
    index = {}
    for w, _, fs in os.walk(M):
        for f in fs:
            if f.lower().endswith(AUDIO):
                index.setdefault(norm(f), []).append(os.path.join(w, f))

    plan, dubletten, unklar = [], [], []
    for w, _, fs in os.walk(a.quelle):
        for name in sorted(fs):
            if not name.lower().endswith(AUDIO):
                continue
            p = os.path.join(w, name)
            try:
                f = lade_tags(p)
            except Exception:  # kaputte/leere Datei -> Liste unklar, nichts verschieben
                f = None
            k, t = (tag(f, 'artist'), tag(f, 'title')) if f is not None else ('', '')
            if not k or not t:
                unklar.append(p)
                continue
            schluessel = norm(f'{k} - {t}')
            d = dauer(p)
            treffer = [q for q in index.get(schluessel, []) if d and dauer(q) and abs(dauer(q) - d) <= 2]
            if treffer:
                dubletten.append((p, treffer[0]))
                continue
            genre1 = re.split(r'[;,/]', tag(f, 'genre') or 'Unsortiert')[0].strip() or 'Unsortiert'
            gordner = genres.get(genre1.lower(), sauber(genre1.title() if genre1.islower() else genre1))
            album = putze_album(tag(f, 'album')) or 'Single'
            ziel = os.path.join(M, gordner, sauber(k), sauber(album), sauber(f'{k} - {t}') + os.path.splitext(name)[1].lower())
            if os.path.exists(ziel):
                dubletten.append((p, ziel))
                continue
            plan.append((p, ziel))
            index.setdefault(schluessel, []).append(ziel)  # Dubletten innerhalb des Neuzugangs

    with open(os.path.join(a.sicherung, 'dubletten.tsv'), 'w', encoding='utf-8') as fh:
        fh.writelines(f'{p}\t{q}\n' for p, q in dubletten)
    with open(os.path.join(a.sicherung, 'unklar.tsv'), 'w', encoding='utf-8') as fh:
        fh.writelines(f'{p}\n' for p in unklar)
    if a.ausfuehren:
        with open(os.path.join(a.sicherung, 'ablage.tsv'), 'w', encoding='utf-8') as log:
            for p, ziel in plan:
                os.makedirs(os.path.dirname(ziel), exist_ok=True)
                shutil.move(p, ziel)
                log.write(f'{p}\t{ziel}\n')
    else:
        for p, ziel in plan[:40]:
            print('  ', ziel.replace(M + '/', ''))
    print('Modus: %s | neu: %d | Dubletten (bleiben im Eingang): %d | unklar (ohne Kuenstler/Titel): %d'
          % ('AUSFUEHREN' if a.ausfuehren else 'PROBE', len(plan), len(dubletten), len(unklar)))


if __name__ == '__main__':
    main()

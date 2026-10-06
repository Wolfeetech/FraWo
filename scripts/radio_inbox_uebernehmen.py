#!/usr/bin/env python3
"""Sende-Titel, die nur im Eingangsordner liegen, in die Bibliothek uebernehmen (Odoo #1916).

AzuraCast sieht nur Master_Library und Curated_Playlists (Freigabe [sender]). Links aus den Sendungen
nach Inbox/_STAGING_RAW sind fuer den Sender tot. Fuer jeden noch offenen Link aus
/var/lib/beets/inbox_abgleich_20261005.tsv (ohne die schon umgehaengten):
  1. Datei nach Master_Library/<Genre>/<Kuenstler>/Single/<Kuenstler - Titel>.<ext> KOPIEREN
     (Inbox bleibt unveraendert). Gibt es dort schon eine Datei gleichen Namens mit anderem Ton,
     bekommt die neue den Zusatz " [Inbox]".
  2. Sendungs-Link auf die neue Datei umhaengen (absolut/relativ wie vorher).
Rueckweg: /var/lib/beets/inbox_uebernahme_20261006.tsv (Link, altes Ziel, neue Datei, neu kopiert ja/nein).
Ohne --ausfuehren nur Plan ausgeben.
"""
import os, re, shutil, subprocess, sys
sys.path.insert(0, '/var/lib/beets')
import mutagen
from radio_titel_putzen import lade_tags

M = '/mnt/music/'
AUS = '--ausfuehren' in sys.argv
LOG = '/var/lib/beets/inbox_uebernahme_20261006.tsv'


def tag(p, k):
    try:
        v = (lade_tags(p).get(k) or [''])[0]
    except Exception:
        v = ''
    if not v:
        try:
            f = mutagen.File(p, easy=True)
            v = ((f.tags or {}).get(k) or [''])[0] if f else ''
        except Exception:
            v = ''
    return str(v).strip()


def md5(p):
    return subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-map', '0:a', '-f', 'md5', '-'],
                          capture_output=True, text=True).stdout.strip()


def sauber(s):
    return re.sub(r'[\\/:*?"<>|]', '_', s).strip(' .') or 'Unbekannt'


GENRES = {g.lower(): g for g in os.listdir(M + 'Master_Library') if os.path.isdir(M + 'Master_Library/' + g)}


def genre_ordner(g):
    for teil in re.split(r'[;,/]', g):
        k = teil.strip().lower()
        if k in GENRES:
            return GENRES[k]
    return GENRES.get('electronic', 'Electronic')


erledigt = {l.split('\t')[0] for l in open('/var/lib/beets/inbox_umhaengen_20261005.tsv', encoding='utf-8')}
plan = []
for z in open('/var/lib/beets/inbox_abgleich_20261005.tsv', encoding='utf-8'):
    t = z.rstrip('\n').split('\t')
    link, quelle = t[1], t[2]
    if link in erledigt or not os.path.lexists(link) or not os.path.exists(quelle):
        continue
    ext = os.path.splitext(quelle)[1].lower()
    kuenstler = tag(quelle, 'artist') or os.path.basename(os.path.dirname(os.path.dirname(quelle)))
    titel = tag(quelle, 'title') or re.sub(r'^\d{1,3}\s*[-_.]?\s*', '', os.path.splitext(os.path.basename(quelle))[0])
    titel = re.sub(r'\s*\(\d+\)$', '', titel)  # "(2)"-Kopiezaehler aus Dateinamen
    ordner = os.path.join(M, 'Master_Library', genre_ordner(tag(quelle, 'genre')), sauber(kuenstler), 'Single')
    ziel = os.path.join(ordner, sauber(f'{kuenstler} - {titel}') + ext)
    neu = True
    if os.path.exists(ziel):
        if md5(ziel) == md5(quelle):
            neu = False
        else:
            ziel = os.path.join(ordner, sauber(f'{kuenstler} - {titel} [Inbox]') + ext)
    plan.append((link, os.readlink(link), quelle, ziel, neu))

for link, _, quelle, ziel, neu in plan:
    print('%s %s\n      -> %s' % ('KOPIE ' if neu else 'VORHANDEN', quelle.replace(M, ''), ziel.replace(M, '')))
print('Titel:', len(plan), '| neu kopiert:', sum(1 for p in plan if p[4]))
if not AUS:
    sys.exit(0)
with open(LOG, 'w', encoding='utf-8') as log:
    for link, altziel, quelle, ziel, neu in plan:
        if neu and not os.path.exists(ziel):
            os.makedirs(os.path.dirname(ziel), exist_ok=True)
            shutil.copy2(quelle, ziel)
            if md5(ziel) != md5(quelle):
                sys.exit(f'ABBRUCH: Kopie fehlerhaft {ziel}')
        neues = ziel if os.path.isabs(altziel) else os.path.relpath(ziel, os.path.dirname(link))
        os.symlink(neues, link + '.neu'); os.replace(link + '.neu', link)
        log.write('\t'.join([link, altziel, ziel, 'ja' if neu else 'nein']) + '\n')
tot = sum(1 for p in plan if not os.path.exists(p[0]))
print('umgehaengt:', len(plan), '| danach tot:', tot, '| Protokoll:', LOG)

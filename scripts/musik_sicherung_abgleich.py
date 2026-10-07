#!/usr/bin/env python3
"""Drive-Musiksicherung (gdrive:FraWo_Musik) gegen die Live-Bibliothek abgleichen (Odoo #1927/#1929).

Eingaben (Anker, /root/musik-abgleich-20261007):
  drive_md5.json  rclone lsjson -R --hash md5 gdrive:FraWo_Musik
  live_md5.txt    md5sum ueber /anker-backup/musik-umzug-20261005 (Pfade relativ, "./...")
Je Drive-Datei eine Klasse:
  IDENTISCH      gleicher Inhalt (MD5) liegt in der Bibliothek
  DRIVE_DUBLETTE gleicher Inhalt liegt in Drive schon unter anderem Pfad (erste Fundstelle zaehlt)
  ALTE_FASSUNG   gleicher relativer Pfad in der Bibliothek, Inhalt geaendert (z. B. Tags/APE/Cover geputzt)
  GLEICHER_TITEL kein Pfad-/Inhaltstreffer, aber Kuenstler-Titel-Name kommt in der Bibliothek vor
  NUR_IN_DRIVE   Audio ohne jeden Treffer -> Kandidat zum Zurueckholen
  NICHT_AUDIO    Bilder, Dokumente, Datenbanken, Sicherungen
Ausgabe: abgleich.tsv (klasse, pfad, bytes, verweis) und Zusammenfassung je Ordner/Klasse.
Loescht NICHTS.
"""
import collections, json, os, re, sys, unicodedata

D = sys.argv[1] if len(sys.argv) > 1 else '/root/musik-abgleich-20261007'
AUDIO = ('.mp3', '.flac', '.wav', '.aiff', '.aif', '.m4a', '.ogg', '.opus', '.wma')


def norm(name):
    s = unicodedata.normalize('NFKD', os.path.basename(name)).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\.(mp3|flac|wav|aiff?|m4a|ogg|opus|wma)$', '', s)
    s = re.sub(r'\s*\(\d+\)$', '', s)
    s = re.sub(r'^\d{1,3}\s*[-_.]?\s*', '', s)
    s = re.sub(r'\((original|extended|radio)( mix| edit)?\)', '', s)
    return re.sub(r'[^a-z0-9]+', '', s)


live_md5, live_pfad, live_name = {}, set(), set()
for z in open(os.path.join(D, 'live_md5.txt'), encoding='utf-8', errors='surrogateescape'):
    h, p = z.rstrip('\n').split('  ', 1)
    p = p[2:] if p.startswith('./') else p
    live_md5.setdefault(h, p)
    live_pfad.add(p)
    if p.lower().endswith(AUDIO):
        live_name.add(norm(p))

gesehen = {}
zahl = collections.defaultdict(collections.Counter)
groesse = collections.defaultdict(collections.Counter)
with open(os.path.join(D, 'abgleich.tsv'), 'w', encoding='utf-8', errors='surrogateescape') as out:
    for x in json.load(open(os.path.join(D, 'drive_md5.json'), encoding='utf-8')):
        p, g, h = x['Path'], x['Size'], (x.get('Hashes') or {}).get('md5', '')
        rel = p.split('/', 1)[1] if p.startswith('music_hdd/') else p
        if h in live_md5:
            k, ref = 'IDENTISCH', live_md5[h]
        elif h in gesehen:
            k, ref = 'DRIVE_DUBLETTE', gesehen[h]
        elif not p.lower().endswith(AUDIO):
            k, ref = 'NICHT_AUDIO', ''
        elif rel in live_pfad:
            k, ref = 'ALTE_FASSUNG', rel
        elif norm(p) in live_name:
            k, ref = 'GLEICHER_TITEL', ''
        else:
            k, ref = 'NUR_IN_DRIVE', ''
        gesehen.setdefault(h, p)
        ordner = '/'.join(p.split('/')[:2])
        zahl[ordner][k] += 1
        groesse[ordner][k] += g
        out.write(f'{k}\t{p}\t{g}\t{ref}\n')

KL = ['IDENTISCH', 'DRIVE_DUBLETTE', 'ALTE_FASSUNG', 'GLEICHER_TITEL', 'NUR_IN_DRIVE', 'NICHT_AUDIO']
summe = collections.Counter()
print('%-40s' % 'Ordner' + ''.join('%16s' % k[:15] for k in KL))
for o in sorted(groesse, key=lambda o: -sum(groesse[o].values())):
    print('%-40s' % o[:40] + ''.join('%9.1f GB/%5d' % (groesse[o][k] / 1e9, zahl[o][k]) if zahl[o][k] else '%16s' % '-' for k in KL))
    summe.update(groesse[o])
print('SUMME GB: ' + ', '.join(f'{k} {summe[k] / 1e9:.1f}' for k in KL))

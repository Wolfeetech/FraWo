#!/usr/bin/env python3
"""Drive-Musik gegen die Radio-Bibliothek abgleichen, ohne etwas herunterzuladen (Odoo #1929).

Eingaben: JSON-Listen je Drive-Hauptordner aus drive_musik_inventar.sh (rclone lsjson), dazu die
Bibliothek (live: Anker /anker-backup/musik-umzug-20261005, bis zur SSD #1919).
Je Drive-Datei:
  GLEICH   - gleiche Groesse (Bytes) UND gleicher normalisierter Name wie eine Bibliotheksdatei
  NAME     - gleicher normalisierter Name, andere Groesse (andere Fassung/Kodierung) -> spaeter per Ton pruefen
  NEU      - weder noch -> Kandidat fuer radio_neuzugang.sh
Ausgabe: <out>/abgleich.tsv (ordner, pfad, bytes, status, bibliothekspfad) und Zusammenfassung je Ordner.
"""
import collections, glob, json, os, re, sys, unicodedata

INV = sys.argv[1] if len(sys.argv) > 1 else '/root/drive-musik-inventar-20261006'
LIB = sys.argv[2] if len(sys.argv) > 2 else '/anker-backup/musik-umzug-20261005'
AUDIO = ('.mp3', '.flac', '.wav', '.aiff', '.aif', '.m4a', '.ogg')


def norm(name):
    s = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\.(mp3|flac|wav|aiff?|m4a|ogg)$', '', s)
    s = re.sub(r'\s*\(\d+\)$', '', s)              # "(2)"-Kopiezaehler
    s = re.sub(r'^\d{1,3}\s*[-_.]?\s*', '', s)     # Tracknummer
    s = re.sub(r'\((original|extended|radio)( mix| edit)?\)', '', s)
    return re.sub(r'[^a-z0-9]+', '', s)


nach_groesse = collections.defaultdict(list)
nach_name = collections.defaultdict(list)
for wurzel in ('Master_Library', 'Inbox', 'Quarantine'):
    for w, _, fs in os.walk(os.path.join(LIB, wurzel)):
        for f in fs:
            if f.lower().endswith(AUDIO):
                p = os.path.join(w, f)
                try:
                    g = os.path.getsize(p)
                except OSError:
                    continue
                nach_groesse[g].append(p)
                nach_name[norm(f)].append(p)

zusammen = collections.defaultdict(collections.Counter)
groesse = collections.defaultdict(collections.Counter)
with open(os.path.join(INV, 'abgleich.tsv'), 'w', encoding='utf-8') as out:
    for j in sorted(glob.glob(os.path.join(INV, '*.json'))):
        ordner = os.path.basename(j)[:-5]
        try:
            eintraege = json.load(open(j, encoding='utf-8'))
        except Exception:
            print('UNVOLLSTAENDIG:', ordner)
            continue
        for x in eintraege:
            n, g = norm(x['Name']), x['Size']
            gleiche = [p for p in nach_groesse.get(g, []) if norm(os.path.basename(p)) == n]
            if gleiche:
                st, ref = 'GLEICH', gleiche[0]
            elif n in nach_name:
                st, ref = 'NAME', nach_name[n][0]
            else:
                st, ref = 'NEU', ''
            # ganz gleiche Groesse, anderer Name: sehr wahrscheinlich dieselbe Datei umbenannt
            if st == 'NEU' and g > 1_000_000 and len(nach_groesse.get(g, [])) == 1:
                st, ref = 'GROESSE', nach_groesse[g][0]
            zusammen[ordner][st] += 1
            groesse[ordner][st] += g
            out.write('\t'.join([ordner, x['Path'], str(g), st, ref.replace(LIB + '/', '')]) + '\n')

print('%-34s %7s %7s %7s %7s %9s' % ('Drive-Ordner', 'GLEICH', 'GROESSE', 'NAME', 'NEU', 'NEU in GB'))
for o in sorted(zusammen, key=lambda o: -sum(groesse[o].values())):
    z = zusammen[o]
    print('%-34s %7d %7d %7d %7d %9.1f' % (o[:34], z['GLEICH'], z['GROESSE'], z['NAME'], z['NEU'], groesse[o]['NEU'] / 1e9))

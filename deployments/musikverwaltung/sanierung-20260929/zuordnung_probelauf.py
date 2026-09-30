# 🤖 [Claude] 29.09.2026 — Odoo #1263, Sanierung Phase 3.4: Zuordnungs-PROBELAUF.
# Liest musik.db nur lesend, liest Datei-Tags, schreibt nur CSV-Listen nach /root/sanierung-20260929/.
# Aendert weder Datenbank noch Musikdateien.
import os, re, sqlite3, csv, collections, unicodedata, time, sys
from mediafile import MediaFile

AUS = '/root/sanierung-20260929'
os.makedirs(AUS, exist_ok=True)
ML = b'/mnt/music/Master_Library'
AUDIO = (b'.mp3', b'.flac', b'.m4a', b'.aac', b'.wav', b'.aiff', b'.aif', b'.ogg', b'.opus', b'.wma', b'.alac')
t0 = time.time()

def norm(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode().lower()
    s = re.sub(r'\((original|extended|radio|club|album)[^)]*\)', '', s)
    s = re.sub(r'\b(feat|ft)\b.*', '', s)
    s = re.sub(r'[^a-z0-9]+', ' ', s)
    return s.strip()

def stem(p):
    b = os.path.splitext(os.path.basename(p))[0]
    b = re.sub(r'^\d{1,3}[\s._-]+', '', b)          # Tracknummer vorne
    b = re.sub(r'[\s_]*\(\d\)$', '', b)              # (2)-Suffix der kaputten Pipeline
    b = re.sub(r'_new_\d+$', '', b)
    return norm(b)

db = sqlite3.connect('file:/var/lib/beets/musik.db?mode=ro', uri=True)
flex = collections.defaultdict(dict)
for eid, k, v in db.execute("select entity_id, key, value from item_attributes where key in ('acoustid_id','vibe')"):
    flex[eid][k] = v
items = []
for iid, p, artist, title, length, mbt in db.execute('select id, path, artist, title, length, mb_trackid from items'):
    if isinstance(p, str): p = p.encode('utf-8', 'surrogateescape')
    items.append(dict(id=iid, path=p, artist=artist or '', title=title or '', length=length or 0,
                      mbt=mbt or '', acid=flex[iid].get('acoustid_id', '') or ''))
lebend_pfade = set(i['path'] for i in items if os.path.exists(i['path']))
tot = [i for i in items if not os.path.exists(i['path'])]
print('Eintraege', len(items), '| tot', len(tot), '| lebend', len(items) - len(tot), flush=True)

# echte Dateien in Master_Library
dateien = []
for wurzel, ordner, namen in os.walk(ML):
    for n in namen:
        if n.lower().endswith(AUDIO) and not n.startswith(b'.ntfs-3g'):
            dateien.append(os.path.join(wurzel, n))
unbekannt = [f for f in dateien if f not in lebend_pfade]
print('Dateien', len(dateien), '| davon ohne DB-Eintrag', len(unbekannt), '| %.0fs' % (time.time() - t0), flush=True)

# Tags der unbekannten Dateien lesen (seriell, Platte schonen)
info = {}
fehler = 0
for n, f in enumerate(unbekannt):
    d = dict(artist='', title='', length=0, mbt='', acid='')
    try:
        m = MediaFile(f.decode('utf-8', 'surrogateescape'))
        d.update(artist=m.artist or '', title=m.title or '', length=m.length or 0,
                 mbt=m.mb_trackid or '', acid=getattr(m, 'acoustid_id', '') or '')
    except Exception:
        fehler += 1
    info[f] = d
    if n % 1000 == 0:
        print('  Tags gelesen', n, '%.0fs' % (time.time() - t0), flush=True)
print('Tags gelesen', len(info), '| unlesbar', fehler, flush=True)

idx = {s: collections.defaultdict(list) for s in (1, 2, 3, 5)}
for f, d in info.items():
    if d['acid']: idx[1][d['acid']].append(f)
    if d['mbt']: idx[2][d['mbt']].append(f)
    if d['artist'] and d['title']: idx[3][(norm(d['artist']), norm(d['title']))].append(f)
    idx[5][stem(f.decode('utf-8', 'surrogateescape'))].append(f)

def kandidaten(i):
    if i['acid'] and idx[1].get(i['acid']): return 1, idx[1][i['acid']]
    if i['mbt'] and idx[2].get(i['mbt']): return 2, idx[2][i['mbt']]
    k = (norm(i['artist']), norm(i['title']))
    if k[0] and k[1] and idx[3].get(k):
        c = idx[3][k]
        eng = [f for f in c if i['length'] and info[f]['length'] and abs(info[f]['length'] - i['length']) <= 2]
        if len(eng) >= 1: return 3, eng
        return 4, c
    s = stem(i['path'].decode('utf-8', 'surrogateescape'))
    if s and idx[5].get(s): return 5, idx[5][s]
    return 0, []

vorschlag = {}
for i in tot:
    vorschlag[i['id']] = kandidaten(i)
# Zwei-auf-eins erkennen
ziel_zaehler = collections.Counter(c[0] for st, c in vorschlag.values() if len(c) == 1)
eindeutig, mehrdeutig, zwei_auf_eins, ohne = [], [], [], []
byid = {i['id']: i for i in tot}
for iid, (st, c) in vorschlag.items():
    i = byid[iid]
    zeile = [iid, i['artist'], i['title'], round(i['length']), i['path'].decode('utf-8', 'surrogateescape')]
    if not c: ohne.append(zeile)
    elif len(c) > 1: mehrdeutig.append(zeile + [st, ' | '.join(x.decode('utf-8', 'surrogateescape') for x in c[:5])])
    elif ziel_zaehler[c[0]] > 1: zwei_auf_eins.append(zeile + [st, c[0].decode('utf-8', 'surrogateescape')])
    else: eindeutig.append(zeile + [st, c[0].decode('utf-8', 'surrogateescape')])

kopf = ['id', 'artist', 'title', 'laenge_s', 'alter_pfad']
for name, rows, extra in (('eindeutig', eindeutig, ['stufe', 'neuer_pfad']), ('mehrdeutig', mehrdeutig, ['stufe', 'kandidaten']),
                          ('zwei_auf_eins', zwei_auf_eins, ['stufe', 'neuer_pfad']), ('ohne_treffer', ohne, [])):
    with open(os.path.join(AUS, name + '.csv'), 'w', newline='', encoding='utf-8', errors='surrogateescape') as fh:
        w = csv.writer(fh, delimiter=';'); w.writerow(kopf + extra); w.writerows(rows)
stufen = collections.Counter(r[5] for r in eindeutig)
print('ERGEBNIS eindeutig', len(eindeutig), dict(sorted(stufen.items())), '| zwei_auf_eins', len(zwei_auf_eins),
      '| mehrdeutig', len(mehrdeutig), '| ohne_treffer', len(ohne))
belegt = set(r[6] for r in eindeutig) | set(r[6] for r in zwei_auf_eins)
print('Dateien ohne DB-Eintrag, die danach immer noch keinen haetten:', len([f for f in unbekannt if f.decode('utf-8', 'surrogateescape') not in belegt]))
print('fertig %.0fs' % (time.time() - t0))

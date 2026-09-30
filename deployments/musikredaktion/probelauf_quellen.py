"""Probelauf beide Quellen: erst Beatport, dann Discogs — dieselben 200 Titel (Odoo #1090).
Liest nur, schreibt nur /root/musikredaktion-probe/quellen.csv."""
import collections
import csv
import random
import sqlite3
import sys

sys.path.insert(0, '/opt/musikredaktion')
import beatport_abgleich as bp
import discogs_abgleich as dc


def env(pfad):
    with open(pfad) as f:
        return dict(l.strip().split('=', 1) for l in f if '=' in l)


b = env('/etc/frawo/beatport.env')
s = bp.anmelden(b['BEATPORT_USER'], b['BEATPORT_PASS'])
c = dc.DiscogsClient(env('/etc/frawo/discogs.env')['DISCOGS_TOKEN'])
db = sqlite3.connect('file:/var/lib/beets/musik.db?mode=ro', uri=True)
rows = db.execute('select id, artist, title, length, genre from items order by id').fetchall()
random.seed(20260930)
probe = random.sample(rows, 200)
zaehl = collections.Counter()
with open('/root/musikredaktion-probe/quellen.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['id', 'artist', 'title', 'genre_alt', 'quelle_art', 'status', 'styles', 'bpm', 'tonart', 'quelle'])
    for n, (iid, artist, title, length, genre) in enumerate(probe, 1):
        titel = {'artist': artist or '', 'title': title or '', 'length': length or 0}
        a, t = dc.suchbegriffe(titel)
        art, r = 'keine', {'status': 'unklar', 'styles': [], 'quelle': ''}
        if a and t:
            r = bp.bewerte(titel, bp.suche(s, a, t))
            art = 'beatport'
            if r['status'] != 'belegt':
                r2 = dc.bewerte(titel, c.suche(a, t))
                if r2['status'] == 'belegt' or r['status'] == 'unklar':
                    r, art = r2, 'discogs'
        zaehl[(art if r['status'] == 'belegt' else '-', r['status'])] += 1
        w.writerow([iid, artist, title, genre, art, r['status'], '|'.join(r['styles']), r.get('bpm') or '',
                    r.get('tonart') or '', r['quelle']])
        if n % 25 == 0:
            print(n, dict(zaehl), flush=True)
belegt = sum(v for (a, st), v in zaehl.items() if st == 'belegt')
print('ERGEBNIS', dict(zaehl), 'quote=%.0f%%' % (100 * belegt / 200))

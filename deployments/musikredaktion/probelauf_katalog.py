"""Probelauf: 200 zufällige Titel gegen Discogs (Odoo #1090). Liest nur, schreibt nur CSV."""
import collections
import csv
import os
import random
import sqlite3
import sys

sys.path.insert(0, '/opt/musikredaktion')
import discogs_abgleich as d

AUS = '/root/musikredaktion-probe'
os.makedirs(AUS, exist_ok=True)
with open('/etc/frawo/discogs.env') as f:
    token = dict(l.strip().split('=', 1) for l in f if '=' in l)['DISCOGS_TOKEN']
db = sqlite3.connect('file:/var/lib/beets/musik.db?mode=ro', uri=True)
rows = db.execute('select id, artist, title, length, genre from items order by id').fetchall()
random.seed(20260930)
probe = random.sample(rows, 200)
c = d.DiscogsClient(token)
zaehl = collections.Counter()
with open(os.path.join(AUS, 'katalog.csv'), 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['id', 'artist', 'title', 'genre_alt', 'status', 'genre', 'styles', 'quelle'])
    for n, (iid, artist, title, length, genre) in enumerate(probe, 1):
        titel = {'artist': artist or '', 'title': title or '', 'length': length or 0}
        a, t = d.suchbegriffe(titel)
        treffer = c.suche(a, t) if a and t else []
        r = d.bewerte(titel, treffer)
        zaehl[r['status']] += 1
        w.writerow([iid, artist, title, genre, r['status'], r['genre'], '|'.join(r['styles']), r['quelle']])
        if n % 25 == 0:
            print(n, dict(zaehl), flush=True)
print('ERGEBNIS belegt=%d widerspruch=%d unklar=%d quote=%.0f%%'
      % (zaehl['belegt'], zaehl['widerspruch'], zaehl['unklar'], 100 * zaehl['belegt'] / 200))

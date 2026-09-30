"""Probelauf Klang-Messung: dieselben 200 Titel wie der Katalog-Probelauf, seriell (Odoo #1090).
Liest nur, schreibt nur /root/musikredaktion-probe/messung.csv."""
import csv
import os
import random
import sqlite3
import statistics
import sys
import time

sys.path.insert(0, '/opt/musikredaktion')
import energie_merkmale as e

BIN = '/opt/essentia/essentia-extractors-v2.1_beta2/streaming_extractor_music'
db = sqlite3.connect('file:/var/lib/beets/musik.db?mode=ro', uri=True)
rows = db.execute('select id, artist, title, length, genre from items order by id').fetchall()
random.seed(20260930)
probe = random.sample(rows, 200)
pfade = dict(db.execute('select id, path from items'))
bpm_b = dict(db.execute('select id, bpm from items'))
zeiten, fehler, abw = [], 0, 0
with open('/root/musikredaktion-probe/messung.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.writer(f, delimiter=';')
    w.writerow(['id', 'pfad', 'laenge', 'sekunden', 'bpm', 'bpm_beets', 'tonart', 'tonart_sicherheit',
                'lautheit', 'tanzbarkeit', 'anschlagdichte', 'dynamik', 'fehler'])
    for n, (iid, _, _, laenge, _) in enumerate(probe, 1):
        p = pfade[iid]
        p = p if isinstance(p, bytes) else p.encode('utf-8', 'surrogateescape')
        if not os.path.exists(p):
            continue
        t0 = time.time()
        m = e.messe(p, BIN)
        dt = time.time() - t0
        zeiten.append(dt)
        if 'fehler' in m:
            fehler += 1
        elif bpm_b.get(iid) and abs(m['bpm'] - bpm_b[iid]) / bpm_b[iid] > 0.03:
            abw += 1
        w.writerow([iid, p.decode('utf-8', 'surrogateescape'), round(laenge or 0), round(dt, 1), m.get('bpm'), bpm_b.get(iid),
                    m.get('tonart'), m.get('tonart_sicherheit'), m.get('lautheit'), m.get('tanzbarkeit'),
                    m.get('anschlagdichte'), m.get('dynamik'), m.get('fehler', '')])
        f.flush()
        if n % 20 == 0:
            print(n, 'gemessen', len(zeiten), 'median %.1fs' % statistics.median(zeiten), flush=True)
print('ERGEBNIS gemessen=%d fehler=%d sekunden_median=%.1f sekunden_summe=%.0f bpm_abweichung_ueber_3pct=%d'
      % (len(zeiten), fehler, statistics.median(zeiten), sum(zeiten), abw))

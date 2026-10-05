# Baut SQL fuer AzuraCast: Titel/Kuenstler aller Medien, deren Datei (realpath) in titel.tsv steht,
# und Cover-Reset fuer die von radio_cover_azuracast_zuordnen.py gelieferten IDs.
# Eingabe medien.tsv: id<TAB>unique_id<TAB>path (relativ zu /mnt/music), aus der AzuraCast-DB.
import os
SICH = '/var/lib/beets/ape-entfernt-20261005'
titel = {}
for z in open(SICH + '/titel.tsv', encoding='utf-8'):
    p, t, k = z.rstrip('\n').split('\t')
    titel[p] = (t, k)
def q(s): return "'" + s.replace('\\', '\\\\').replace("'", "''") + "'"
out = ['CREATE TABLE IF NOT EXISTS station_media_bak_20261005_ape AS SELECT id,title,artist,art_updated_at FROM station_media WHERE 1=0;']
n = 0
ids_titel = []
for z in open(SICH + '/medien.tsv', encoding='utf-8'):
    t = z.rstrip('\n').split('\t')
    if len(t) < 3 or not t[0].isdigit():
        continue
    rp = os.path.realpath('/mnt/music/' + t[2])
    if rp in titel:
        ti, ku = titel[rp]
        ids_titel.append(t[0])
        out.append('UPDATE station_media SET title=%s%s WHERE id=%s;' % (q(ti), (', artist=%s' % q(ku)) if ku else '', t[0]))
        n += 1
if ids_titel:
    out.insert(1, 'INSERT INTO station_media_bak_20261005_ape SELECT id,title,artist,art_updated_at FROM station_media WHERE id IN (%s);' % ','.join(ids_titel))
cover_ids = SICH + '/sicherung_cover/azuracast_ids.txt'
if os.path.exists(cover_ids):
    ids = [l.strip() for l in open(cover_ids) if l.strip().isdigit()]
    if ids:
        out.append('INSERT INTO station_media_bak_20261005_ape SELECT id,title,artist,art_updated_at FROM station_media WHERE id IN (%s) AND id NOT IN (SELECT id FROM station_media_bak_20261005_ape);' % ','.join(ids))
        out.append('UPDATE station_media SET art_updated_at=0 WHERE id IN (%s);' % ','.join(ids))
open(SICH + '/nachzug.sql', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('Titel-Updates:', n, '| Cover-Resets:', len(ids) if os.path.exists(cover_ids) else 0)

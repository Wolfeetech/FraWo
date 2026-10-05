# Odoo #1908/#1915, Schritt 2 nach ape_entfernen.py: Eingaben fuer AzuraCast bauen.
# 1) cover_protokoll.tsv  'OK<TAB>pfad<TAB>1' fuer Dateien, deren Cover NUR im APE-Block steckte
#    -> radio_cover_azuracast_zuordnen.py (verschiebt .albumart-Kopien, liefert Medien-IDs)
# 2) titel.tsv  realpath<TAB>titel<TAB>kuenstler  aus dem (sauberen) ID3v2 fuer alle bearbeiteten Dateien
import glob, os, pickle, sys
sys.path.insert(0, '/var/lib/beets')
from mutagen.id3 import ID3
from radio_titel_putzen import lade_tags
SICH = '/var/lib/beets/ape-entfernt-20261005'
cov = open(SICH + '/cover_protokoll.tsv', 'w', encoding='utf-8')
tit = open(SICH + '/titel.tsv', 'w', encoding='utf-8')
n_cov = n_tit = 0
for f in sorted(glob.glob(SICH + '/*.pkl')):
    d = pickle.load(open(f, 'rb')); p = d['pfad']
    if not os.path.exists(p):
        continue
    hatte_ape_cover = any('cover' in k.lower() for k in d['ape'])
    try:
        id3_bild = len(ID3(p).getall('APIC'))
    except Exception:
        id3_bild = 0
    if hatte_ape_cover and id3_bild == 0:
        cov.write('OK\t%s\t1\n' % p); n_cov += 1
    t = lade_tags(p)
    titel = (t.get('title') or [''])[0].strip(); kuenstler = (t.get('artist') or [''])[0].strip()
    if titel:
        tit.write('%s\t%s\t%s\n' % (os.path.realpath(p), titel.replace('\t', ' '), kuenstler.replace('\t', ' '))); n_tit += 1
print('Cover nur im APE-Block:', n_cov, '| Titel aus ID3:', n_tit)

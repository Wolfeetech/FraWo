# 🤖 [Claude] 29.09.2026 — Odoo #1263, Sanierung Phase 3.6: eindeutige Eintraege (Stufe 2+3) auf echte Datei umhaengen.
# Nur ueber die beets-Python-Schnittstelle, blockweise, Abbruch bei erster Ausnahme. Musikdateien werden nicht angefasst.
import csv, os, shutil, sqlite3, sys, time
import beets.library
D = '/root/sanierung-20260929/'
DB = '/var/lib/beets/musik.db'
sich = DB + '.vor-umhaengen-20260929'
if not os.path.exists(sich):
    src = sqlite3.connect('file:%s?mode=ro' % DB, uri=True); dst = sqlite3.connect(sich)
    src.backup(dst); dst.close(); src.close()
print('Sicherung', sich, os.path.getsize(sich))
rows = [r for r in csv.reader(open(D + 'eindeutig.csv', encoding='utf-8', errors='surrogateescape'), delimiter=';')][1:]
rows = [r for r in rows if r[5] in ('2', '3')]
lib = beets.library.Library(DB)
fertig = uebersprungen = 0
log = open(D + 'umhaengen.log', 'a', encoding='utf-8', errors='surrogateescape')
for start in range(0, len(rows), 500):
    with lib.transaction():
        for r in rows[start:start + 500]:
            iid, alt, neu = int(r[0]), r[4], r[6]
            it = lib.get_item(iid)
            neu_b = neu.encode('utf-8', 'surrogateescape')
            if it is None or it.path.decode('utf-8', 'surrogateescape') != alt or not os.path.exists(neu_b) or os.path.exists(it.path):
                uebersprungen += 1; log.write('SKIP %s\n' % iid); continue
            it.path = neu_b
            it.store()
            fertig += 1
            log.write('OK %s\t%s\t%s\n' % (iid, alt, neu))
    print('Block ab', start, '| umgehaengt', fertig, '| uebersprungen', uebersprungen, flush=True)
log.close()
tot = 0
db = sqlite3.connect('file:%s?mode=ro' % DB, uri=True)
for (p,) in db.execute('select path from items'):
    if not os.path.exists(p if isinstance(p, bytes) else p.encode('utf-8', 'surrogateescape')): tot += 1
vibe = db.execute("select count(*) from item_attributes where key='vibe'").fetchone()[0]
print('FERTIG umgehaengt', fertig, '| tote Pfade jetzt', tot, '| vibe-Merkmale', vibe)

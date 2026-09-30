# 🤖 [Claude] 29.09.2026 — Odoo #1263, Phase 3.5: doppelte Eintraege zusammenlegen (Regel Spec 5.5).
# Je Datei bleibt ein Eintrag (der vollste). Leere Felder werden aus den Doppeln uebernommen,
# abweichende Werte kommen auf die Pruefliste. Doppel werden NUR aus der Datenbank entfernt (keine Datei geloescht).
import csv, os, sqlite3
import beets.library
D = '/root/sanierung-20260929/'
DB = '/var/lib/beets/musik.db'
sich = DB + '.vor-zusammenlegen-20260929'
if not os.path.exists(sich):
    src = sqlite3.connect('file:%s?mode=ro' % DB, uri=True); dst = sqlite3.connect(sich)
    src.backup(dst); dst.close(); src.close()
print('Sicherung', sich, os.path.getsize(sich))
SCHUETZEN = {'id', 'path', 'album_id', 'added', 'mtime'}
import re
# Wolf 29.09.: nichts Werbe-/Linkartiges darf von einem Doppel uebernommen werden
MUELL = re.compile(r'https?://|www\.|\b[a-z0-9-]+\.(com|net|club|ru|org|info|biz|to|cc|de|eu|me|io|fm|pl|xyz|top|site|online)\b'
                   r'|myfreemp3|mp3juice|promo only|free download|zippyshare|torrent', re.I)
lib = beets.library.Library(DB)
rows = list(csv.reader(open(D + 'zusammenlegen.csv', encoding='utf-8', errors='surrogateescape'), delimiter=';'))[1:]
pruef = open(D + 'zusammenlegen_pruefliste.csv', 'w', newline='', encoding='utf-8', errors='surrogateescape')
pw = csv.writer(pruef, delimiter=';'); pw.writerow(['bleibt_id', 'entfaellt_id', 'feld', 'wert_bleibt', 'wert_entfaellt'])
log = open(D + 'zusammenlegen.log', 'a', encoding='utf-8', errors='surrogateescape')
gruppen = entfernt = uebernommen = uebersprungen = 0
for start in range(0, len(rows), 200):
    with lib.transaction():
        for datei, bleibt, entfaellt, _ in rows[start:start + 200]:
            ziel = datei.encode('utf-8', 'surrogateescape')
            s = lib.get_item(int(bleibt))
            weg = [lib.get_item(int(x)) for x in entfaellt.split(',') if x]
            belegt = len(lib.items(beets.library.PathQuery('path', ziel)))
            if s is None or None in weg or not os.path.exists(ziel) or belegt or os.path.exists(s.path):
                uebersprungen += 1; log.write('SKIP %s\n' % bleibt); continue
            for w in weg:
                for k in w.keys(computed=False, with_album=False):
                    if k in SCHUETZEN: continue
                    wv, sv = w.get(k), s.get(k)
                    if wv in (None, '', 0, 0.0): continue
                    if isinstance(wv, str) and MUELL.search(wv) and k != 'research_source': continue
                    if sv in (None, '', 0, 0.0):
                        s[k] = wv; uebernommen += 1
                    elif sv != wv and k in ('vibe', 'research_source', 'genre', 'style', 'bpm', 'mb_trackid', 'acoustid_id'):
                        pw.writerow([s.id, w.id, k, sv, wv])
            s.path = ziel
            s.store()
            for w in weg:
                log.write('ENTFERNT %s -> %s\n' % (w.id, s.id))
                w.remove(delete=False, with_album=True)
                entfernt += 1
            gruppen += 1
    print('Block ab', start, '| Gruppen', gruppen, '| entfernt', entfernt, '| uebersprungen', uebersprungen, flush=True)
pruef.close(); log.close()
db = sqlite3.connect('file:%s?mode=ro' % DB, uri=True)
n = db.execute('select count(*) from items').fetchone()[0]
tot = sum(1 for (p,) in db.execute('select path from items') if not os.path.exists(p if isinstance(p, bytes) else p.encode('utf-8', 'surrogateescape')))
vibe = db.execute("select count(*) from item_attributes where key='vibe'").fetchone()[0]
print('FERTIG Gruppen', gruppen, '| Felder uebernommen', uebernommen, '| Eintraege jetzt', n, '| tote Pfade', tot, '| vibe-Merkmale', vibe)

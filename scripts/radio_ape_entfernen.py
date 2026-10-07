# Odoo #1908/#1915: APEv2-Altblock aus MP3s entfernen (alte Titel + Haendler-Cover + Werbefelder).
# ID3v2 bleibt unberuehrt. Ton-MD5 vor/nach; Probelauf ohne --ausfuehren.
# Sicherung (seit 07.10.2026, Review Hermes #1908/#1915): je Datei <nr>.roh = alle Bytes ab der ersten Abweichung
# (APE-Block samt allem, was dahinter lag) plus <nr>.json mit Pfad, Laenge des gemeinsamen Anfangs und SHA-256 vorher.
# Rueckweg byte-genau: radio_ape_zurueck.py (kuerzt auf den gemeinsamen Anfang und haengt .roh an, prueft SHA-256).
# Bis 07.10. wurden nur zerlegte Felder (.pkl) gesichert - die sind KEINE byte-genaue Ruecksicherung.
import os, sys, json, hashlib, subprocess
from mutagen.apev2 import APEv2, APENoHeaderError, delete
AUS = '--ausfuehren' in sys.argv
def _arg(name, std):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else std
# Seit 06.10.2026 auch fuer Neuzugaenge nutzbar (#1928): --root <ordner> --sicherung <ordner>
ROOT = _arg('--root', '/mnt/music/Master_Library')
SICH = _arg('--sicherung', '/var/lib/beets/ape-entfernt-20261005')
def md5(p): return subprocess.run(['ffmpeg','-v','error','-i',p,'-map','0:a','-f','md5','-'],capture_output=True,text=True).stdout.strip()
ziele=[]
for w,_,fs in os.walk(ROOT):
    for f in fs:
        if f.lower().endswith('.mp3'):
            p=os.path.join(w,f)
            try: APEv2(p); ziele.append(p)
            except APENoHeaderError: pass
            except Exception as e: print('LESEFEHLER', p, e)
print('Dateien mit APE-Block:', len(ziele))
if not AUS: sys.exit(0)
os.makedirs(SICH, exist_ok=True)
ok=fehler=0; log=open(SICH+'/protokoll.tsv','w',encoding='utf-8')
for i,p in enumerate(ziele):
    try:
        vorher=md5(p)
        with open(p,'rb') as fh: alt=fh.read()
        delete(p)
        with open(p,'rb') as fh: neu=fh.read()
        n=0; m=min(len(alt),len(neu))
        while n<m and alt[n]==neu[n]: n+=1
        with open(f'{SICH}/{i:04d}.roh','wb') as fh: fh.write(alt[n:])
        with open(f'{SICH}/{i:04d}.json','w',encoding='utf-8') as fh:
            json.dump({'pfad':p,'gemeinsam':n,'sha256_vorher':hashlib.sha256(alt).hexdigest(),'sha256_nachher':hashlib.sha256(neu).hexdigest()},fh)
        nachher=md5(p)
        if not vorher or vorher!=nachher: raise RuntimeError('TON VERAENDERT %s %s' % (vorher,nachher))
        log.write(f'{i:04d}\t{p}\tOK\n'); ok+=1
    except Exception as e:
        log.write(f'{i:04d}\t{p}\tFEHLER {e}\n'); fehler+=1; print('FEHLER', p, e)
print('entfernt:', ok, '| Fehler:', fehler)

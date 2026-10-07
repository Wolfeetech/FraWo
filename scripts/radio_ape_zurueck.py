# Gegenstueck zu radio_ape_entfernen.py (#1908/#1915): stellt Dateien byte-genau wieder her.
# Aufruf: python3 radio_ape_zurueck.py <sicherungsordner> [<nr> ...] [--ausfuehren]   (ohne --ausfuehren nur Pruefung)
import sys, os, json, hashlib
AUS = '--ausfuehren' in sys.argv
args = [a for a in sys.argv[1:] if a != '--ausfuehren']
SICH, nummern = args[0], args[1:]
if not nummern:
    nummern = sorted(f[:-5] for f in os.listdir(SICH) if f.endswith('.json'))
ok = fehler = 0
for nr in nummern:
    meta = json.load(open(f'{SICH}/{nr}.json', encoding='utf-8'))
    roh = open(f'{SICH}/{nr}.roh', 'rb').read()
    jetzt = open(meta['pfad'], 'rb').read()
    if hashlib.sha256(jetzt).hexdigest() != meta['sha256_nachher']:
        print('UEBERSPRUNGEN (Datei seither veraendert)', nr, meta['pfad']); fehler += 1; continue
    wieder = jetzt[:meta['gemeinsam']] + roh
    if hashlib.sha256(wieder).hexdigest() != meta['sha256_vorher']:
        print('FEHLER (Pruefsumme passt nicht)', nr, meta['pfad']); fehler += 1; continue
    if AUS:
        open(meta['pfad'], 'wb').write(wieder)
    ok += 1
print(('wiederhergestellt' if AUS else 'wiederherstellbar') + ':', ok, '| Fehler/uebersprungen:', fehler)

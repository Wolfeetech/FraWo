#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""FraWo — Cover-Probe: Werbe-Cover in eingebetteten Bildern finden (Odoo #1471).

Wolf, 01.10.2026: Werbe-Cover wie eingebettete Banner "www.djsoundtop.com
Exclusive" sollen aus den Musikdateien raus und durch das echte Release-
Cover ersetzt werden. Gibt es keins, bleibt das Bild leer.

NUR EIN PROBELAUF: Dieses Skript liest ausschließlich. Es schreibt NIE in
Musikdateien oder die beets-Datenbank -- auch nicht mit --anwenden o. ä.,
das gibt es hier absichtlich nicht.

ERKENNUNG -- Weg und Begründung
================================
Die Text-Tags der Bibliothek wurden am 29./30.09. geputzt
(musikverwaltung/tags-putzen.py), eingebettete Bilder dabei bewusst
verschont -- die ursprüngliche Werbequelle steht also nicht mehr im Tag,
nur noch im Bild selbst.

Verlässlichster Weg ohne Risiko an den Dateien: ein Bild, das BYTE-
IDENTISCH (SHA-256 der Bilddaten) bei vielen unterschiedlichen Alben
eingebettet ist, ist so gut wie sicher ein Werbe- oder Platzhalter-Cover --
ein echtes Artist-Cover wiederholt sich nicht über fremde Veröffentlichungen
hinweg. Das ist die PRIMÄRE, harte Erkennung (Schwelle: >= SCHWELLE_ALBEN
verschiedene Alben mit identischem Bild).

Zusatz: tesseract-ocr (+ tesseract-ocr-eng, am 01.10. per apt auf CT120
installiert -- 6 kleine Pakete/~20 MB, keine Config-Änderung, nur lesende
Diagnose) bestätigt die häufigsten/verdächtigsten Bilder per Texterkennung
gegen bekannte Werbequellen (djsoundtop, electronicfresh, musicdjs.club,
fordjonly, muzhousebeat, iptorrents, minimalfreaks.co, djpoolrecords) und
allgemeine Werbephrasen. OCR läuft NUR auf die paar Dutzend *unter-
schiedlichen* verdächtigen Bilder (nicht auf alle 10.669 Dateien) -- das
ist schnell genug und bestätigt den Verdacht, ersetzt ihn aber nicht: ohne
OCR-Treffer bleibt ein häufiges Bild ein unbestätigter Verdacht im CSV,
nicht automatisch "Werbe-Cover".

ABLAUF
======
    cover_probe.py erkennen [--limit N] [--ohne-ocr] [--schwelle N]
        Voller Lauf über die Bibliothek (lesen, Hash + optional OCR),
        schreibt kandidaten.csv. --limit nur für einen schnellen Testlauf.

    cover_probe.py ersatzsuche [--anzahl 30]
        Feste Stichprobe aus kandidaten.csv gegen Beatport (zuerst) und
        Discogs (Rückfall) -- genau wie beatport_abgleich/discogs_abgleich
        es für den Genre-Abgleich schon tun (gebremst, Login aus
        /etc/frawo/*.env). Schreibt die gefundene Ersatzquelle (Cover-URL)
        oder 'keins' in dieselbe CSV zurück.

    cover_probe.py beispiele [--anzahl 5]
        Speichert Originalbild + gefundenes Ersatzbild für n Treffer aus
        der Stichprobe als Dateien unter BEISPIEL_DIR.

Spec-Hintergrund: DOCS/superpowers/specs/2026-09-30-frawo-funk-musikredaktion-design.md
Odoo: Task #1471 "💿 Radio-Cover: echte Release-Bilder statt Sampler-Cover"
"""
import argparse
import base64
import collections
import csv
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile

DB = '/var/lib/beets/musik.db'
AUSGABE_DIR = '/root/musikredaktion-cover'
CSV_PFAD = os.path.join(AUSGABE_DIR, 'kandidaten.csv')
BEISPIEL_DIR = os.path.join(AUSGABE_DIR, 'beispiele')

SCHWELLE_ALBEN = 5      # Bild bei >= so vielen unterschiedlichen Alben identisch -> harter Kandidat
OCR_SCHWELLE = 3        # ab so vielen Alben lohnt sich OCR zur Bestätigung (Kosten sparen)

WERBEQUELLEN = ('djsoundtop', 'electronicfresh', 'musicdjs.club', 'fordjonly',
                'muzhousebeat', 'iptorrents', 'minimalfreaks.co', 'djpoolrecords')
WERBEWOERTER = ('exclusive', 'promo only', 'free download', 'www.')

CSV_FELDER = ['pfad', 'hash', 'grund', 'albenzahl', 'ocr_bestaetigt', 'artist', 'title',
              'album', 'breite', 'hoehe', 'groesse_bytes', 'mime', 'ersatzquelle']


# ---------------------------------------------------------------------------
# Reine Logik -- kein Datei-/Netzwerkzugriff, deshalb ohne beets/mutagen/
# requests testbar (Review-Vorgabe: Kernentscheidung separat von I/O).
# ---------------------------------------------------------------------------

def gruppieren(eintraege):
    """eintraege: Liste von Dicts mit 'hash' (str oder None/leer) und 'album'.
    -> {hash: {'anzahl_dateien': n, 'alben': {album, ...}}}, nur für Einträge
    mit Bild. Mehrere Titel desselben Albums zählen für die Albenzahl nur
    einmal -- sonst würde ein Album mit 12 Titeln allein schon die Schwelle
    reißen, ohne dass das Bild album-übergreifend vorkommt."""
    gruppen = {}
    for e in eintraege:
        h = e.get('hash')
        if not h:
            continue
        g = gruppen.setdefault(h, {'anzahl_dateien': 0, 'alben': set()})
        g['anzahl_dateien'] += 1
        g['alben'].add(e.get('album') or '(unbekannt)')
    return gruppen


def ocr_verdaechtig(text):
    """True, wenn der erkannte Text auf eine bekannte Werbequelle oder eine
    typische Werbephrase hindeutet."""
    t = (text or '').lower()
    return any(q in t for q in WERBEQUELLEN) or any(w in t for w in WERBEWOERTER)


def kandidaten_bestimmen(eintraege, schwelle_alben=SCHWELLE_ALBEN, ocr=None):
    """Reine Entscheidungslogik, kein I/O.

    eintraege: Liste von Dicts {item_id, pfad, artist, album, title, hash,
               mime, groesse_bytes, breite, hoehe} -- 'hash' ist leer/None, wenn
               kein Bild eingebettet ist (solche Einträge sind NIE Kandidat:
               ohne Bild gibt es nichts zu entfernen).
    ocr:       optional {hash: text} mit bereits erkanntem OCR-Text je Hash.

    -> Liste von Kandidaten-Dicts (Kopie von eintraege-Dict + 'albenzahl',
       'ocr_bestaetigt', 'grund'), nur für Dateien mit Bild UND Verdacht.
       Der Haupt-Grund ist immer die Häufigkeit über Alben -- ein reiner
       OCR-Treffer ohne Häufigkeits-Verdacht reicht NICHT (Einzelbilder
       mit zufällig ähnlichem Text sollen nicht gelöscht werden)."""
    gruppen = gruppieren(eintraege)
    ocr = ocr or {}
    kandidaten = []
    for e in eintraege:
        h = e.get('hash')
        if not h:
            continue
        g = gruppen[h]
        albenzahl = len(g['alben'])
        if albenzahl < schwelle_alben:
            continue
        text = ocr.get(h, '')
        bestaetigt = ocr_verdaechtig(text)
        if bestaetigt:
            grund = "Werbe-Cover bestätigt per OCR (%r), gleiches Bild bei %d Alben" % (text.strip()[:80], albenzahl)
        else:
            grund = "gleiches Bild bei %d verschiedenen Alben (Verdacht: Werbe-/Platzhalter-Cover, ohne OCR-Bestätigung)" % albenzahl
        kandidaten.append(dict(e, albenzahl=albenzahl, ocr_bestaetigt=bestaetigt, grund=grund))
    return kandidaten


def pfade_entdoppeln(eintraege):
    """Die beets-DB hat 204 Pfade mit je zwei Datensatz-Zeilen (bekannter,
    separater Altbestand -- vgl. musikverwaltung/doubletten-quarantaene.sh;
    hier NICHT bereinigt, nur für diese Auswertung neutralisiert). Ohne
    Entdopplung würde ein einziges Bild in zwei DB-Zeilen wie zwei Dateien
    über zwei 'Alben' zählen und die Häufigkeits-Schwelle künstlich
    erreichen. Pro Pfad bleibt eine Zeile übrig -- die mit dem volleren
    Album-Feld, sonst die erste. Reihenfolge der Eingabe bleibt erhalten."""
    gewaehlt = {}
    reihenfolge = []
    for e in eintraege:
        p = e.get('pfad')
        bisher = gewaehlt.get(p)
        if bisher is None:
            gewaehlt[p] = e
            reihenfolge.append(p)
        elif not (bisher.get('album') or '').strip() and (e.get('album') or '').strip():
            gewaehlt[p] = e
    return [gewaehlt[p] for p in reihenfolge]


def bild_url_suchen(objekt, tiefe=0):
    """Sucht rekursiv (flach begrenzt) in einer API-Antwort (verschachtelte
    dicts/lists aus JSON) nach einer Bild-URL -- robust gegen leicht
    unterschiedliche Feldnamen zwischen Beatport- und Discogs-Antworten,
    ohne deren genaues Schema fest zu verdrahten. Reine Logik: bekommt
    bereits geparstes JSON, macht selbst keinen Netzwerkzugriff."""
    if tiefe > 4 or objekt is None:
        return ''
    if isinstance(objekt, str):
        kandidat = objekt.replace('{w}', '500').replace('{h}', '500').replace('{x}', '500').replace('{y}', '500')
        return kandidat if re.search(r'\.(jpe?g|png)(\?|$)', kandidat, re.I) else ''
    if isinstance(objekt, dict):
        for schl in ('cover_image', 'thumb', 'image', 'artwork', 'picture', 'dynamic_uri', 'uri'):
            if schl in objekt:
                treffer = bild_url_suchen(objekt[schl], tiefe + 1)
                if treffer:
                    return treffer
        for v in objekt.values():
            treffer = bild_url_suchen(v, tiefe + 1)
            if treffer:
                return treffer
    elif isinstance(objekt, (list, tuple)):
        for v in objekt:
            treffer = bild_url_suchen(v, tiefe + 1)
            if treffer:
                return treffer
    return ''


# ---------------------------------------------------------------------------
# I/O -- liest Dateien/Netzwerk, schreibt NIE in Musikdateien oder die DB.
# ---------------------------------------------------------------------------

def eingebettetes_bild(pfad):
    """(bytes, mime, breite, hoehe) des ersten eingebetteten Bilds einer
    Musikdatei, sonst None. Deckt ID3 (APIC: MP3/WAV/AIFF), MP4/M4A (covr),
    FLAC (.pictures) und Vorbis/Opus (metadata_block_picture) ab -- dieselben
    Formate, die tags-putzen.py in NIE_FRAME ausdrücklich schützt."""
    import mutagen
    import mutagen.flac
    try:
        f = mutagen.File(pfad)
    except Exception:
        return None
    if f is None:
        return None
    pics = getattr(f, 'pictures', None)
    if pics:
        p = pics[0]
        return p.data, p.mime, (p.width or None), (p.height or None)
    tags = f.tags
    if tags is None:
        return None
    for key in tags.keys():
        if str(key).startswith('APIC'):
            frame = tags[key]
            return frame.data, frame.mime, None, None
    if 'covr' in tags and tags['covr']:
        img = tags['covr'][0]
        mime = 'image/png' if getattr(img, 'imageformat', None) == getattr(img, 'FORMAT_PNG', -1) else 'image/jpeg'
        return bytes(img), mime, None, None
    for key in ('metadata_block_picture', 'METADATA_BLOCK_PICTURE'):
        if key in tags:
            try:
                block = mutagen.flac.Picture(base64.b64decode(tags[key][0]))
                return block.data, block.mime, (block.width or None), (block.height or None)
            except Exception:
                pass
    return None


def bild_hash(daten):
    return hashlib.sha256(daten).hexdigest()


def bild_abmessungen(daten):
    try:
        from PIL import Image
        with Image.open(io.BytesIO(daten)) as img:
            return img.size
    except Exception:
        return None, None


def ocr_lesen(daten, mime='', tesseract='tesseract'):
    """Texterkennung über die tesseract-CLI (keine Python-Bindung nötig,
    keine zusätzliche Abhängigkeit). Leerer String bei jedem Fehler -- OCR
    ist nur eine Zusatzbestätigung, kein hartes Kriterium."""
    endung = '.png' if 'png' in (mime or '') else '.jpg'
    try:
        with tempfile.NamedTemporaryFile(suffix=endung, delete=False) as tmp:
            tmp.write(daten)
            tmp_pfad = tmp.name
        try:
            r = subprocess.run([tesseract, tmp_pfad, 'stdout'],
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=20)
            return r.stdout.decode('utf-8', 'ignore')
        finally:
            os.unlink(tmp_pfad)
    except Exception:
        return ''


def bibliothek_scannen(db_pfad=DB, limit=None, fortschritt=None):
    """Liest jeden Bibliothekseintrag, extrahiert ggf. das eingebettete
    Bild. Hält KEINE Bilddaten im Speicher (10.669 Dateien x bis zu
    mehreren 100 KB wäre auf dem 2-GB-Container zu viel) -- nur Hash,
    Maße, Größe. -> Liste von Dicts {item_id, pfad, artist, album, title,
    hash, mime, groesse_bytes, breite, hoehe}; hash ist '' ohne eingebettetes Bild."""
    import beets.library
    lib = beets.library.Library(db_pfad)
    items = list(lib.items())
    if limit:
        items = items[:limit]
    eintraege = []
    for n, it in enumerate(items, 1):
        pfad = it.path
        pfad = pfad.decode('utf-8', 'surrogateescape') if isinstance(pfad, bytes) else pfad
        basis = {'item_id': it.id, 'pfad': pfad, 'artist': it.artist or '',
                 'album': it.album or '', 'title': it.title or ''}
        bild = eingebettetes_bild(pfad) if os.path.exists(pfad) else None
        if bild:
            daten, mime, breite, hoehe = bild
            if breite is None:
                breite, hoehe = bild_abmessungen(daten)
            eintraege.append(dict(basis, hash=bild_hash(daten), mime=mime or '',
                                   groesse_bytes=len(daten), breite=breite, hoehe=hoehe))
        else:
            eintraege.append(dict(basis, hash='', mime='', groesse_bytes=0, breite=None, hoehe=None))
        if fortschritt and (n % 500 == 0 or n == len(items)):
            fortschritt(n, len(items))
    entdoppelt = pfade_entdoppeln(eintraege)
    if len(entdoppelt) != len(eintraege):
        print('Bekannte DB-Dubletten (gleicher Pfad, zwei Zeilen) entdoppelt: %d'
              % (len(eintraege) - len(entdoppelt)))
    return entdoppelt


def ocr_anreichern(eintraege, kandidaten_hashes, tesseract='tesseract'):
    """Liest je verdächtigem Hash EINMAL eine Beispieldatei erneut (die
    Rohdaten wurden beim Scan nicht behalten) und OCRt deren Bild.
    -> {hash: text}"""
    beispiel = {}
    for e in eintraege:
        h = e.get('hash')
        if h in kandidaten_hashes and h not in beispiel:
            beispiel[h] = e['pfad']
    ergebnis = {}
    for h, pfad in beispiel.items():
        bild = eingebettetes_bild(pfad)
        if bild:
            daten, mime, _, _ = bild
            ergebnis[h] = ocr_lesen(daten, mime, tesseract)
    return ergebnis


def env_lesen(pfad):
    with open(pfad, encoding='utf-8') as f:
        return dict(z.strip().split('=', 1) for z in f if '=' in z and not z.startswith('#'))


def csv_schreiben(zeilen, pfad=CSV_PFAD):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=CSV_FELDER, delimiter=';', extrasaction='ignore')
        w.writeheader()
        for z in zeilen:
            w.writerow({feld: z.get(feld, '') for feld in CSV_FELDER})


def csv_lesen(pfad=CSV_PFAD):
    with open(pfad, encoding='utf-8') as f:
        return list(csv.DictReader(f, delimiter=';'))


def ersatz_suchen(zeilen, anzahl=30, seed=20260930):
    """zeilen: CSV-Zeilen (dicts, wie von csv_lesen()). Wählt eine feste,
    reproduzierbare Stichprobe ohne bereits gesetzte Ersatzquelle (so bleibt
    ein erneuter Lauf billig und erweitert statt doppelt zu suchen), sucht
    über Beatport (zuerst) und Discogs (Rückfall) -- gebremst wie die
    vorhandenen Module es selbst schon tun (Pausen/Ratelimit in
    beatport_abgleich.suche / discogs_abgleich.DiscogsClient).

    Vereinfachung für den Probelauf: Die Bild-URL wird aus der GESAMTEN,
    als 'belegt' bewerteten Treffermenge gezogen (bild_url_suchen), nicht
    zwingend exakt aus dem einen Datensatz, den bewerte() für Genre/Stil
    gewählt hat. Für den echten Lauf denselben Datensatz verwenden.

    -> (aktualisierte Zeilen, Trefferzahl)"""
    import random
    sys.path.insert(0, '/opt/musikredaktion')
    import beatport_abgleich as bp
    import discogs_abgleich as dc

    offen = [z for z in zeilen if not z.get('ersatzquelle')]
    random.seed(seed)
    stichprobe = random.sample(offen, min(anzahl, len(offen)))
    stichprobe_pfade = {z['pfad'] for z in stichprobe}

    b = env_lesen('/etc/frawo/beatport.env')
    s = bp.anmelden(b['BEATPORT_USER'], b['BEATPORT_PASS'])
    c = dc.DiscogsClient(env_lesen('/etc/frawo/discogs.env')['DISCOGS_TOKEN'])

    treffer = 0
    for z in zeilen:
        if z['pfad'] not in stichprobe_pfade:
            continue
        titel = {'artist': z.get('artist', ''), 'title': z.get('title', '')}
        a, t = dc.suchbegriffe(titel)
        url = ''
        if a and t:
            bp_treffer = bp.suche(s, a, t)
            r = bp.bewerte(titel, bp_treffer)
            if r['status'] == 'belegt':
                url = bild_url_suchen(bp_treffer)
            if not url:
                dc_treffer = c.suche(a, t)
                r2 = dc.bewerte(titel, dc_treffer)
                if r2['status'] == 'belegt':
                    url = bild_url_suchen(dc_treffer)
        z['ersatzquelle'] = url or 'keins'
        if url:
            treffer += 1
    return zeilen, treffer


def beispiele_speichern(zeilen, ziel_dir=BEISPIEL_DIR, anzahl=5):
    """Speichert Original- und Ersatzbild für die ersten `anzahl` Treffer
    mit gefundener Ersatzquelle. Liest/lädt nur, schreibt ausschließlich in
    ziel_dir -- keine Musikdatei wird angefasst."""
    import requests
    os.makedirs(ziel_dir, exist_ok=True)
    treffer = [z for z in zeilen if z.get('ersatzquelle') and z['ersatzquelle'] != 'keins']
    gespeichert = []
    for n, z in enumerate(treffer[:anzahl], 1):
        bild = eingebettetes_bild(z['pfad'])
        if not bild:
            continue
        daten, mime, _, _ = bild
        alt_pfad = os.path.join(ziel_dir, '%02d-original%s' % (n, '.png' if 'png' in (mime or '') else '.jpg'))
        with open(alt_pfad, 'wb') as f:
            f.write(daten)
        r = requests.get(z['ersatzquelle'], timeout=30)
        r.raise_for_status()
        neu_pfad = os.path.join(ziel_dir, '%02d-ersatz%s' % (n, '.png' if 'png' in r.headers.get('Content-Type', '') else '.jpg'))
        with open(neu_pfad, 'wb') as f:
            f.write(r.content)
        info_pfad = os.path.join(ziel_dir, '%02d-info.txt' % n)
        with open(info_pfad, 'w', encoding='utf-8') as f:
            f.write('Pfad: %s\nArtist: %s\nTitel: %s\nGrund: %s\nErsatzquelle: %s\n'
                    % (z['pfad'], z.get('artist', ''), z.get('title', ''), z.get('grund', ''), z['ersatzquelle']))
        gespeichert.append((alt_pfad, neu_pfad, info_pfad))
    return gespeichert


# ---------------------------------------------------------------------------
# Subkommandos
# ---------------------------------------------------------------------------

def _fortschritt(n, gesamt):
    print('  %d / %d gelesen' % (n, gesamt), flush=True)


def tat_erkennen(args):
    print('Scanne Bibliothek (%s)%s ...' % (DB, ' [limit=%d]' % args.limit if args.limit else ''))
    eintraege = bibliothek_scannen(limit=args.limit, fortschritt=_fortschritt)
    mit_bild = [e for e in eintraege if e['hash']]
    print('Dateien gesamt: %d | mit eingebettetem Bild: %d | ohne Bild: %d'
          % (len(eintraege), len(mit_bild), len(eintraege) - len(mit_bild)))

    ocr_text = {}
    if not args.ohne_ocr:
        gruppen = gruppieren(eintraege)
        ocr_hashes = {h for h, g in gruppen.items() if len(g['alben']) >= OCR_SCHWELLE}
        print('OCR auf %d unterschiedliche verdächtige Bilder (ab %d Alben) ...' % (len(ocr_hashes), OCR_SCHWELLE))
        ocr_text = ocr_anreichern(eintraege, ocr_hashes)

    kandidaten = kandidaten_bestimmen(eintraege, schwelle_alben=args.schwelle, ocr=ocr_text)
    csv_schreiben(kandidaten)
    print('Kandidaten (>= %d Alben, Bild identisch): %d -> %s' % (args.schwelle, len(kandidaten), CSV_PFAD))
    bestaetigt = sum(1 for k in kandidaten if k['ocr_bestaetigt'])
    print('  davon per OCR bestätigt: %d | nur Häufigkeits-Verdacht: %d' % (bestaetigt, len(kandidaten) - bestaetigt))

    nach_hash = collections.Counter(k['hash'] for k in kandidaten)
    print('Häufigste Werbe-/Verdachts-Hashes:')
    for h, n in nach_hash.most_common(10):
        beispiel = next(k for k in kandidaten if k['hash'] == h)
        print('  %s...  %3dx Dateien, %d Alben  Beispiel: %s%s'
              % (h[:12], n, beispiel['albenzahl'], beispiel['pfad'],
                 '  [OCR bestätigt]' if beispiel['ocr_bestaetigt'] else ''))
    return 0


def tat_ersatzsuche(args):
    zeilen = csv_lesen()
    zeilen, treffer = ersatz_suchen(zeilen, anzahl=args.anzahl)
    csv_schreiben(zeilen)
    gesucht = min(args.anzahl, len(zeilen))
    print('Stichprobe: %d Kandidaten geprüft, echtes Ersatzcover gefunden: %d (%.0f%%)'
          % (gesucht, treffer, 100.0 * treffer / gesucht if gesucht else 0))
    print('CSV aktualisiert: %s' % CSV_PFAD)
    return 0


def tat_beispiele(args):
    zeilen = csv_lesen()
    gespeichert = beispiele_speichern(zeilen, anzahl=args.anzahl)
    print('Beispiele gespeichert (%d Paare) unter %s:' % (len(gespeichert), BEISPIEL_DIR))
    for alt, neu, info in gespeichert:
        print('  %s  +  %s  (%s)' % (alt, neu, info))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='kommando', required=True)

    p1 = sub.add_parser('erkennen', help='voller Lauf über die Bibliothek, schreibt kandidaten.csv')
    p1.add_argument('--limit', type=int, default=None, help='nur die ersten N Bibliothekseinträge (Testlauf)')
    p1.add_argument('--schwelle', type=int, default=SCHWELLE_ALBEN, help='ab so vielen Alben gilt ein Bild als Kandidat')
    p1.add_argument('--ohne-ocr', action='store_true', help='OCR-Bestätigung überspringen (schneller, weniger aussagekräftig)')
    p1.set_defaults(func=tat_erkennen)

    p2 = sub.add_parser('ersatzsuche', help='Stichprobe aus kandidaten.csv gegen Beatport/Discogs')
    p2.add_argument('--anzahl', type=int, default=30)
    p2.set_defaults(func=tat_ersatzsuche)

    p3 = sub.add_parser('beispiele', help='Original- und Ersatzbild für n Treffer als Dateien speichern')
    p3.add_argument('--anzahl', type=int, default=5)
    p3.set_defaults(func=tat_beispiele)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())

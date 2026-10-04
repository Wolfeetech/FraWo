#!/usr/bin/env python3
"""Titel und Kuenstler sendertauglich putzen (Odoo #1915, Wolf 04.10.2026).

Wolf: "Tracknamen auf jeden Fall clean und nach Vorgaben fuer Radiosender".
Konvention: "Kuenstler - Titel (Version)". Die Datei ist die Quelle: AzuraCast
uebernimmt beim Neueinlesen jeden vorhandenen Titel-Tag, also wird hier in den
Dateien geputzt. Regeln und Beispiele: test_radio_titel_putzen.py.

Was NICHT automatisch passiert (Nacharbeitsliste): Kauderwelsch-Codes wie
"$R8EZCC2", leerer Titel oder leerer Kuenstler - dort wuerde jede Regel raten.

Ohne --ausfuehren: Probelauf, schreibt nur die Vorher/Nachher-Liste.
Mit --ausfuehren: alte Werte stehen vorher in <sicherung>/aenderungen.tsv (Rueckweg).
"""
import argparse, os, re, sys

ENDUNGEN = ('.mp3', '.flac', '.m4a', '.aac', '.ogg', '.aiff', '.aif')

ORIGINAL = re.compile(r'\s*\((?:Original|Orginal|Original Version)(?: Mix)?\)', re.I)
BPM_ENDE = re.compile(r'(?<=\))\s+\d{2,3}$')
TRACKNR = re.compile(r'^(?:\d{1,3}\s*[-.]\s+|0\d\s+)')
ENDUNG = re.compile(r'\.(?:mp3|flac|wav|aiff?|m4a)$', re.I)
RIP = re.compile(r'\s*\[(?:vinyl[ _-]?rip|free download|320|320kbps|flac|web|qrip|promo|www[^\]]*)\]', re.I)
FEAT = re.compile(r'\s+(?:feat\.?|ft\.?|featuring)\s+(.+?)(?=\s*\(|$)', re.I)
VERSION_WORT = re.compile(r'\b(remix|mix|edit|dub|version|rework|bootleg|instrumental)\b', re.I)
# Kauderwelsch: Download-Codes ($R8EZCC2, Buchstaben+Ziffern gemischt), "@@"-Reste,
# lange Ziffernfolgen (Katalog-/Datei-IDs). Reine Woerter wie "ALIVE" sind kein Code.
CODE = re.compile(r'^\$[A-Z0-9]{5,}$|^(?=.*\d)(?=.*[A-Z])[A-Z0-9]{6,}$|@@|\d{6,}')


def _version_gross(m):
    inhalt = m.group(1)
    if VERSION_WORT.search(inhalt):
        # Jedes klein geschriebene Wort gross anfangen: "(club version)" -> "(Club Version)"
        inhalt = re.sub(r'(?<![\w\'’])([a-zäöü])', lambda b: b.group(1).upper(), inhalt)
    return '(%s)' % inhalt


def putze_titel(titel, kuenstler=''):
    # Bis zum festen Punkt putzen: eine Regel kann die naechste erst freilegen
    # ("00 - Kuenstler - Titel": erst Tracknummer weg, dann Kuenstler-Praefix).
    t = titel
    for _ in range(4):
        neu = _putze_einmal(t, kuenstler)
        if neu == t:
            break
        t = neu
    return t


def _putze_einmal(titel, kuenstler=''):
    t = (titel or '').strip()
    if not t:
        return t
    # Mehrfachwert "A; B" (Tag mit mehreren Werten): erster Wert gilt
    if ';' in t:
        t = t.split(';', 1)[0].strip()
    t = ENDUNG.sub('', t)
    if '_' in t and ' ' not in t.strip('_'):
        t = t.replace('_', ' ')
    t = RIP.sub('', t)
    t = BPM_ENDE.sub('', t)
    t = TRACKNR.sub('', t)
    if kuenstler:
        praefix = kuenstler.strip() + ' - '
        if t.lower().startswith(praefix.lower()):
            t = t[len(praefix):]
    t = ORIGINAL.sub('', t)
    # feat. aus dem Titel in eine eigene Klammer direkt hinter den Titel
    m = FEAT.search(t)
    if m and not re.search(r'\(feat\.', t, re.I):
        gast = m.group(1).strip()
        rest = (t[:m.start()] + t[m.end():]).strip()
        kern, sep, versionen = rest.partition(' (')
        t = '%s (feat. %s)%s' % (kern.strip(), gast, (' (' + versionen) if sep else '')
    t = re.sub(r'\(([^)]*)\)', _version_gross, t)
    t = re.sub(r'\s{2,}', ' ', t).strip(' -')
    return t


def putze_kuenstler(kuenstler):
    k = (kuenstler or '').strip()
    if ';' in k:
        # Mehrfachwert-Tag: erster Wert ist der Anzeige-Kuenstler ("A & B; A; B")
        k = k.split(';', 1)[0].strip()
    return re.sub(r'\s{2,}', ' ', k)


def braucht_nacharbeit(titel, kuenstler):
    t = (titel or '').strip()
    return ((not t) or (not (kuenstler or '').strip()) or bool(CODE.search(t))
            or ' - ' in putze_titel(t, putze_kuenstler(kuenstler)))


def aus_dateiname(name, kuenstler, titel):
    """Fehlenden Titel/Kuenstler aus "Kuenstler - Titel" im Dateinamen ableiten.

    Nur eindeutige Faelle: genau ein " - ", keine Tracknummer vorne. Fehlt nur
    der Titel, muss der Kuenstler im Dateinamen dem Kuenstler-Tag entsprechen.
    Gibt (kuenstler, titel) oder None zurueck.
    """
    k, t = (kuenstler or '').strip(), (titel or '').strip()
    if k and t:
        return None
    teile = name.split(' - ')
    if len(teile) != 2 or TRACKNR.match(name) or re.match(r'^\d', name):
        return None
    dk, dt = teile[0].strip(), teile[1].strip()
    if not dk or len(dt) < 2:
        return None
    if dk.lower() in ('various artists', 'various', 'va', 'v.a.', 'unknown artist', 'unknown'):
        return None  # Sammel-Platzhalter, kein echter Kuenstler (7 Faelle am 04.10.)
    if k and dk.lower() != k.lower():
        return None
    return (k or dk, t or dt)


def ist_kauderwelsch(titel):
    return bool(CODE.search((titel or '').strip()))


def main():
    import mutagen
    ap = argparse.ArgumentParser()
    ap.add_argument('--root', required=True)
    ap.add_argument('--sicherung', required=True)
    ap.add_argument('--ausfuehren', action='store_true')
    a = ap.parse_args()
    os.makedirs(a.sicherung, exist_ok=True)

    aenderungen = open(os.path.join(a.sicherung, 'aenderungen.tsv' if a.ausfuehren else 'probe.tsv'), 'w')
    nacharbeit = open(os.path.join(a.sicherung, 'nacharbeit.tsv'), 'w')
    n_geaendert = n_nach = n_fehler = 0
    for wurzel, _, dateien in os.walk(a.root):
        for name in sorted(dateien):
            if not name.lower().endswith(ENDUNGEN):
                continue
            pfad = os.path.join(wurzel, name)
            try:
                f = mutagen.File(pfad, easy=True)
                if f is None or f.tags is None:
                    continue
                titel = (f.get('title') or [''])[0]
                kuenstler = (f.get('artist') or [''])[0]
                # Mehrere Werte im Tag ("Boom" + "Boom (Original Mix)"): AzuraCast zeigt sie mit
                # "; " verbunden an. Erster Wert gilt, also immer auf genau einen Wert zurueckschreiben.
                mehrfach = len(f.get('title') or []) > 1 or len(f.get('artist') or []) > 1
                # Fehlt Titel oder Kuenstler: eindeutiges "Kuenstler - Titel" im Dateinamen nutzen
                quelle_k, quelle_t = (aus_dateiname(os.path.splitext(name)[0], kuenstler, titel)
                                      or (kuenstler, titel))
                if braucht_nacharbeit(quelle_t, quelle_k):
                    nacharbeit.write('%s\t%s\t%s\n' % (pfad, kuenstler, titel))
                    n_nach += 1
                if ist_kauderwelsch(quelle_t):
                    continue  # steht auf der Nacharbeitsliste, keine Regel raten lassen
                neu_k = putze_kuenstler(quelle_k)
                neu_t = putze_titel(quelle_t, neu_k)
                if ((neu_t, neu_k) == (titel, kuenstler) and not mehrfach) or not neu_t:
                    continue
                aenderungen.write('%s\t%s\t%s\t%s\t%s\n' % (pfad, kuenstler, titel, neu_k, neu_t))
                n_geaendert += 1
                if a.ausfuehren:
                    f['title'] = neu_t
                    if neu_k:
                        f['artist'] = neu_k
                    f.save()
            except Exception as e:
                n_fehler += 1
                nacharbeit.write('%s\tFEHLER\t%s\n' % (pfad, e))
    aenderungen.close()
    nacharbeit.close()
    print('Modus: %s, geaendert: %d, Nacharbeit: %d, Fehler: %d'
          % ('AUSFUEHREN' if a.ausfuehren else 'PROBE', n_geaendert, n_nach, n_fehler))
    return 1 if n_fehler else 0


if __name__ == '__main__':
    sys.exit(main())

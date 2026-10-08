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
# Download-Portale im Titel ("www.djsoundtop.com", "heydj.pro"): nur ganze Domain-Woerter
WEBADRESSE = re.compile(r'\s*\b(?:https?://)?(?:www\.)?[a-z0-9-]+\.(?:com|net|org|pro|ru|pw|to|cc|info|biz)\b/?', re.I)
VERSION_WORT = re.compile(r'\b(remix|mix|edit|dub|version|rework|bootleg|instrumental)\b', re.I)
# Kauderwelsch: Download-Codes ($R8EZCC2, Buchstaben+Ziffern gemischt), "@@"-Reste,
# lange Ziffernfolgen (Katalog-/Datei-IDs). Reine Woerter wie "ALIVE" sind kein Code.
CODE = re.compile(r'^\$[A-Z0-9]{5,}$|^(?=.*\d)(?=.*[A-Z])[A-Z0-9]{6,}$|@@|\d{6,}')
# Reine Zahl im Kuenstlerfeld = Tracknummer aus einem Sampler-Rip.
NUR_ZAHL = re.compile(r'^\d{1,3}$')


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
    t = WEBADRESSE.sub('', t)
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


# Haendler-Verkaufslisten statt echter Alben ("Beatport 100 Afro House 2024 August",
# "BP Weekend Picks 2025 Week 26"). AzuraCast holt dazu per Last.fm das Beatport-Bild nach.
HAENDLER_ALBUM = re.compile(r'(?i)\b(beatport|bp weekend picks|exclusives only|traxsource|juno download|'
                            r'promo only|free download|best new hype)\b')


def putze_album(album):
    a = (album or '').strip()
    return '' if HAENDLER_ALBUM.search(a) else a


def braucht_nacharbeit(titel, kuenstler):
    t = (titel or '').strip()
    k = (kuenstler or '').strip()
    # Eine reine Zahl ist kein Kuenstler, sondern eine Tracknummer, die beim
    # Import ins falsche Feld gelaufen ist (Beatport-Sampler, 07.10.2026).
    # Ohne diese Pruefung galten 44 Titel als sendertauglich und gingen so
    # auf Sendung.
    bereinigt = putze_titel(titel, kuenstler)
    # Ein Bindestrich im Titel ist zulässig, wenn danach nur eine übliche
    # Versionsangabe folgt (z. B. "Calma - Extended" oder "Kula - Remix").
    rest_ist_version = bool(re.search(
        r'\s-\s[^-]*(?:extended|radio\s+edit|club\s+mix|deep\s+mix|remix|edit|dub|version|rework|bootleg)\b$',
        bereinigt,
        re.I,
    ))
    return ((not t) or (not k) or bool(NUR_ZAHL.match(k)) or bool(CODE.search(t))
            or (' - ' in bereinigt and not rest_ist_version))


KOMMA_OHNE_LUECKE = re.compile(r',(?=\S)')
# Letztes Feld ist nur eine Versionsangabe ("Extended", "Radio Edit", "Dub Mix")
# und gehoert damit an den Titel, nicht in ein eigenes Feld.
VERSION_ANHANG = re.compile(
    r'^(?:extended|radio\s+edit|original|instrumental|dub|club\s+mix|'
    r'[\w\s().\'&,]*\b(?:remix|mix|edit|dub|version|rework|bootleg)\b[\w\s().\'&,]*)$',
    re.I)


def entwirre_sampler(kuenstler, titel):
    """Sampler-Rips entwirren, bei denen die Tracknummer im Kuenstlerfeld landete.

    Beim Beatport-Import am 07.10.2026 kamen 44 Titel gleichzeitig so auf
    Sendung: Kuenstler = "37", Titel = "Beatport 100 Afro House 2024 August -
    Sterio T,NkOstA LED,TomyV - Uwrongo". Der einmalige Putz-Lauf hat das
    korrekt als Nacharbeit gemeldet, konnte es aber nicht aufloesen.

    Greift nur, wenn das Kuenstlerfeld eine reine Zahl ist UND der Titel
    mindestens zwei " - " enthaelt. Dann gilt: letztes Feld = Titel,
    vorletztes = Kuenstler, alles davor = Album (Sampler).
    Eine abschliessende Version ("- Extended", "- Radio Edit") bleibt am Titel.

    Gibt (kuenstler, titel, album) zurueck oder None, wenn das Muster nicht
    sicher passt -- dann bleibt der Fall Nacharbeit und wird nicht geraten.
    """
    k = (kuenstler or '').strip()
    t = (titel or '').strip()
    haendler_kuenstler = bool(HAENDLER_ALBUM.search(k))
    if haendler_kuenstler:
        # Einige Beatport-Imports setzten den Sampler-Namen direkt in ARTIST,
        # während der echte Künstler am Ende des TIT2-Feldes steht:
        # "You Got Me - Karter (Original Mix)".
        teile = [x.strip() for x in t.rsplit(' - ', 1)]
        if len(teile) != 2 or not teile[0] or not teile[1]:
            return None
        m = re.match(r'^(.*?)\s*(\([^)]*\))$', teile[1])
        neuer_kuenstler = (m.group(1) if m else teile[1]).strip()
        neuer_titel = teile[0] + (f' {m.group(2)}' if m else '')
        if not neuer_kuenstler or neuer_kuenstler.lower() == k.lower():
            return None
        return (putze_kuenstler(neuer_kuenstler), putze_titel(neuer_titel, neuer_kuenstler), k)
    if not NUR_ZAHL.match(k) or not t:
        return None

    teile = [x.strip() for x in t.split(' - ')]
    # Fuehrender Bindestrich ("- Pierre Johnson,... - Ukuphila") ist ein Rest aus
    # dem Rip, kein Trenner: das erste Feld faengt dann mit "-" an.
    if teile and teile[0].startswith('-'):
        teile[0] = teile[0].lstrip('- ').strip()
    # Ein leeres erstes Feld ist ebenfalls nur ein Rest, kein Sampler-Name.
    if teile and teile[0] == '':
        teile = teile[1:]
    sampler = ''
    if len(teile) < 2:
        return None

    # Eine abschliessende Versionsangabe gehoert zum Titel, nicht als Feld.
    if len(teile) > 2 and VERSION_ANHANG.match(teile[-1]):
        teile = teile[:-2] + [teile[-2] + ' - ' + teile[-1]]
    if len(teile) < 2:
        return None

    neuer_titel = teile[-1]
    neuer_kuenstler = teile[-2]
    if len(teile) > 2:
        sampler = ' - '.join(teile[:-2])

    if not neuer_titel or not neuer_kuenstler:
        return None
    if NUR_ZAHL.match(neuer_kuenstler):
        return None

    return (putze_kuenstler(KOMMA_OHNE_LUECKE.sub(', ', neuer_kuenstler)),
            putze_titel(neuer_titel, neuer_kuenstler),
            sampler)


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


class _AiffTags:
    """AIFF hat ID3-Tags, aber kein 'easy'-Interface: title/artist/album auf TIT2/TPE1/TALB abbilden.

    Ohne das las das Werkzeug bei AIFF 'kein Titel' und der Schreibversuch kam nicht an
    (gefunden 04.10.2026 an 'Maze DJ - Morning Magic', 31 AIFF-Dateien in der Bibliothek).
    """
    RAHMEN = {'title': 'TIT2', 'artist': 'TPE1', 'album': 'TALB'}

    def __init__(self, f):
        from mutagen import id3
        self.f = f
        self.tags = f.tags
        self._klassen = {'TIT2': id3.TIT2, 'TPE1': id3.TPE1, 'TALB': id3.TALB}

    def get(self, schluessel, vorgabe=None):
        rahmen = self.tags.get(self.RAHMEN[schluessel]) if self.tags is not None else None
        return [str(t) for t in rahmen.text] if rahmen else vorgabe

    def __setitem__(self, schluessel, wert):
        kennung = self.RAHMEN[schluessel]
        self.tags.delall(kennung)
        self.tags.add(self._klassen[kennung](encoding=3, text=[wert]))

    def __delitem__(self, schluessel):
        self.tags.delall(self.RAHMEN[schluessel])

    def save(self):
        self.f.save()


def lade_tags(pfad):
    import mutagen
    from mutagen.aiff import AIFF
    f = mutagen.File(pfad, easy=True)
    if isinstance(f, AIFF):
        if f.tags is None:
            f.add_tags()
        return _AiffTags(f)
    return f


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
    alben = open(os.path.join(a.sicherung, 'alben.tsv' if a.ausfuehren else 'alben_probe.tsv'), 'w')
    n_geaendert = n_nach = n_fehler = n_alben = 0
    for wurzel, _, dateien in os.walk(a.root):
        for name in sorted(dateien):
            if not name.lower().endswith(ENDUNGEN):
                continue
            pfad = os.path.join(wurzel, name)
            try:
                f = lade_tags(pfad)
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
                # Beatport-/Sampler-Rips: Wenn die Tracknummer im Kuenstlerfeld
                # steht, entwirren wir nur das sichere Muster. Alles andere bleibt
                # Nacharbeit und wird nicht geraten.
                sampler = entwirre_sampler(quelle_k, quelle_t)
                if sampler:
                    quelle_k, quelle_t, _sampler_album = sampler
                if braucht_nacharbeit(quelle_t, quelle_k):
                    nacharbeit.write('%s\t%s\t%s\n' % (pfad, kuenstler, titel))
                    n_nach += 1
                # Haendler-Album ("Beatport Weekend Picks ...") leeren - unabhaengig vom Titel
                album = (f.get('album') or [''])[0]
                album_weg = bool(album) and putze_album(album) == ''
                if album_weg:
                    alben.write('%s\t%s\n' % (pfad, album))
                    n_alben += 1
                titel_neu = False
                if not ist_kauderwelsch(quelle_t):  # Kauderwelsch: Nacharbeitsliste, nicht raten
                    neu_k = putze_kuenstler(quelle_k)
                    neu_t = putze_titel(quelle_t, neu_k)
                    titel_neu = bool(neu_t) and ((neu_t, neu_k) != (titel, kuenstler) or mehrfach)
                if titel_neu:
                    aenderungen.write('%s\t%s\t%s\t%s\t%s\n' % (pfad, kuenstler, titel, neu_k, neu_t))
                    n_geaendert += 1
                if a.ausfuehren and (titel_neu or album_weg):
                    if titel_neu:
                        f['title'] = neu_t
                        if neu_k:
                            f['artist'] = neu_k
                    if album_weg:
                        del f['album']
                    f.save()
            except Exception as e:
                n_fehler += 1
                nacharbeit.write('%s\tFEHLER\t%s\n' % (pfad, e))
    aenderungen.close()
    nacharbeit.close()
    alben.close()
    print('Modus: %s, geaendert: %d, Haendler-Alben geleert: %d, Nacharbeit: %d, Fehler: %d'
          % ('AUSFUEHREN' if a.ausfuehren else 'PROBE', n_geaendert, n_alben, n_nach, n_fehler))
    return 1 if n_fehler else 0


if __name__ == '__main__':
    sys.exit(main())

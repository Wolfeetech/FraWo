# -*- coding: utf-8 -*-
"""Rückschreiben der Redaktions-Urteile nach beets (CT120), Odoo #1090.

Holt `GET /radio/redaktion/export` (Header `X-Agent-Token`), ordnet jeden
Titel *eindeutig* dem beets-Katalog zu (Normalisierung wie beim
Discogs-Abgleich: `discogs_abgleich.norm` auf Artist und Titel) und schreibt
je Titel den gerundeten Mittelwert aller Energie-Urteile, die Quelle und die
Sendungen mit mindestens einem passt=0-Urteil. Rät nie: ohne eindeutigen
Katalog-Treffer wird nichts geschrieben, der Titel landet nur in der
Offen-Liste. Schreiben ausschließlich über `beets.library` (`item.store()`).

Spec: DOCS/superpowers/specs/2026-09-30-frawo-funk-musikredaktion-design.md
"""
import argparse
import collections
import csv
import datetime
import os
import shutil
import sys

import requests

from discogs_abgleich import norm

EXPORT_URL = 'https://frawo.tech/radio/redaktion/export'
ENV_DATEI = '/etc/frawo/odoo.env'
DB_PFAD = '/var/lib/beets/musik.db'
OFFEN_CSV = '/root/musikredaktion/rueckschreiben-offen.csv'


# ---------------------------------------------------------------------------
# Reine Logik — ohne beets, ohne Netzwerk, ohne Dateisystem (testbar)
# ---------------------------------------------------------------------------

def _treffer(track_id, katalog):
    """katalog: Liste von {'id', 'artist', 'title'} (einfache dicts, kein
    beets-Item — so bleibt die Zuordnung ohne beets testbar). Liefert die
    Liste der passenden item_ids (0, 1 oder mehrere)."""
    if not track_id or '|' not in track_id:
        return []
    artist_roh, titel_roh = track_id.split('|', 1)
    a, t = norm(artist_roh), norm(titel_roh)
    if not a or not t:
        return []
    return [k['id'] for k in katalog if norm(k.get('artist')) == a and norm(k.get('title')) == t]


def zuordnen(track_id, items):
    """Eindeutiger Katalog-Treffer -> item_id, sonst None (kein Treffer
    oder mehrdeutig — beide Fälle raten nicht, sondern geben None)."""
    treffer = _treffer(track_id, items)
    return treffer[0] if len(treffer) == 1 else None


def auswerten(zeilen):
    """zeilen: alle Export-Zeilen EINES track_id.
    -> {'energie': int|None, 'passt_nicht': [Sendung, ...]}
    Energie: kaufmännisch gerundeter Mittelwert aller 'energie'-Urteile
    (None, wenn keine vorliegen). passt_nicht: Sendungen, in denen
    mindestens ein 'passt'-Urteil mit wert=0 abgegeben wurde, alphabetisch
    sortiert, ohne Duplikate."""
    energie = [z['wert'] for z in zeilen if z.get('art') == 'energie']
    passt_nicht = sorted({z.get('sendung') for z in zeilen
                           if z.get('art') == 'passt' and z.get('wert') == 0 and z.get('sendung')})
    mittel = int(sum(energie) / len(energie) + 0.5) if energie else None
    return {'energie': mittel, 'passt_nicht': passt_nicht}


def plan_erstellen(export_rows, katalog):
    """Reine Planung ohne Nebenwirkungen. -> (zuordnungen, offen)
    zuordnungen: [{'item_id', 'track_id', 'energie', 'passt_nicht'}]
    offen: [{'track_id', 'grund', 'anzahl_urteile'}], grund in
    ('kein_treffer', 'mehrdeutig')."""
    nach_track = collections.defaultdict(list)
    for z in export_rows:
        nach_track[z['track_id']].append(z)
    zuordnungen, offen = [], []
    for track_id in sorted(nach_track):
        zeilen = nach_track[track_id]
        treffer = _treffer(track_id, katalog)
        if len(treffer) == 1:
            aus = auswerten(zeilen)
            zuordnungen.append(dict(aus, item_id=treffer[0], track_id=track_id))
        else:
            grund = 'mehrdeutig' if treffer else 'kein_treffer'
            offen.append({'track_id': track_id, 'grund': grund, 'anzahl_urteile': len(zeilen)})
    return zuordnungen, offen


def merge_passt_nicht(bestehend, neue):
    """Kommagetrennte Sendungsliste: bestehenden beets-Wert behalten, neue
    Sendungen anhängen, keine Duplikate, Reihenfolge stabil."""
    vorhandene = [s.strip() for s in (bestehend or '').split(',') if s.strip()]
    for s in neue:
        if s and s not in vorhandene:
            vorhandene.append(s)
    return ', '.join(vorhandene)


# ---------------------------------------------------------------------------
# I/O — Export, Token, CSV, DB-Sicherung, beets (nur hier, nicht oben testen)
# ---------------------------------------------------------------------------

def token_lesen(pfad=ENV_DATEI):
    with open(pfad, encoding='utf-8') as f:
        werte = dict(z.strip().split('=', 1) for z in f if '=' in z and not z.startswith('#'))
    return werte['ODOO_EXPORT_TOKEN']


def export_holen(token, url=EXPORT_URL):
    r = requests.get(url, headers={'X-Agent-Token': token}, timeout=30)
    r.raise_for_status()
    return r.json()


def csv_schreiben(offen, pfad=OFFEN_CSV):
    os.makedirs(os.path.dirname(pfad), exist_ok=True)
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['track_id', 'grund', 'anzahl_urteile'])
        for o in offen:
            w.writerow([o['track_id'], o['grund'], o['anzahl_urteile']])


def sichern(db_pfad=DB_PFAD, datum=None):
    """Kopiert die beets-DB vor dem Schreiben weg. Gibt den Zielpfad zurück."""
    datum = datum or datetime.date.today().isoformat()
    ziel = '%s.vor-rueckschreiben-%s' % (db_pfad, datum)
    shutil.copy2(db_pfad, ziel)
    return ziel


def _katalog_aus_lib(lib):
    return [{'id': it.id, 'artist': it.artist, 'title': it.title} for it in lib.items()]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--probe', action='store_true', help='nur rechnen und anzeigen, nichts schreiben')
    args = ap.parse_args(argv)

    import beets.library  # erst hier: Probelauf/Tests brauchen kein beets

    token = token_lesen()
    export = export_holen(token)
    lib = beets.library.Library(DB_PFAD)
    katalog = _katalog_aus_lib(lib)
    zuordnungen, offen = plan_erstellen(export, katalog)
    datum = datetime.date.today().isoformat()

    titel_gesamt = len({z['track_id'] for z in export})
    print('Export-Zeilen: %d, Titel gesamt: %d, zugeordnet: %d, offen: %d'
          % (len(export), titel_gesamt, len(zuordnungen), len(offen)))
    for z in zuordnungen:
        print('  item=%s %s energie=%s passt_nicht=%s'
              % (z['item_id'], z['track_id'], z['energie'], z['passt_nicht'] or '-'))
    for o in offen:
        print('  offen: %s (%s, %d Urteil(e))' % (o['track_id'], o['grund'], o['anzahl_urteile']))

    if args.probe:
        print('PROBE: nichts geschrieben.')
        return 0

    # DB-Sicherung vor JEDEM echten Lauf, unabhängig davon, ob am Ende
    # etwas zu schreiben ist (Vorgabe: Sicherung *vor* dem Lauf, nicht nur
    # vor tatsächlichen Schreibzugriffen).
    sicherung = sichern(datum=datum)
    print('DB gesichert nach', sicherung)

    if offen:
        csv_schreiben(offen)
        print('Offen-Liste geschrieben:', OFFEN_CSV)

    if not zuordnungen:
        print('Nichts zu schreiben.')
        return 0

    geschrieben = 0
    for z in zuordnungen:
        item = lib.get_item(z['item_id'])
        if item is None:
            continue
        if z['energie'] is not None:
            item.energie = z['energie']
            item.quelle_energie = 'Redaktion %s' % datum
        if z['passt_nicht']:
            item.passt_nicht = merge_passt_nicht(item.get('passt_nicht', ''), z['passt_nicht'])
        item.store()
        geschrieben += 1
    print('geschrieben: %d Titel' % geschrieben)
    return 0


if __name__ == '__main__':
    sys.exit(main())

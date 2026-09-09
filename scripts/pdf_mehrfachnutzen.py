#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mehrere PDF-Seiten auf ein Blatt legen (2-fach oder 4-fach Nutzen).

Anlass, 09.09.2026: Fuer das Amtsgericht Viechtach muessen 94 Seiten
Kontoauszug eingereicht werden. Die N26-Auszuege sind extrem duenn gesetzt -
gemessen 100 bis 140 Woerter je A4-Seite, wo eine normale Textseite 400 bis 600
traegt. Es ist also fast nur Luft, die da gedruckt wuerde.

Deshalb: mehrere Originalseiten massstaeblich verkleinert auf ein Blatt, mit
duenner Trennlinie, damit sofort erkennbar bleibt, dass es sich um mehrere
Seiten handelt und nichts fehlt oder verschoben wurde.

    2-fach  ->  A4 quer, zwei Hochformatseiten nebeneinander, Massstab 0,707
                Schrift von 11 pt auf rund 7,8 pt - bequem lesbar
    4-fach  ->  A4 hoch, zwei mal zwei Seiten, Massstab 0,5
                Schrift auf rund 5,5 pt - klein, aber lesbar

Die Seitenreihenfolge bleibt streng erhalten (links nach rechts, oben nach
unten). Das ist bei Belegen fuer ein Gericht keine Kosmetik, sondern
Voraussetzung dafuer, dass die Anlage ueberhaupt nachvollziehbar ist.

Aufruf:
    python3 pdf_mehrfachnutzen.py <ein.pdf> <aus.pdf> <2|4>
"""

import sys

import pikepdf
from pikepdf import Pdf, Page, Rectangle

A4_BREIT, A4_HOCH = 595.276, 841.890
RAND = 8.0            # Punkt Luft am Blattrand
STEG = 6.0            # Punkt zwischen den Feldern


def felder(anzahl):
    """Blattgroesse und die Rechtecke, in die die Seiten gelegt werden."""
    if anzahl == 2:
        # A4 quer, zwei Felder nebeneinander
        blatt = (A4_HOCH, A4_BREIT)
        spalten, zeilen = 2, 1
    elif anzahl == 4:
        # A4 hoch, zwei mal zwei
        blatt = (A4_BREIT, A4_HOCH)
        spalten, zeilen = 2, 2
    else:
        raise SystemExit('Nur 2 oder 4 moeglich, nicht %r' % anzahl)

    b, h = blatt
    feld_b = (b - 2 * RAND - (spalten - 1) * STEG) / spalten
    feld_h = (h - 2 * RAND - (zeilen - 1) * STEG) / zeilen

    rechtecke = []
    for z in range(zeilen):
        for s in range(spalten):
            x0 = RAND + s * (feld_b + STEG)
            # PDF zaehlt von unten; wir wollen oben anfangen (Lesereihenfolge)
            y1 = h - RAND - z * (feld_h + STEG)
            rechtecke.append(Rectangle(x0, y1 - feld_h, x0 + feld_b, y1))
    return blatt, rechtecke


def trennlinien(rechtecke):
    """Duenner grauer Rahmen je Feld - macht die Aufteilung sichtbar."""
    teile = ['q 0.75 0.75 0.75 RG 0.4 w']
    for r in rechtecke:
        teile.append('%.2f %.2f %.2f %.2f re S'
                     % (r.llx, r.lly, r.urx - r.llx, r.ury - r.lly))
    teile.append('Q')
    return ' '.join(teile).encode('ascii')


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    quelle, ziel, anzahl = sys.argv[1], sys.argv[2], int(sys.argv[3])

    blatt, rechtecke = felder(anzahl)
    src = Pdf.open(quelle)
    out = Pdf.new()

    seiten = len(src.pages)
    for anfang in range(0, seiten, anzahl):
        blattseite = out.add_blank_page(page_size=blatt)
        ziel_seite = Page(blattseite)
        gelegt = 0
        for i in range(anzahl):
            if anfang + i >= seiten:
                break
            ziel_seite.add_overlay(src.pages[anfang + i], rechtecke[i])
            gelegt += 1
        # Rahmen nur um tatsaechlich belegte Felder - ein leerer Kasten am
        # Ende sieht aus, als fehle eine Seite.
        blattseite.contents_add(
            pikepdf.Stream(out, trennlinien(rechtecke[:gelegt])), prepend=False)

    out.save(ziel)
    blaetter = (seiten + anzahl - 1) // anzahl
    print('  %-46s %3d Seiten -> %3d Blatt (%d-fach, beidseitig %d Blatt)'
          % (quelle.split('/')[-1], seiten, blaetter, anzahl,
             (blaetter + 1) // 2))


if __name__ == '__main__':
    main()

# -*- coding: utf-8 -*-
# Liest aus Paperless alle Dokumente des Jahres 2026 und zieht Betraege heraus.
# Zweck: Grundlage fuer die EUER 2026 (Einzelunternehmen bis 04/2026, GbR ab 04/2026).
#
# Laeuft im Paperless-Container:
#   docker exec -i paperless-webserver python3 manage.py shell < dieses_skript.py
#
# Bewusst nur LESEND. Es aendert nichts in Paperless.
#
# Betragserkennung: Zahlen im deutschen (1.234,56) und englischen (1,234.56)
# Format. Bevorzugt werden Zeilen mit Summen-Stichworten; sonst gilt der
# groesste gefundene Betrag als Kandidat. Das ist eine HILFE, kein Beleg —
# jede Zeile muss gegen das Original geprueft werden, bevor sie in die
# Steuererklaerung wandert.

import re
from documents.models import Document

SUMMEN_WORTE = (
    "gesamtbetrag", "gesamtsumme", "rechnungsbetrag", "zu zahlen",
    "zahlbetrag", "endbetrag", "total", "amount due", "grand total",
    "summe", "gesamt", "betrag",
)

# 1.234,56  |  1,234.56  |  1234,56  |  1234.56
GELD = re.compile(r"(?<![\d.,])(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})|\d+[.,]\d{2})(?![\d])")


def zu_float(s):
    """Wandelt einen erkannten Geldstring in eine Zahl."""
    s = s.strip()
    if "," in s and "." in s:
        # Das hintere Zeichen ist das Dezimaltrennzeichen
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def betrag_raten(text):
    """Liefert (betrag, quelle) - Summenzeile bevorzugt, sonst groesster Wert."""
    if not text:
        return (None, "")
    kandidaten_summenzeile = []
    alle = []
    for zeile in text.splitlines():
        klein = zeile.lower()
        treffer = [zu_float(m) for m in GELD.findall(zeile)]
        treffer = [t for t in treffer if t is not None and t > 0]
        if not treffer:
            continue
        alle.extend(treffer)
        if any(w in klein for w in SUMMEN_WORTE):
            kandidaten_summenzeile.append((max(treffer), zeile.strip()[:70]))
    if kandidaten_summenzeile:
        # letzte Summenzeile im Dokument ist meist die maszgebliche
        return kandidaten_summenzeile[-1]
    if alle:
        return (max(alle), "(keine Summenzeile - groeszter Betrag im Text)")
    return (None, "")


docs = [d for d in Document.objects.all() if d.created.year == 2026]
docs.sort(key=lambda d: d.created)

print("ANZAHL 2026: %d" % len(docs))
print("")
print("ID   | Datum      | Typ              | Absender                  | Betrag     | Fundstelle")
print("-" * 130)

for d in docs:
    betrag, quelle = betrag_raten(d.content)
    typ = str(d.document_type) if d.document_type else "-"
    absender = str(d.correspondent) if d.correspondent else "-"
    b = ("%10.2f" % betrag) if betrag is not None else "         ?"
    print("%-4d | %s | %-16s | %-25s | %s | %s" % (
        d.id, d.created, typ[:16], absender[:25], b, quelle[:48]))

# -*- coding: utf-8 -*-
# Loescht die am 08.09.2026 identifizierten Dubletten aus Paperless.
#
# Freigabe: Wolf am 08.09.2026 ausdruecklich erteilt.
#
# 179, 184, 180, 187 sind beim Handbetrieb-Nachziehen der Google-Drive-Inbox
# entstanden - Dateien, die Paperless am 06.09. bereits verarbeitet hatte.
# Paperless erkennt Dubletten nur ueber die Pruefsumme; zwei Downloads
# derselben Rechnung unterscheiden sich in wenigen Bytes und rutschen durch.
# 156 ist eine aeltere Dublette (Allianz-Ueberweisungsbestaetigung),
# stammt nicht aus diesem Vorgang.
#
# Das Skript zeigt ERST, was es loeschen wuerde, und prueft dabei, ob das
# jeweilige Original noch existiert. Findet es ein Original nicht, wird die
# betreffende Dublette NICHT geloescht - dann waere es keine Dublette mehr,
# sondern das letzte Exemplar.

from documents.models import Document

# Dublette -> Original, das bestehen bleiben muss
PAARE = {
    179: 160,   # Anthropic Invoice-NZQ8GPTZ-0031, 02.09.
    184: 162,   # Anthropic Receipt-2495-8774-9965, 02.09.
    180: 161,   # Anthropic Invoice-NZQ8GPTZ-0033, 06.09.
    187: 173,   # Anthropic Receipt-2645-9847-0190, 06.09.
    156: 42,    # Allianz Ueberweisungsbestaetigung, 30.04.
}

print("PRUEFUNG")
print("-" * 78)

zu_loeschen = []
for dubl_id, orig_id in sorted(PAARE.items()):
    try:
        dubl = Document.objects.get(pk=dubl_id)
    except Document.DoesNotExist:
        print("%-4d uebersprungen - existiert nicht (mehr)" % dubl_id)
        continue
    if not Document.objects.filter(pk=orig_id).exists():
        print("%-4d NICHT geloescht - Original %d fehlt, waere das letzte Exemplar" % (dubl_id, orig_id))
        continue
    orig = Document.objects.get(pk=orig_id)
    print("%-4d %s  %-34s  -> Original %d bleibt (eingegangen %s)" % (
        dubl_id, dubl.created, (dubl.title or "")[:34], orig_id, orig.added.date()))
    zu_loeschen.append(dubl)

print("")
print("LOESCHE %d Dokument(e)" % len(zu_loeschen))
print("-" * 78)

for d in zu_loeschen:
    kennung = "%d %s" % (d.id, (d.title or "")[:44])
    d.delete()
    print("geloescht: %s" % kennung)

print("")
print("Dokumente in Paperless danach: %d" % Document.objects.count())

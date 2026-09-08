# -*- coding: utf-8 -*-
# Findet Dubletten in Paperless: gleiche Absender + gleiches Belegdatum +
# gleicher Inhaltsanfang. Nur LESEND — loescht nichts.
#
# Anlass: Beim Handbetrieb-Nachziehen der Google-Drive-Inbox am 08.09.2026
# wurden Dateien eingespielt, die Paperless am 06.09. teilweise schon
# verarbeitet hatte. Paperless erkennt Dubletten nur ueber die Pruefsumme —
# zwei Downloads derselben Rechnung unterscheiden sich aber in ein paar
# Bytes und rutschen deshalb durch.

from collections import defaultdict
from documents.models import Document

gruppen = defaultdict(list)
for d in Document.objects.all():
    if d.created.year != 2026:
        continue
    kopf = (d.content or "")[:180].strip().replace("\n", " ")
    schluessel = (str(d.correspondent), str(d.created), kopf)
    gruppen[schluessel].append(d)

mehrfach = {k: v for k, v in gruppen.items() if len(v) > 1}

print("DUBLETTEN-GRUPPEN: %d" % len(mehrfach))
gesamt_ueberzaehlig = 0
print("")

for (absender, datum, _kopf), docs in sorted(mehrfach.items(), key=lambda x: x[0][1]):
    docs.sort(key=lambda d: d.added)
    behalten = docs[0]
    weg = docs[1:]
    gesamt_ueberzaehlig += len(weg)
    print("%s | %-26s | behalten: %-4d (eingegangen %s)" % (
        datum, absender[:26], behalten.id, behalten.added.date()))
    for d in weg:
        print("      ueberzaehlig: %-4d (eingegangen %s)  %s" % (
            d.id, d.added.date(), (d.title or "")[:52]))

print("")
print("UEBERZAEHLIGE DOKUMENTE INSGESAMT: %d" % gesamt_ueberzaehlig)
print("Davon heute (08.09.) eingegangen: %d" % sum(
    1 for k, v in mehrfach.items() for d in sorted(v, key=lambda x: x.added)[1:]
    if str(d.added.date()) == "2026-09-08"))

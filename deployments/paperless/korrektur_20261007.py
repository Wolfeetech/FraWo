# Paperless-Bestand nach Ablageordnung korrigieren (Odoo #1927, Wolf 07.10.: "Best practice umsetzen").
# Laeuft in CT110:  docker exec -i paperless-webserver python3 manage.py shell < korrektur_20261007.py
# Schreibt vorher die alten Werte nach /usr/src/paperless/data/korrektur_20261007_vorher.json (Rueckweg).
# Nur eindeutige Faelle; Zweifelsfaelle werden NICHT geaendert, sondern am Ende gelistet.
import json, re
from documents.models import Document, Correspondent, DocumentType

C = {c.name: c for c in Correspondent.objects.all()}
T = {t.name: t for t in DocumentType.objects.all()}
vorher = {}

def merke(d):
    vorher.setdefault(d.id, {"title": d.title, "correspondent": d.correspondent_id, "document_type": d.document_type_id})

def setze(d, korr=None, typ=None, titel=None):
    merke(d)
    if korr: d.correspondent = C[korr]
    if typ: d.document_type = T[typ]
    if titel: d.title = titel
    d.save()

# 1) Noerpel-Unterlagen 2017 (Quelle Drive 00_INBOX/Noerpel) - von der KI der GbR zugeschrieben
for i, titel in [(294, "Zuschläge Arbeitsvertrag Noerpel 2017-11-25"), (301, "Arbeitsvertrag Noerpel Seite 2 2017-03-10"),
                 (303, "Arbeitsvertrag Noerpel Seite 4 2017-03-10"), (295, "Arbeitsvertrag Noerpel Seite 6 2017-03-10")]:
    setze(Document.objects.get(id=i), "Noerpel Logistics & Services GmbH", "Vertrag", titel)

# 2) Eigene AEVO-/Ausbilder-Unterlagen (2013-2025) - nicht von der GbR, Verfasser Wolf
for d in Document.objects.filter(id__in=[112, 116, 118, 120, 123, 126, 127, 129]):
    t = re.sub(r"\s*FraWo[ _]GbR", "", d.title).strip()
    t = re.sub(r"^Schulungsunterlage\s*$", "Schulungsunterlage " + re.sub(r"\.\w+$", "", d.original_filename), t)
    setze(d, "Wolf Prinz", None, t)

# 3) Lohn-/Gehaltsabrechnungen mit falscher Dokumentart
for d in Document.objects.filter(id__in=[276, 289, 292, 293]):
    setze(d, None, "Gehaltsabrechnung", re.sub(r"(?i)^(Lohnabrechnung|Gehaltsnachweis)", "Gehaltsabrechnung", d.title))

# 4) Doppelte Korrespondenten zusammenfuehren (gleiche Firma, verschiedene Schreibweisen)
ZUSAMMEN = {
    "Noerpel Logistics & Services GmbH": ["Noerpel Logistics", "Noerpel Logistics & Services"],
    "Lindau Tourismus und Kongress GmbH": ["Lindau Tourismus und Kongress"],
    "IHK Bodensee-Oberschwaben": ["IHK Bodensee - Oberschwaben"],
    "Wolf Prinz": ["Wolfgang Prinz", "Prinz, Wolfgang", "Prinz Wolfgang Ferdinand"],
    "Unbekannt": ["null"],
}
for ziel, alte in ZUSAMMEN.items():
    for a in alte:
        if a in C:
            for d in Document.objects.filter(correspondent=C[a]):
                setze(d, ziel)
            C[a].delete()

# 5) Entscheidungen Wolf 07.10.: "Gehalt zahlt LTK", Gesellschaftsvertrag "01.04.", Aenderungsvertrag 2024
#    "war ich bei der LTK", Shelly-CSV ist kein Beleg (Kopie liegt in Nextcloud 80_Technik/IT/Messdaten).
import datetime
LTK = "Lindau Tourismus und Kongress GmbH"
for i, titel in [(20, "Gehaltsabrechnung Lindau Tourismus und Kongress 2026-03-27"),
                 (276, "Gehaltsabrechnung Lindau Tourismus und Kongress 2026-07-29")]:
    setze(Document.objects.get(id=i), LTK, "Gehaltsabrechnung", titel)
d = Document.objects.get(id=104); merke(d); vorher[104]["created"] = str(d.created)
d.created = datetime.date(2026, 4, 1); d.title = "Gesellschaftsvertrag FraWo GbR 2026-04-01"; d.save()
setze(Document.objects.get(id=109), LTK, "Vertrag", "Änderungsvertrag Lindau Tourismus und Kongress 2024-07-31")
d = Document.objects.get(id=275); merke(d); d.delete()   # Papierkorb, 30 Tage wiederherstellbar

json.dump(vorher, open("/usr/src/paperless/data/korrektur_20261007_vorher.json", "w"), indent=1)
print("geaendert:", len(vorher), "Dokumente (275 in den Papierkorb)")

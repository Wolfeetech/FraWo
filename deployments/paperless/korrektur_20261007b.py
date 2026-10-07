# Paperless: Dokumente ohne Absender nachziehen (Odoo #1927). Laeuft in CT110:
#   docker exec -i paperless-webserver python3 manage.py shell < korrektur_20261007b.py
# Alte Werte -> /usr/src/paperless/data/korrektur_20261007b_vorher.json. Nur eindeutige Faelle (nach OCR-Text geprueft).
import datetime, json
from documents.models import Document, Correspondent, DocumentType

C = lambda n: Correspondent.objects.get_or_create(name=n)[0]
T = lambda n: DocumentType.objects.get(name=n)
vorher = {}

def setze(i, korr=None, typ=None, titel=None, datum=None):
    d = Document.objects.get(id=i)
    vorher[i] = {"title": d.title, "correspondent": d.correspondent_id, "document_type": d.document_type_id, "created": str(d.created)}
    if korr: d.correspondent = C(korr)
    if typ: d.document_type = T(typ)
    if titel: d.title = titel
    if datum: d.created = datum
    d.save()

setze(229, "GitHub", "Quittung", "Quittung GitHub 2026-09-23", datetime.date(2026, 9, 23))      # Text: "payment for your GitHub.com subscription", Wolfeetech
setze(412, "Wolf Prinz", "Bewerbung", "Lebenslauf Wolf Prinz")                                   # war "Zeugnis", Datum = Geburtsdatum
setze(414, None, None, "Arbeitszeugnis Wolfgang Prinz")                                          # docx, OCR unlesbar
setze(383, None, "Sonstiges", "Arbeitszeiten Juni 2025 (Screenshot)")                            # Excel-Stundenliste, kein Lohnzettel
setze(385, None, "Sonstiges", "Arbeitszeiten Juli 2025 (Screenshot)")
setze(386, None, "Sonstiges", "Kostenübersicht Cloud-Dienst Juni 2025 (Screenshot)")             # Kosten-Dashboard, keine Rechnung

# Produktbilder JBL EON615 (keine Dokumente) - Kopie liegt in Nextcloud 80_Technik/Ton/JBL_EON615 -> Papierkorb (30 Tage)
for i in (258, 259, 260, 261):
    d = Document.objects.get(id=i); vorher[i] = {"title": d.title, "papierkorb": True}; d.delete()

json.dump(vorher, open("/usr/src/paperless/data/korrektur_20261007b_vorher.json", "w"), indent=1)
print("geaendert:", len(vorher), "(davon 4 Bilder in den Papierkorb)")

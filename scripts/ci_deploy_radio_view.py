#!/usr/bin/env python3
"""Fuer odoo shell: Radioseite (ir.ui.view 3353) aus der Repo-Quelle live setzen.

Warum odoo shell und nicht die normale Schnittstelle: `arch_db` ist ein
uebersetztes Feld. Ueber die Schnittstelle wird nur die Sprache der eigenen
Sitzung geschrieben (en_US) -- die Website laeuft aber auf de_DE. Darum wird
hier jede aktive Sprache gesetzt und danach der Cache geleert und signalisiert
(ohne signal_changes sehen die anderen Arbeitsprozesse die Aenderung nicht).

Erwartet den neuen Inhalt unter /tmp/radio_page_neu.xml im Container.
"""

VIEW_ID = 3353
QUELLE = "/tmp/radio_page_neu.xml"

with open(QUELLE, encoding="utf-8") as fh:
    neu = fh.read()

view = env["ir.ui.view"].browse(VIEW_ID)
if not view.exists():
    raise SystemExit("Ansicht %s nicht gefunden" % VIEW_ID)

langs = env["res.lang"].search([("active", "=", True)]).mapped("code")
print("Sprachen:", langs)

for lang in langs:
    rec = view.with_context(lang=lang)
    alt = rec.arch_db or ""
    rec.arch_db = neu
    print("  %s: %d -> %d Zeichen" % (lang, len(alt), len(neu)))

env.registry.clear_cache()
env.registry.signal_changes()
env.cr.commit()

# Gegenprobe direkt aus der Datenbank, in jeder Sprache
for lang in langs:
    gelesen = env["ir.ui.view"].browse(VIEW_ID).with_context(lang=lang).arch_db or ""
    print("  Gegenprobe %s: beat-stage=%s, getLevels=%s, Altfarben=%d" % (
        lang,
        "ff-beat-stage" in gelesen,
        "getLevels" in gelesen,
        sum(gelesen.lower().count(c) for c in ("#00bfff", "#00e599", "#a855f7", "#0099cc")),
    ))
print("FERTIG")

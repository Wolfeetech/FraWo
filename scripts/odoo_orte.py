# -*- coding: utf-8 -*-
# Ortsdimension fuer Aufgaben, 09.09.2026.
#
# Wolf: "ich wuerde gern Aufgaben iwie schlau aufteilen ... todo @rk22
# todo @villa und todo_remote ... und so immer direkt wissen was wo ansteht ...
# aber das funktioniert nur wenn's schlau und sauber umgesetzt wird nicht nur
# schnell schnell"
#
# ENTWURFSENTSCHEIDUNGEN, kurz begruendet
#
# 1. Schlagwoerter, kein eigenes Feld.
#    Ein Auswahlfeld waere datenmodellierisch sauberer (ein Ort je Aufgabe,
#    nicht verwechselbar). Es braucht aber ein ir.model.fields plus geerbte
#    Ansichten - ein Eingriff ins Produktivsystem mit echtem Risiko, kaputte
#    Ansichten inklusive. Schlagwoerter koennen dasselbe, funktionieren sofort,
#    erscheinen in der Handy-App und sind rueckstandslos entfernbar. Wenn sich
#    die Ortsdimension bewaehrt, ist die Umstellung auf ein Feld spaeter ohne
#    Datenverlust moeglich.
#
# 2. Wolfs Schreibweise, nicht meine.
#    Er denkt in "@rk22". Also heissen sie so - nicht "Ort: Rothkreuz 22a".
#    Das @-Praefix sortiert sie zusammen und macht sie unverwechselbar.
#
# 3. Der Ort wird NICHT aus dem Projekt abgeleitet.
#    Genau davor warnt die Standortnotiz: der Container gehoert FraWo, steht
#    aber in Stockenweiler. Organisatorische Zugehoerigkeit ist nicht der
#    physische Ort. Zugeordnet wird deshalb nur dort, wo das Projekt SELBST
#    ein Ort ist ("Studio Villa (Rothkreuz 14)"). Alles andere bleibt offen
#    und taucht im Filter "Ohne Ort" auf - sichtbar statt geraten.

ERLEDIGT = "(6, 35)"
ORTE = {
    'rk22':          (154, 'Rothkreuz 22a — Wohnung, Anker-Server, Werkbank'),
    'villa':         (155, 'Rothkreuz 14 — Studio, Geschaeftsadresse, Baustelle'),
    'stockenweiler': (156, 'Grundstueck der Eltern — Container, PV, Waermepumpe'),
    'inselhalle':    (159, 'Arbeitsplatz Lindau'),
    'unterwegs':     (158, 'Post, Bank, Abholung — alles auf dem Weg'),
    'remote':        (157, 'ortsunabhaengig, am Rechner'),
}
ALLE_ORT_IDS = [v[0] for v in ORTE.values()]

Filter = env['ir.filters']
Task = env['project.task']
modell = 'project.task'


def ansicht(name, domain, context):
    # Odoo 19: aus ir.filters.user_id (many2one) wurde user_ids (many2many).
    # Leere Liste bedeutet: fuer alle sichtbar. 'sort' ist Pflichtfeld und
    # nimmt eine Liste als Text - leer heisst Standardsortierung.
    werte = {'name': name, 'model_id': modell, 'domain': domain,
             'context': context, 'user_ids': [(6, 0, [])], 'sort': '[]',
             'action_id': False, 'is_default': False}
    vorhanden = Filter.search([('name', '=', name), ('model_id', '=', modell)], limit=1)
    if vorhanden:
        vorhanden.write(werte)
        return 'aktualisiert'
    Filter.create(werte)
    return 'angelegt'


print("=" * 78)
print("ORTSANSICHTEN")
print("=" * 78)

for kurz, (tag_id, beschreibung) in ORTE.items():
    name = "@%s" % kurz
    zustand = ansicht(
        name,
        "[('tag_ids', 'in', [%d]), ('stage_id', 'not in', %s)]" % (tag_id, ERLEDIGT),
        "{'group_by': ['stage_id']}")
    anzahl = Task.search_count([('tag_ids', 'in', [tag_id]),
                                ('stage_id', 'not in', (6, 35))])
    print("  %-12s %-16s %3d offene Aufgaben   %s"
          % (zustand, name, anzahl, beschreibung))

# Der wichtigste Filter von allen: was noch keinen Ort hat. Eine Dimension,
# die nur halb gepflegt ist, taeuscht mehr als sie hilft - also muss die
# Luecke sichtbar sein.
zustand = ansicht(
    "📍 Ohne Ort — bitte zuordnen",
    "[('tag_ids', 'not in', %s), ('stage_id', 'not in', %s)]"
    % (str(ALLE_ORT_IDS), ERLEDIGT),
    "{'group_by': ['project_id']}")
ohne = Task.search_count([('tag_ids', 'not in', ALLE_ORT_IDS),
                          ('stage_id', 'not in', (6, 35))])
print("  %-12s %-16s %3d offene Aufgaben" % (zustand, "Ohne Ort", ohne))

zustand = ansicht(
    "📍 Alles nach Ort",
    "[('stage_id', 'not in', %s)]" % ERLEDIGT,
    "{'group_by': ['tag_ids']}")
print("  %-12s %-16s  nach Schlagwort gruppiert" % (zustand, "Alles nach Ort"))

# --- Vorsichtige Erstzuordnung ---------------------------------------------
# NUR Projekte, die selbst einen Ort bezeichnen. Alles andere waere geraten.
print("")
print("=" * 78)
print("ERSTZUORDNUNG — nur wo das Projekt SELBST der Ort ist")
print("=" * 78)

SICHER = {
    159: 155,   # "Studio Villa (Rothkreuz 14)"        -> @villa
    106: 156,   # "Familie & Immobilien (Stockenweiler)" -> @stockenweiler
}

for projekt_id, tag_id in SICHER.items():
    p = env['project.project'].browse(projekt_id).exists()
    if not p:
        print("  Projekt %s fehlt - uebersprungen" % projekt_id)
        continue
    offen = Task.search([('project_id', '=', projekt_id),
                         ('stage_id', 'not in', (6, 35)),
                         ('tag_ids', 'not in', ALLE_ORT_IDS)])
    if offen:
        offen.write({'tag_ids': [(4, tag_id)]})
    print("  %-46s %3d Aufgaben markiert" % (p.name[:46], len(offen)))

print("")
print("  Alles andere bleibt bewusst ohne Ort. Der Ort einer Aufgabe ergibt")
print("  sich nicht aus ihrem Projekt - das muss ein Mensch entscheiden.")

env.cr.commit()
print("")
print("Festgeschrieben. Sichtbar unter Projekt → Aufgaben → Favoriten.")

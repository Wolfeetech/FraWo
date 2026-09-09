# -*- coding: utf-8 -*-
# Orte zuweisen, wo sie aus der Sache folgen. 09.09.2026.
#
# Der Tagesplan im Bericht zeigt nur, was einen Ort hat. 60 machbare
# Aufgaben hatten keinen - der Plan blieb dadurch duenn.
#
# Heute frueh habe ich nur zwei Projekte zugeordnet, weil die Standortnotiz
# warnt: "organisatorische Zugehoerigkeit ist nicht der physische Ort".
# Das gilt weiter. Aber bei diesen vier Projekten folgt der Ort aus der
# TAETIGKEIT, nicht aus der Zugehoerigkeit:
#
#   Werkstatt          -> @villa    Die Werkstatt STEHT in der Villa.
#   Business/Finanzen  -> @remote   Rechnungen, Belege, EUER = Schreibtisch.
#   Marke & Website    -> @remote   Text, Bild, Web = Schreibtisch.
#   Radio              -> @remote   Server und Playlisten = Schreibtisch.
#
# Bewusst NICHT zugeordnet:
#   104 Auftraege & Events  - haengt am jeweiligen Veranstaltungsort
#   105 IT & Infrastruktur  - teils am Server (@rk22), teils fern (@remote).
#                             Das muss ein Mensch je Aufgabe entscheiden.
#
# Bestehende Ortszuordnungen werden nicht ueberschrieben.

ORTE = {'rk22': 154, 'villa': 155, 'stockenweiler': 156,
        'remote': 157, 'unterwegs': 158, 'inselhalle': 159}
ALLE = list(ORTE.values())

ZUORDNUNG = {
    160: (ORTE['villa'],  'Werkstatt steht in der Villa'),
    163: (ORTE['remote'], 'Rechnungen, Belege, EUER - Schreibtischarbeit'),
    110: (ORTE['remote'], 'Text, Bild, Website - Schreibtischarbeit'),
    161: (ORTE['remote'], 'Server und Playlisten - Schreibtischarbeit'),
}

Task = env['project.task']

print("=" * 74)
print("ORTE ZUWEISEN")
print("=" * 74)

gesamt = 0
for projekt_id, (tag_id, grund) in ZUORDNUNG.items():
    p = env['project.project'].browse(projekt_id).exists()
    if not p:
        continue
    offen = Task.search([('project_id', '=', projekt_id),
                         ('stage_id', 'not in', (6, 35)),
                         ('tag_ids', 'not in', ALLE)])
    if offen:
        offen.write({'tag_ids': [(4, tag_id)]})
    gesamt += len(offen)
    print("  %-46s %3d Aufgaben   %s" % (p.name[:46], len(offen), grund))

ohne = Task.search_count([('stage_id', 'in', (2, 3)),
                          ('project_id', 'not in', (106, 107)),
                          ('tag_ids', 'not in', ALLE)])
print("")
print("  zugewiesen: %d" % gesamt)
print("  noch ohne Ort (machbar): %d" % ohne)
print("")
print("  Der Rest ist Absicht: Auftraege haengen am Veranstaltungsort,")
print("  IT-Aufgaben teils am Server, teils fern. Das entscheidet ein Mensch")
print("  - Ansicht 'Ohne Ort' unter Favoriten.")

env.cr.commit()
print("")
print("Festgeschrieben.")

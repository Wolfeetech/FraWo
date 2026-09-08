# -*- coding: utf-8 -*-
# Neuzuschnitt der FraWo-Projektstruktur, 08.09.2026.
#
# Verschiebt offene Aufgaben aus den beiden ueberfuellten Sammelprojekten
# in die neuen Fachprojekte. Erledigte Aufgaben bleiben unangetastet -
# sie sind Historie, ein Verschieben braechte nichts und wuerde nur die
# Auswertungen verfaelschen.
#
# Laeuft in der Odoo-Shell:
#   docker exec -i frawotech-odoo-1 odoo shell -d FraWo_GbR < dieses_skript.py
#
# Ordnungsprinzip: nach ERGEBNIS, nicht nach Werkzeug.
# Faustregel fuer Zweifelsfaelle: Was der Kunde oder Hoerer merkt, gehoert
# ins Fachprojekt. Was nur der Betreiber merkt, gehoert in die IT.

ZIELE = {
    # 40 - Radio FraWo Funk: alles, was der Hoerer merkt
    161: [243, 323, 334, 467, 529, 552, 890, 1017, 1090, 1123,
          1261, 1263, 1268, 1295, 1300, 1350],

    # 20 - Werkstatt & Lautsprecherbau: gebaut und repariert wird hier
    160: [374, 376, 377, 381, 385, 477, 1089, 1099, 1100, 1103,
          1104, 1105, 1038, 1205, 1206, 1207],

    # 60 - Business, Recht & Finanzen: alles mit Fristen und Folgen
    163: [152, 222, 824, 992, 996, 1362, 1365, 1189],

    # 70 - Marke & Website: alles, was nach aussen wirkt
    110: [722, 723, 538, 1124, 1125, 465, 1092],

    # 80 - GrowBox: das Testmodell
    162: [958, 1157, 1160, 1161, 1162, 1091],

    # 30 - Studio Villa: alles zu Rothkreuz 14 OG
    159: [1040, 1041, 1043, 1175, 1176, 1177, 1178, 1179, 1180],
}

ERLEDIGT_STAGES = (6, 35)   # Erledigt, Abgebrochen

gesamt = 0
uebersprungen = []

for ziel_id, task_ids in ZIELE.items():
    ziel = env['project.project'].browse(ziel_id)
    tasks = env['project.task'].browse(task_ids).exists()

    # Sicherheitsnetz: nichts anfassen, was schon abgeschlossen ist
    offen = tasks.filtered(lambda t: t.stage_id.id not in ERLEDIGT_STAGES)
    zu_alt = tasks - offen
    for t in zu_alt:
        uebersprungen.append((t.id, t.name[:50], t.stage_id.name))

    fehlend = set(task_ids) - set(tasks.ids)
    for f in fehlend:
        uebersprungen.append((f, "(existiert nicht)", "-"))

    if offen:
        offen.write({'project_id': ziel_id})
        gesamt += len(offen)
    print("%-46s %3d verschoben" % (ziel.name, len(offen)))

print("")
print("GESAMT VERSCHOBEN: %d" % gesamt)

if uebersprungen:
    print("")
    print("UEBERSPRUNGEN:")
    for tid, name, stage in uebersprungen:
        print("  %-5s %-50s %s" % (tid, name, stage))

env.cr.commit()
print("")
print("Festgeschrieben.")

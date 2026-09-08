# -*- coding: utf-8 -*-
# Zwei Aufraeumschritte, 08.09.2026.
#
# 1. Meilensteine aus archivierten Projekten in die aktiven umhaengen.
#    Es gibt sechs Stueck; fuenf davon (Waermepumpe Stockenweiler) sind seit
#    Wochen ueberfaellig. Gesehen hat das niemand, weil allow_milestones auf
#    ALLEN Projekten aus war und die Traegerprojekte archiviert sind.
#
# 2. "Anschaffungen & Investitionen" in "60 - Business, Recht & Finanzen"
#    aufgehen lassen. Investitionen haengen an Abschreibung und
#    Wirtschaftlichkeit - das ist ein Finanzthema, kein eigener Bereich.
#
# Laeuft in der Odoo-Shell.

# --- 1. Meilensteine umhaengen --------------------------------------------
UMZUG = {
    58: 106,   # WP-Stockenweiler-3 (archiviert) -> 90 - Familie & Immobilien
    35: 105,   # P0 Infrastruktur (archiviert)   -> 50 - IT & Infrastruktur
}

print("MEILENSTEINE")
print("-" * 76)

for alt, neu in UMZUG.items():
    ms = env['project.milestone'].search([('project_id', '=', alt)])
    if not ms:
        print("  aus Projekt %s: keine gefunden" % alt)
        continue
    ziel = env['project.project'].browse(neu)
    for m in ms:
        status = "erreicht" if m.is_reached else "OFFEN"
        print("  %-58s %-9s %s" % (m.name[:58], str(m.deadline), status))
    ms.write({'project_id': neu})
    print("  -> %d Stueck nach %s\n" % (len(ms), ziel.name))

# --- 2. Anschaffungen in Business ueberfuehren -----------------------------
QUELLE, ZIEL = 109, 163
ERLEDIGT = (6, 35)

print("ANSCHAFFUNGEN & INVESTITIONEN")
print("-" * 76)

alle = env['project.task'].search([('project_id', '=', QUELLE)])
offen = alle.filtered(lambda t: t.stage_id.id not in ERLEDIGT)
print("  im Projekt insgesamt: %d, davon offen: %d" % (len(alle), len(offen)))

if offen:
    offen.write({'project_id': ZIEL})
    print("  %d offene Aufgaben nach '60 - Business, Recht & Finanzen' verschoben" % len(offen))

# Erledigte bleiben liegen - Historie. Das Projekt wird archiviert, nicht
# geloescht: reversibel, und die Auswertungen der Vergangenheit bleiben heil.
rest = env['project.task'].search([('project_id', '=', QUELLE)])
quelle = env['project.project'].browse(QUELLE)
if not offen or len(rest) == len(alle) - len(offen):
    quelle.write({'active': False})
    print("  Projekt '%s' archiviert (%d erledigte Aufgaben bleiben darin)"
          % (quelle.name, len(rest)))

env.cr.commit()
print("")
print("Festgeschrieben.")

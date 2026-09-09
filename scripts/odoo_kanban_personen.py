# -*- coding: utf-8 -*-
# Persoenliche Ansichten + richtige Zustaendigkeiten, 09.09.2026.
#
# Auftrag: "optimiere selbstaendig unser kanban, dass es professionellen
# standards entspricht und sowohl ich als auch franz damit arbeiten koennen"
#
# Zwei Luecken:
#   1. Die heute angelegten Werkstatt-Aufgaben haengen am Agenten (7) statt
#      an Franz (10). Franz sieht seine eigene Arbeit dadurch nicht.
#   2. Es gibt keine persoenliche Ansicht. Wer 199 offene Aufgaben sieht,
#      sieht nichts.

from odoo.tools.safe_eval import safe_eval

WOLF = 6
FRANZ = 10
ERLEDIGT = "(6, 35)"
FREMD = "(106, 107)"        # Vaters Bauprojekt, Arbeitgeber
modell = 'project.task'

Task = env['project.task']
Filter = env['ir.filters']

# --- 1. Werkstatt gehoert Franz -------------------------------------------
WERKSTATT = [1406, 1407, 1408, 1409, 1410, 1411]

print("=" * 74)
print("ZUSTAENDIGKEIT WERKSTATT")
print("=" * 74)
for tid in WERKSTATT:
    t = Task.browse(tid).exists()
    if not t:
        continue
    t.write({'user_ids': [(6, 0, [FRANZ])]})
    print("  #%-5s -> Franz   %s" % (tid, t.name[:50]))

# --- 2. Persoenliche Ansichten --------------------------------------------
def ansicht(name, domain, context):
    werte = {'name': name, 'model_id': modell, 'domain': domain,
             'context': context, 'user_ids': [(6, 0, [])], 'sort': '[]',
             'action_id': False, 'is_default': False}
    v = Filter.search([('name', '=', name), ('model_id', '=', modell)], limit=1)
    if v:
        v.write(werte)
        return 'aktualisiert'
    Filter.create(werte)
    return 'angelegt'


ANSICHTEN = [
    ("\U0001F464 Franz",
     "[('user_ids', 'in', [%d]), ('stage_id', 'not in', %s)]" % (FRANZ, ERLEDIGT),
     "{'group_by': ['stage_id']}"),

    ("\U0001F464 Wolf",
     "[('user_ids', 'in', [%d]), ('stage_id', 'not in', %s)]" % (WOLF, ERLEDIGT),
     "{'group_by': ['stage_id']}"),

    # Das eigentliche Arbeitsbrett: nur FraWo, ohne Vaters Bauprojekt und
    # ohne den Arbeitgeber. Nach Spalte gruppiert = echtes Kanban.
    ("\U0001F3E0 FraWo-Board (ohne Fremdprojekte)",
     "[('project_id', 'not in', %s), ('stage_id', 'not in', %s)]" % (FREMD, ERLEDIGT),
     "{'group_by': ['stage_id']}"),

    # Was laeuft gerade - die WIP-Kontrolle
    ("\U0001F525 Läuft gerade (WIP-Kontrolle)",
     "[('stage_id', '=', 3), ('project_id', 'not in', %s)]" % FREMD,
     "{'group_by': ['user_ids']}"),

    # Niemand zustaendig = niemand macht es
    ("❓ Ohne Zuständigen",
     "[('user_ids', '=', False), ('stage_id', 'not in', %s), "
     "('project_id', 'not in', %s)]" % (ERLEDIGT, FREMD),
     "{'group_by': ['project_id']}"),
]

print("")
print("=" * 74)
print("PERSOENLICHE ANSICHTEN")
print("=" * 74)
for name, domain, ctx in ANSICHTEN:
    zustand = ansicht(name, domain, ctx)
    try:
        n = Task.search_count(safe_eval(domain))
        info = "%d Aufgaben" % n
    except Exception as e:
        info = "!! %s" % str(e)[:40]
    print("  %-13s %-42s %s" % (zustand, name, info))

env.cr.commit()
print("")
print("Festgeschrieben. Sichtbar unter Projekt → Aufgaben → Favoriten.")

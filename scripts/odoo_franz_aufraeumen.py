# -*- coding: utf-8 -*-
# Franz' Liste auf das reduzieren, was er anfassen kann. 09.09.2026.
#
# Wolf: "fuer franz ist das gesamte system ein einziges fragezeichen"
#
# BEFUND
# Franz hat 28 offene Aufgaben zugewiesen. Darunter:
#   [EPIC 2027] Mobile Hybrid-Power ... Notstrom daheim
#   Phase 3 (April 2027): 19-Zoll-Flightcase 24V-Sammelschiene+Inverter
#   [EPIC 2027] Getraenkeautomat mit Nayax: Kiosk-Schwund stoppen
#   Firmenkonzept & Geschaeftsmodell
#   Anker - Miet-Beteiligung
#
# Das ist Planung, Konzeptarbeit und Geschaeftsfuehrung - nichts davon kann
# ein Handwerker in die Hand nehmen. Wer so eine Liste oeffnet, macht sie
# wieder zu.
#
# GRUNDSATZ (Standard in jedem Betrieb mit getrennten Rollen)
#   Wolf besitzt Planung, Konzept, Kaufmaennisches.
#   Franz besitzt, was in der Werkstatt oder auf dem Job passiert.
#   Ein Epic ist nie eine Arbeitsanweisung - es ist eine Klammer.
#
# Franz bleibt Mitleser (follower), wo es ihn betrifft - er verliert also
# keine Information, nur die falsche Zustaendigkeit.

WOLF = 6
FRANZ = 10

# Was NICHT auf Franz' Liste gehoert, mit Grund
ABGEBEN = {
    1046: 'Epic 2027 Hybrid-Power - Klammer, keine Arbeitsanweisung',
    1047: 'Epic 2027 Getraenkeautomat - Konzept, nicht Werkstatt',
    1048: 'Epic Verleih - Klammer ueber viele Aufgaben',
    1040: 'Epic Rothkreuz 14 OG - Klammer',
    1183: 'Nayax Phase 3 RFID 2027 - Softwarethema',
    1188: 'Mietvertrag ausdrucken - kaufmaennisch',
    780:  'Firmenkonzept - Geschaeftsfuehrung',
    222:  'Miet-Beteiligung Anker - kaufmaennisch',
    824:  'Fixkosten-Tracking - kaufmaennisch',
}

Task = env['project.task']
Filter = env['ir.filters']

vorher = Task.search_count([('user_ids', 'in', [FRANZ]),
                            ('stage_id', 'not in', (6, 35))])

print("=" * 74)
print("FRANZ' LISTE AUFRAEUMEN")
print("=" * 74)
print("  vorher: %d offene Aufgaben" % vorher)
print("")

for tid, grund in sorted(ABGEBEN.items()):
    t = Task.browse(tid).exists()
    if not t or FRANZ not in t.user_ids.ids:
        continue
    # Zustaendigkeit zu Wolf, Franz bleibt Mitleser
    t.write({'user_ids': [(6, 0, [WOLF])]})
    t.message_subscribe(partner_ids=[env['res.users'].browse(FRANZ).partner_id.id])
    print("  #%-5s -> Wolf   %s" % (tid, grund[:54]))

nachher = Task.search_count([('user_ids', 'in', [FRANZ]),
                             ('stage_id', 'not in', (6, 35))])
aktiv = Task.search_count([('user_ids', 'in', [FRANZ]),
                           ('stage_id', 'in', (2, 3, 5))])

print("")
print("  nachher: %d zugewiesen, davon %d aktiv (Als Naechstes / In Arbeit / Blockiert)"
      % (nachher, aktiv))

# --- Franz' Ansicht: nur was wirklich ansteht -----------------------------
# Backlog und Ideen bewusst NICHT - das ist Wolfs Vorrat, nicht Franz' Arbeit.
werte = {
    'name': '\U0001F528 Franz — was ansteht',
    'model_id': 'project.task',
    'domain': "[('user_ids', 'in', [%d]), ('stage_id', 'in', (2, 3, 5))]" % FRANZ,
    'context': "{'group_by': ['stage_id']}",
    'user_ids': [(6, 0, [])],
    'sort': '[]',
    'action_id': False,
    'is_default': False,
}
v = Filter.search([('name', '=', werte['name']),
                   ('model_id', '=', 'project.task')], limit=1)
if v:
    v.write(werte)
    print("")
    print("  Ansicht aktualisiert: %s (%d Aufgaben)" % (werte['name'], aktiv))
else:
    Filter.create(werte)
    print("")
    print("  Ansicht angelegt: %s (%d Aufgaben)" % (werte['name'], aktiv))

env.cr.commit()
print("")
print("Festgeschrieben.")

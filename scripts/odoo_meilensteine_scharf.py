# -*- coding: utf-8 -*-
# Meilensteine scharf stellen - was die Kette aufgedeckt hat. 09.09.2026.
#
# Die Meilensteinkette hat zwei Dinge sichtbar gemacht, die vorher niemand
# sehen konnte. Beide werden hier korrigiert.
#
# BEFUND 1 - Projekt 159 hat NICHT ein Ziel, sondern zwei.
#
#   Ich hatte dem Studio-Projekt einen einzigen Meilenstein gegeben:
#   "Studio bespielbar", 30.06.2027. Ein Blick in die Spalte zeigt, dass das
#   falsch ist. In "Als Naechstes" liegen dort drei voellig verschiedene Dinge:
#
#     - Wohnungsabnahme Lu Maier          Frist 15.09.2026  (in sechs Tagen)
#     - Server ins OG, bevor es kalt wird  Frist 20.09.2026
#     - Studioausbau und Akustik           2027
#
#   Der Serverumzug ist kein Studio-Thema. Er ist Frostschutz: die Abwaerme
#   der 24/7-Hardware haelt das leerstehende OG ueber Null. Wer das im
#   Oktober macht statt im September, heizt den Winter ueber mit Strom oder
#   riskiert Schimmel. Unter einem Ziel im Juni 2027 war das unsichtbar.
#
#   Zwei Ziele, zwei Meilensteine. So sind Meilensteine gemeint.
#
# BEFUND 2 - Radio ist nicht unwichtig, es ist ABGESCHALTET.
#
#   Neun Radio-Aufgaben standen auf "Als Naechstes". Gemessen, nicht geraten:
#     funk.frawo.tech antwortet mit 502
#     keine AzuraCast-VM laeuft (VM 210 auf dem Anker ist Home Assistant)
#     CT120 Musikserver existiert nicht mehr
#   Die Radio-Maschine ist mit dem ProDesk gestorben und wartet auf den
#   OptiPlex. Solange kann daran niemand arbeiten.
#
#   "Als Naechstes" haette bedeutet: das koennte ich morgen anfangen. Kann
#   ich nicht. Richtig ist "Blockiert" mit genanntem Blocker - dann steht im
#   Brett, WARUM nichts passiert, statt dass es nach Traegheit aussieht.
#
# Nichts wird geloescht, nichts erledigt. Alles ist eine Stufe oder eine
# Zuordnung - jederzeit zurueckdrehbar.

BLOCKIERT = 5
BACKLOG = 1
STUDIO = 159

Milestone = env['project.milestone']
Task = env['project.task']

print("=" * 78)
print("MEILENSTEINE SCHARF STELLEN")
print("=" * 78)


def stufe(tid, ziel, grund):
    t = Task.browse(tid).exists()
    if not t:
        print("  #%-5s fehlt" % tid)
        return 0
    if t.stage_id.id == ziel:
        return 0
    alt = t.stage_id.name
    try:
        t.write({'stage_id': ziel})
    except Exception as e:
        print("  #%-5s !! %s" % (tid, str(e)[:56]))
        return 0
    t.message_post(body='&#129302; [Claude] %s' % grund,
                   message_type='comment', subtype_xmlid='mail.mt_note')
    print("  #%-5s %-13s -> %-13s %s" % (tid, alt[:13], t.stage_id.name[:13],
                                         grund[:38]))
    return 1


# --- 1. Projekt 159 bekommt sein zweites, naeheres Ziel --------------------
print("")
print("1. OG-UEBERNAHME - eigenes Ziel, sechs Tage entfernt")
print("-" * 78)

og = Milestone.search([('project_id', '=', STUDIO),
                       ('name', 'like', 'OG uebernommen')], limit=1)
if not og:
    og = Milestone.create({
        'project_id': STUDIO,
        'name': 'OG uebernommen - Wohnung abgenommen, Server steht oben',
        'deadline': '2026-09-30',
    })
    print("  angelegt: %s  (30.09.2026)" % og.name)
else:
    og.write({'deadline': '2026-09-30'})
    print("  vorhanden: %s  (30.09.2026)" % og.name)

# Was auf die Uebernahme einzahlt - und was beim Studio bleibt.
# 1044 (AirBnB vs. Eigennutzung) gehoert hierher: die Frage entscheidet,
# wofuer das OG ueberhaupt hergerichtet wird. Sie kommt VOR dem Ausbau.
ZUR_UEBERNAHME = {
    1040: 'Klammer OG - Abnahme, Serverumzug, Ausbau',
    1041: 'Serverumzug = Frostschutz, Frist 20.09.',
    1175: 'Rack-Platz im OG - Voraussetzung Serverumzug',
    1176: 'Netzwerk ins OG - Voraussetzung Serverumzug',
    1177: 'Temperaturueberwachung - misst, ob der Frostschutz wirkt',
    1258: 'Drohnenfotos an Lu - gehoert zur Uebergabe',
    1044: 'AirBnB oder Eigennutzung - entscheidet, wofuer ausgebaut wird',
}
zu = 0
for tid, grund in ZUR_UEBERNAHME.items():
    t = Task.browse(tid).exists()
    if not t:
        continue
    try:
        t.write({'milestone_id': og.id})
        zu += 1
    except Exception as e:
        print("     #%-5s !! %s" % (tid, str(e)[:52]))
print("  %d Aufgaben zahlen auf die Uebernahme ein" % zu)

# Die drei Teilrecherchen zu 1044 sind Zuarbeit, nicht Naechstes.
for tid in (1169, 1170, 1171):
    stufe(tid, BACKLOG,
          'Zuarbeit zur Machbarkeitsfrage #1044 - erst wenn die Frage drankommt')

print("")
print("  beim Studio-Ziel (30.06.2027) bleiben:")
for t in Task.search([('project_id', '=', STUDIO),
                      ('stage_id', 'not in', (6, 35)),
                      ('id', 'not in', list(ZUR_UEBERNAHME.keys()))]):
    print("     %-58s %s" % (t.name[:58], t.stage_id.name[:14]))


# --- 2. Radio: der Blocker gehoert ins Brett ------------------------------
print("")
print("2. RADIO - kein Unwille, sondern fehlende Hardware")
print("-" * 78)

HARDWARE = ('Blockiert: die Radio-Maschine ist mit dem ProDesk gestorben. '
            'funk.frawo.tech antwortet 502, es laeuft keine AzuraCast-VM, '
            'CT120 gibt es nicht mehr. Geht weiter, sobald der OptiPlex '
            'steht. Vorher ist das keine Aufgabe, sondern ein Wunsch.')
for tid in (467, 529, 1261, 1263, 1295, 1300):
    stufe(tid, BLOCKIERT, HARDWARE)

# Diese zwei warten nicht auf Hardware, sondern auf eine Entscheidung.
stufe(1268, BLOCKIERT,
      'Untersuchung ist fertig, drei Fragen im Text warten auf Wolfs Antwort')
stufe(1123, BLOCKIERT,
      'Ist eine Entscheidung, keine Arbeit - wartet auf Wolf')

# --- 3. Klammern sind keine Arbeitsanweisung ------------------------------
print("")
print("3. VORHABEN-KLAMMERN raus aus 'Als Naechstes'")
print("-" * 78)
for tid in (1090, 1091, 1048, 927):
    stufe(tid, BACKLOG,
          'Ein Vorhaben / Epic ist eine Klammer ueber viele Aufgaben, '
          'nichts das man direkt anfassen kann')

t1048 = Task.browse(1048).exists()
if t1048 and not t1048.milestone_id:
    t1048.write({'milestone_id': 10})
t927 = Task.browse(927).exists()
if t927 and not t927.milestone_id:
    t927.write({'milestone_id': 6})


# --- Kontrolle ------------------------------------------------------------
print("")
print("=" * 78)
print("KETTE DANACH")
print("=" * 78)
for m in Milestone.search([('is_reached', '=', False)], order='deadline'):
    n = Task.search_count([('milestone_id', '=', m.id),
                           ('stage_id', 'not in', (6, 35))])
    print("  %-10s %-56s %3d offen" % (str(m.deadline), m.name[:56], n))

ohne = Task.search([('milestone_id', '=', False),
                    ('stage_id', 'in', (2, 3)),
                    ('project_id', 'not in', (106, 107))])
print("")
print("  noch ohne Ziel und trotzdem machbar: %d" % len(ohne))
for t in ohne:
    print("     %-56s %s" % (t.name[:56], (t.project_id.name or '')[:22]))

env.cr.commit()
print("")
print("Festgeschrieben.")

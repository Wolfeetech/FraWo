# -*- coding: utf-8 -*-
# WIP-Grenze durchsetzen, 09.09.2026.
#
# Auftrag von Wolf: "arbeite als professioneller unternehmensberater und planer
# und optimiere selbstaendig unser kanban, dass es professionellen standards
# entspricht und sowohl ich als auch franz damit arbeiten koennen"
#
# BEFUND
# 19 Aufgaben standen gleichzeitig auf "In Arbeit" - bei zwei Leuten im
# Feierabend. Das ist keine Spalte mehr, sondern eine Wunschliste. Ein Board
# mit unbegrenztem WIP zeigt nicht, woran gearbeitet wird, sondern woran man
# gern arbeiten wuerde.
#
# Die Alterung (rotting) half bei der Auswahl nicht: ich selbst habe heute
# fast alle angefasst, das setzt write_date zurueck. Also nach INHALT.
#
# REGEL, die hier angewendet wird
#   "In Arbeit" heisst: jemand arbeitet DIESE WOCHE daran.
#   Alles andere ist "Als Naechstes" - geplant, aber nicht begonnen.
#
# Drei Gruppen wandern zurueck:
#   1. Buchhaltungsvorgaenge, die auf Wolf warten (Rechnungen, Belege, EUER)
#   2. Aufgaben, die ICH heute angelegt habe und die auf eine Entscheidung
#      warten - die haette ich nie auf "In Arbeit" setzen duerfen
#   3. Die drei Doppelfuehrungen aus dem Business-Projekt (#1221-1223), die
#      dieselben Vorgaenge fuehren wie #377/#374/#381/#380
#
# Nichts wird geloescht, nichts erledigt - nur die Spalte stimmt danach.

ALS_NAECHSTES = 2

ZURUECK = {
    # 1. Buchhaltung - wartet auf Wolf, laeuft nicht
    992:  'Rechnung WWZ - wartet auf Bearbeitung',
    996:  'Inkasso-Vorgang KOHL/Delta - wartet auf Bearbeitung',
    152:  'Lieferrechnung Freigabe - wartet auf Entscheidung',
    222:  'Miet-Beteiligung Anker - wartet auf Klaerung',
    1189: 'Beleg-Zuordnung N26 - wartet auf Bearbeitung',
    824:  'Fixkosten-Tracking - wartet auf Bearbeitung',
    1362: 'EUER 2026 - haengt am Kontenimport (#1371)',
    1365: 'Stromanteil Shelly - wartet auf Wolfs Freigabe',

    # 2. Heute von mir angelegt, wartet auf Wolfs Entscheidung
    1405: 'Transport klaeren - wartet auf Entscheidung im Franz-Gespraech',
    1413: 'Erste 20 Kunden - wartet auf die Namensliste',
    1292: 'Investitionsplan - wartet auf Budget und Reihenfolge',

    # 3. Doppelfuehrung - dieselben Vorgaenge wie #377/#374/#381/#380
    1221: 'Doppelfuehrung zu #377 (CX2) - zusammenlegen',
    1222: 'Doppelfuehrung zu #374/#381 (Sub-Upgrade) - zusammenlegen',
    1223: 'Doppelfuehrung zu #380 (RS232) - zusammenlegen',
}

# Bleibt bewusst auf "In Arbeit" - daran wird tatsaechlich gearbeitet:
#   1357  ProDesk-Wiederanlauf (laeuft seit 07.09.)
#   1048  Verleih-Epic (Klammer, wird bearbeitet)
#   1389  Sicherheitsstandards (heute mehrfach vorangekommen)
#   1415  Hausordnung Odoo (heute angelegt und in Anwendung)
#   1371  Kontenimport (naechster grosser Schritt)

Task = env['project.task']

vorher = Task.search_count([('stage_id', '=', 3)])
print("=" * 74)
print("WIP-GRENZE DURCHSETZEN")
print("=" * 74)
print("  vorher auf 'In Arbeit': %d" % vorher)
print("")

verschoben = 0
for tid, grund in sorted(ZURUECK.items()):
    t = Task.browse(tid).exists()
    if not t:
        print("  #%-5s fehlt" % tid)
        continue
    if t.stage_id.id != 3:
        print("  #%-5s steht nicht auf 'In Arbeit' - uebersprungen" % tid)
        continue
    t.write({'stage_id': ALS_NAECHSTES})
    t.message_post(
        body=('&#129302; [Claude] Von „In Arbeit“ nach „Als Nächstes“ '
              'verschoben: %s.<br/>WIP-Grenze eingeführt — „In Arbeit“ '
              'heißt ab jetzt: es wird diese Woche daran gearbeitet. '
              'Inhaltlich unverändert.' % grund),
        message_type='comment', subtype_xmlid='mail.mt_note')
    print("  #%-5s -> Als Naechstes   %s" % (tid, grund[:52]))
    verschoben += 1

nachher = Task.search_count([('stage_id', '=', 3)])
print("")
print("  verschoben: %d" % verschoben)
print("  jetzt auf 'In Arbeit': %d  (Grenze 6)" % nachher)
if nachher > 6:
    print("  HINWEIS: noch ueber der Grenze - Rest gehoert Wolf/Franz zur Entscheidung")

env.cr.commit()
print("")
print("Festgeschrieben.")

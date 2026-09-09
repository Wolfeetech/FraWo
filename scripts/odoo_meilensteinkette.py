# -*- coding: utf-8 -*-
# Meilensteine als Prioritaetsrueckgrat - fuer ALLE Aufgaben. 09.09.2026.
#
# Wolf: "ausserdem fehlt ja die priorisierung .. deshalb sind die meilensteine
# fuer mich glaub grad so wichtig" und danach: "du bist zu sehr auf die wenigen
# aufgaben eingefahren ... mir gehts um alles!"
#
# Beides richtig. Der erste Versuch hat fuenfzehn handverlesene Aufgaben
# verknuepft - das ist Dekoration, keine Priorisierung.
#
# DIE REGEL, die hier auf den GESAMTEN Bestand angewendet wird:
#
#   Was JETZT machbar ist (Stufe "Als Naechstes" oder "In Arbeit"),
#   zahlt auf das aktuelle Ziel des Projekts ein.
#   Was im Backlog oder in Ideen liegt, ist Vorrat und bleibt unverknuepft.
#
# Damit beantwortet der Meilenstein die Frage "warum mache ich das?" fuer
# jede einzelne Aufgabe, an der gerade gearbeitet wird. Und was sich keinem
# Ziel zuordnen laesst, faellt auf - das ist der eigentliche Gewinn.
#
# DIE KETTE, bewusst in dieser Reihenfolge - jeder Schritt macht den
# naechsten erst moeglich oder guenstiger:
#   1. Buchhaltung  ohne Zahlen keine Entscheidung
#   2. CI           entsperrt Google Business und das Namensschild
#   3. Werkstatt    Franz' Verdienstfaehigkeit, ohne Fahrzeug nutzbar
#   4. Verleih      braucht Einmessung, Pakete, Kisten
#   5. Studio       teuer, braucht Vorlauf
#
# HINWEIS: project.task.milestone_id ist an die Gruppe
# project.group_project_milestone gekoppelt. Ohne sie existiert das Feld
# fuer den Benutzer nicht - der erste Lauf scheiterte daran mit
# KeyError: 'milestone_id'.

import datetime
import traceback

Milestone = env['project.milestone']
Project = env['project.project']
Task = env['project.task']

MACHBAR = (2, 3)          # Als Naechstes, In Arbeit
ERLEDIGT = (6, 35)

KETTE = [
    (163, 'Buchhaltung schliesst - Kontobewegungen importiert', '2026-09-30'),
    (110, 'CI steht - Namensschild kann produziert werden',      '2026-10-31'),
    (160, 'Werkstatt arbeitsfaehig - erste Reparatur selbst gemacht', '2026-12-15'),
    (104, 'Verleih vorzeigbar - ein Paket komplett, eingemessen, mit Preis', '2027-03-31'),
    (159, 'Studio bespielbar - erste eigene Aufnahme',           '2027-06-30'),
    (105, 'Fangnetz steht - Sicherungen geprueft, Alarme kommen an', '2026-10-15'),
]

print("=" * 78)
print("MEILENSTEINKETTE - alle machbaren Aufgaben zuordnen")
print("=" * 78)

for projekt_id, name, datum in KETTE:
    p = Project.browse(projekt_id).exists()
    if not p:
        print("  Projekt %s fehlt" % projekt_id)
        continue
    if not p.allow_milestones:
        p.write({'allow_milestones': True})

    m = Milestone.search([('project_id', '=', projekt_id),
                          ('is_reached', '=', False)], limit=1)
    if m and not m.name.startswith('[FREMD]'):
        m.write({'name': name, 'deadline': datum})
        zustand = 'aktualisiert'
    else:
        m = Milestone.create({'project_id': projekt_id, 'name': name,
                              'deadline': datum})
        zustand = 'angelegt'

    # ALLE machbaren Aufgaben des Projekts - nicht eine Auswahl.
    # Einzeln schreiben mit Fehlerfang: eine stolpernde Automatik darf nicht
    # den ganzen Lauf killen. Wer scheitert, wird genannt.
    offen = Task.search([('project_id', '=', projekt_id),
                         ('stage_id', 'in', MACHBAR),
                         ('milestone_id', '=', False)])
    gelungen, gescheitert = 0, []
    for t in offen:
        try:
            t.write({'milestone_id': m.id})
            gelungen += 1
        except Exception as e:
            gescheitert.append((t.id, t.name[:44], str(e)[:60]))
    offen = Task.browse([t.id for t in offen])

    vorrat = Task.search_count([('project_id', '=', projekt_id),
                                ('stage_id', 'not in', ERLEDIGT),
                                ('stage_id', 'not in', MACHBAR)])
    print("")
    print("  %-12s %s" % (zustand, name[:62]))
    print("               %-44s %s" % (p.name[:44], datum))
    print("               %3d Aufgaben zahlen darauf ein, %d im Vorrat"
          % (gelungen, vorrat))
    for tid, nm, err in gescheitert:
        print("               !! #%-5s %-44s %s" % (tid, nm, err))

# --- Kontrolle -------------------------------------------------------------
print("")
print("=" * 78)
print("STAND")
print("=" * 78)
heute = datetime.date.today()
for m in Milestone.search([('is_reached', '=', False)], order='deadline'):
    n = Task.search_count([('milestone_id', '=', m.id),
                           ('stage_id', 'not in', ERLEDIGT)])
    marke = '  UEBERFAELLIG' if m.deadline and m.deadline < heute else ''
    print("  %-10s %-54s %3d offen%s"
          % (str(m.deadline), m.name[:54], n, marke))

ohne = Task.search([('milestone_id', '=', False),
                    ('stage_id', 'in', MACHBAR),
                    ('project_id', 'not in', (106, 107))])
print("")
print("  %d machbare Aufgaben zahlen auf KEIN Ziel ein:" % len(ohne))
for t in ohne[:12]:
    print("     %-58s %s" % (t.name[:58], (t.project_id.name or '')[:24]))
if len(ohne) > 12:
    print("     ... und %d weitere" % (len(ohne) - 12))
print("")
print("  Das ist die eigentliche Priorisierungsfrage: Vorrat - oder fehlt ein Ziel?")

env.cr.commit()
print("")
print("Festgeschrieben.")

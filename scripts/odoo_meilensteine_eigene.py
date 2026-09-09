# -*- coding: utf-8 -*-
# Meilensteine dorthin, wo FraWo selbst liefert. 09.09.2026.
#
# Wolf: "das einzige projekt mit meilensteinen ist das, wo ich selbst nur einen
# job habe und der rest nur meinen vater betrifft ... die projekte die wir
# selbst umsetzen muessen und koennen haben noch keine ... was soll das?"
#
# Nachgemessen, er hat recht:
#   Projekt 106 (Stockenweiler, Vaters Waermepumpe)  5 Meilensteine, alle offen
#   Projekt 105 (IT, Paperless)                      1
#   Auftraege, Werkstatt, Studio, Radio, Business    0
#
# Von den fuenf in Stockenweiler sind M1, M2, M3 und M5 FREMDGEWERKE
# (Netzanfrage, Montage Kaelte/Elektro, Ploembierung). FraWo schuldet dort
# genau einen Punkt: M4, die Modbus-Einbindung nach abgeschlossener Montage.
#
# Was dieses Skript tut:
#   1. Die vier Fremdgewerke-Meilensteine kennzeichnen, damit im Tagesbericht
#      erkennbar ist, dass sie nicht FraWos Arbeit sind.
#   2. Vier Meilensteine dort anlegen, wo FraWo tatsaechlich liefert.
#
# Die Termine sind VORLAEUFIG und im Gespraech mit Franz (#1414) zu
# bestaetigen. Ein Meilenstein ohne Datum geht in Odoo nicht - lieber ein
# vorlaeufiges Datum, das man korrigiert, als gar keine Zielmarke.

import datetime

Milestone = env['project.milestone']
Project = env['project.project']

# --- 1. Fremdgewerke kennzeichnen -----------------------------------------
FREMD = {
    1: 'M1: Netzanfrage & Zaehlerspezifikation abgeschlossen',
    2: 'M2: Ortstermin & Gewerke-Koordination abgeschlossen',
    3: 'M3: Montage Kaelte, Elektro & LAN abgeschlossen',
    5: 'M5: Zaehler plombiert, Systemabnahme & Projektabschluss',
}

print("=" * 78)
print("FREMDGEWERKE KENNZEICHNEN (Stockenweiler)")
print("=" * 78)

for mid, _alt in FREMD.items():
    m = Milestone.browse(mid).exists()
    if not m:
        print("  #%s fehlt" % mid)
        continue
    if not m.name.startswith('[FREMD]'):
        m.write({'name': '[FREMD] ' + m.name})
    print("  #%-3s %s" % (mid, m.name[:66]))

print("")
print("  Diese vier liegen beim Heizungsbauer und beim Bauherrn, nicht bei FraWo.")
print("  Nur M4 (Modbus-TCP EMS) ist FraWo-Arbeit - bleibt unveraendert.")

# --- 2. Eigene Meilensteine anlegen ---------------------------------------
# Nur dort, wo FraWo selbst liefert und liefern kann.
EIGENE = [
    (110, 'CI steht - Namensschild kann produziert werden', '2026-10-31',
     'Blockiert aktuell das Google-Business-Video (#465). Ohne Wortmarke, '
     'Bildmarke, Farben und Schrift kein Schild - und ohne Schild kein Video, '
     'das man nur einmal dreht.'),

    (163, 'Buchhaltung schliesst - Kontobewegungen importiert', '2026-09-30',
     'In die Buchhaltung wurde noch NIE eine Kontobewegung importiert (#1371). '
     'Solange das so bleibt, ist jede Zahl eine Schaetzung und jede EUER '
     'Handarbeit. Ein Nachmittag Aufwand.'),

    (160, 'Werkstatt arbeitsfaehig - erste Reparatur selbst gemacht', '2026-12-15',
     'Vier Anschaffungen fuer 1.250-2.150 EUR (#1406), danach die erste '
     'Reparatur komplett in der eigenen Werkstatt. Das ist das Standbein, '
     'das OHNE Fuehrerschein funktioniert - Reparatur ist ein Bringgeschaeft.'),

    (104, 'Erstes Verleihpaket vermietbar', '2027-03-31',
     'Vermietbar heisst: eingemessen, zusammengestellt, kalkuliert, Kisten '
     'gepackt - in dieser Reihenfolge. Aktuell fehlt die realistische Messung '
     'der Anlagen, deshalb sind die Kisten (#1051) zu Recht blockiert.'),
]

print("")
print("=" * 78)
print("EIGENE MEILENSTEINE ANLEGEN")
print("=" * 78)

for projekt_id, name, datum, begruendung in EIGENE:
    p = Project.browse(projekt_id).exists()
    if not p:
        print("  Projekt %s fehlt - uebersprungen" % projekt_id)
        continue

    # Meilensteine brauchen allow_milestones am Projekt, sonst sind sie
    # angelegt aber unsichtbar - derselbe Fehlertyp wie bei den Stufen.
    if not p.allow_milestones:
        p.write({'allow_milestones': True})
        print("  (allow_milestones fuer '%s' eingeschaltet)" % p.name[:40])

    vorhanden = Milestone.search([('project_id', '=', projekt_id),
                                  ('name', '=', name)], limit=1)
    if vorhanden:
        vorhanden.write({'deadline': datum})
        zustand = 'aktualisiert'
        m = vorhanden
    else:
        m = Milestone.create({'project_id': projekt_id, 'name': name,
                              'deadline': datum})
        zustand = 'angelegt'

    print("  %-12s %-46s %s" % (zustand, name[:46], datum))
    print("               %s" % begruendung[:74])

# --- 3. Kontrolle ---------------------------------------------------------
print("")
print("=" * 78)
print("STAND")
print("=" * 78)
heute = datetime.date.today()
for m in Milestone.search([], order='project_id, deadline'):
    fremd = m.name.startswith('[FREMD]')
    faellig = m.deadline and m.deadline < heute and not m.is_reached
    kennz = 'FREMD ' if fremd else '      '
    marke = 'UEBERFAELLIG' if faellig else ''
    print("  %s%-42s %-10s %-30s %s"
          % (kennz, m.name[:42], str(m.deadline),
             (m.project_id.name or '')[:30], marke))

env.cr.commit()
print("")
print("Festgeschrieben. Termine sind vorlaeufig - im Gespraech mit Franz")
print("(#1414) bestaetigen oder korrigieren.")

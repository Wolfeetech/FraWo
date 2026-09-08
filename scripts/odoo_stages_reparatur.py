# -*- coding: utf-8 -*-
# Reparatur 08.09.2026: Beim Neuzuschnitt der Projekte verloren 60 Aufgaben
# ihre Stage.
#
# Ursache: In Odoo haengen die Stages (project.task.type) ueber ein
# many2many an den Projekten. Die neu angelegten Projekte 160/161/162 hatten
# noch KEINE Stage verknuepft - beim Verschieben setzt Odoo stage_id deshalb
# auf leer, weil es im Zielprojekt keine gueltige Stage findet.
#
# Nebeneffekt, der den Fehler zunaechst verdeckt hat: In SQL ist
#   stage_id NOT IN (6,35)
# fuer stage_id IS NULL nicht "wahr", sondern unbekannt. Die betroffenen
# Aufgaben fielen damit aus jeder Auswertung offener Aufgaben heraus -
# sie waren unsichtbar, nicht nur unsortiert.
#
# Zwei Schritte:
#   1. Die vorhandenen Stages mit den neuen Projekten verknuepfen.
#   2. Fuer jede Aufgabe ohne Stage die vorherige aus der Aenderungshistorie
#      (mail.tracking.value) zurueckholen. Nur wo nichts zu finden ist,
#      wird auf Backlog gesetzt - und das wird gemeldet.

NEUE_PROJEKTE = [160, 161, 162]
FALLBACK_STAGE = 1   # Backlog

# --- 1. Stages an die neuen Projekte haengen -------------------------------
# Wir nehmen die Stages, die die etablierten Projekte benutzen.
vorbild = env['project.project'].browse(104)
stages = env['project.task.type'].search([('project_ids', 'in', vorbild.id)])
print("Stages vom Vorbildprojekt: %s" % ", ".join(s.name for s in stages))

for st in stages:
    st.write({'project_ids': [(4, p) for p in NEUE_PROJEKTE]})
print("An %d Projekte gehaengt." % len(NEUE_PROJEKTE))

# --- 2. Verlorene Stages zurueckholen --------------------------------------
# Nur Aufgaben MIT Projekt anfassen. Private Aufgaben ohne Projekt haben
# bewusst keine stage_id - sie nutzen persoenliche Phasen, und ein Schreiben
# darauf quittiert Odoo mit "Sie koennen eine persoenliche Phase nur bei
# einer privaten Aufgabe einstellen".
ohne = env['project.task'].search([
    ('stage_id', '=', False), ('project_id', '!=', False)])
print("")
print("Aufgaben ohne Stage: %d" % len(ohne))
print("")

feld = env['ir.model.fields'].search([
    ('model', '=', 'project.task'), ('name', '=', 'stage_id')], limit=1)

wiederhergestellt = 0
geraten = []

for t in ohne:
    alt = None
    if feld:
        spur = env['mail.tracking.value'].search([
            ('field_id', '=', feld.id),
            ('mail_message_id.model', '=', 'project.task'),
            ('mail_message_id.res_id', '=', t.id),
        ], order='id desc', limit=1)
        if spur and spur.old_value_integer:
            alt = spur.old_value_integer

    if alt:
        t.write({'stage_id': alt})
        wiederhergestellt += 1
    else:
        t.write({'stage_id': FALLBACK_STAGE})
        geraten.append((t.id, t.name[:56]))

print("Aus der Historie zurueckgeholt: %d" % wiederhergestellt)
print("Auf Backlog gesetzt (keine Historie): %d" % len(geraten))

if geraten:
    print("")
    print("Diese bitte gegenpruefen:")
    for tid, name in geraten:
        print("  %-5s %s" % (tid, name))

env.cr.commit()
print("")
print("Festgeschrieben.")

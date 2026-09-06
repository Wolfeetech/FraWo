res = []
Event = env['calendar.event'].sudo()
Activity = env['mail.activity'].sudo()
for rec in records:
    if rec.stage_id.id not in (6, 35):
        continue
    evs = Event.search([('res_model', '=', 'project.task'), ('res_id', '=', rec.id), ('active', '=', True)])
    open_activities = Activity.search([
        ('res_model', '=', 'project.task'),
        ('res_id', '=', rec.id),
        ('calendar_event_id', 'in', evs.ids),
        ('active', '=', True),
    ])
    for act in open_activities:
        act.action_feedback(feedback='Aufgabe erledigt/abgebrochen, Rückmeldung entfällt.')
    if evs:
        evs.write({'active': False})
        res.append('%s: %s Termin(e) archiviert, %s Rückmeldung(en) geschlossen' % (rec.name, len(evs), len(open_activities)))
env['ir.config_parameter'].sudo().set_param('frawo.mcp.diag', ' ;; '.join(res) if res else 'kein Treffer (keine Frist-Termine oder Stage nicht erledigt/abgebrochen)')

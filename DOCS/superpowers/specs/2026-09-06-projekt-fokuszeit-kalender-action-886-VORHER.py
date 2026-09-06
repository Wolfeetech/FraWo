res = []
Event = env['calendar.event'].sudo()
for rec in records:
    if rec.stage_id.id not in (6, 35):
        continue
    evs = Event.search([('res_model', '=', 'project.task'), ('res_id', '=', rec.id), ('active', '=', True)])
    if evs:
        evs.write({'active': False})
        res.append('%s: %s Termin(e) archiviert' % (rec.name, len(evs)))
env['ir.config_parameter'].sudo().set_param('frawo.mcp.diag', ' ;; '.join(res) if res else 'kein Treffer (keine Frist-Termine oder Stage nicht erledigt/abgebrochen)')

if record.date_deadline and record.user_ids:
    existing = env['calendar.event'].search([('res_model_id', '=', 522), ('res_id', '=', record.id)], limit=1)
    if existing:
        existing.write({'start': record.date_deadline, 'stop': record.date_deadline, 'allday': True})
    else:
        for user in record.user_ids:
            env['calendar.event'].create({
                'name': '⏰ Frist: ' + record.name,
                'start': record.date_deadline,
                'stop': record.date_deadline,
                'allday': True,
                'user_id': user.id,
                'partner_ids': [(4, user.partner_id.id)],
                'res_model_id': 522,
                'res_id': record.id,
            })
elif not record.date_deadline:
    env['calendar.event'].search([('res_model_id', '=', 522), ('res_id', '=', record.id)]).unlink()

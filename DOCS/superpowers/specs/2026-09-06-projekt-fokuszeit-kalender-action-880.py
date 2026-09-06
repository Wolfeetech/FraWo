WORK_START, WORK_END = 8, 18
PROJECT_TASK_MODEL_ID = 522
FOKUSZEIT_CATEG_ID = 8


def find_free_slot(env, user, duration_hours, deadline, exclude_event_id=None):
    if duration_hours <= 0 or not deadline:
        return None, None
    duration = datetime.timedelta(hours=duration_hours)
    day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    limit = day + datetime.timedelta(days=30)
    Event = env['calendar.event']
    while day < limit:
        if day.weekday() < 5:
            slot_end_of_day = day.replace(hour=WORK_END)
            candidate = day.replace(hour=WORK_START)
            while candidate + duration <= slot_end_of_day and candidate + duration <= deadline:
                domain = [
                    ('user_id', '=', user.id),
                    ('active', '=', True),
                    ('start', '<', candidate + duration),
                    ('stop', '>', candidate),
                ]
                if exclude_event_id:
                    domain.append(('id', '!=', exclude_event_id))
                clash = Event.search_count(domain)
                if not clash:
                    return candidate, candidate + duration
                candidate += datetime.timedelta(minutes=30)
        day += datetime.timedelta(days=1)
    return None, None


def build_description(record):
    parts = []
    if record.project_id:
        parts.append('<p><b>Projekt:</b> %s</p>' % record.project_id.name)
    if record.description:
        parts.append(record.description[:500])
    parts.append('<p><a href="/odoo/project.task/%d">Aufgabe in Odoo oeffnen</a></p>' % record.id)
    return ''.join(parts)


if record.date_deadline and record.user_ids:
    description = build_description(record)
    for user in record.user_ids:
        existing = env['calendar.event'].search([
            ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
            ('res_id', '=', record.id),
            ('user_id', '=', user.id),
        ], limit=1)

        slot_start, slot_end = find_free_slot(env, user, record.allocated_hours, record.date_deadline, existing.id if existing else None)

        if slot_start and slot_end:
            vals = {
                'name': (record.project_id.name + ' · ' + record.name) if record.project_id else record.name,
                'description': description,
                'start': slot_start,
                'stop': slot_end,
                'duration': (slot_end - slot_start).total_seconds() / 3600.0,
                'allday': False,
                'user_id': user.id,
                'partner_ids': [(4, user.partner_id.id)],
                'res_model_id': PROJECT_TASK_MODEL_ID,
                'res_id': record.id,
                'categ_ids': [(6, 0, [FOKUSZEIT_CATEG_ID])],
            }
        else:
            vals = {
                'name': '⏰ Frist: ' + record.name,
                'description': description,
                'start': record.date_deadline,
                'stop': record.date_deadline,
                'duration': 0,
                'allday': True,
                'user_id': user.id,
                'partner_ids': [(4, user.partner_id.id)],
                'res_model_id': PROJECT_TASK_MODEL_ID,
                'res_id': record.id,
                'categ_ids': [(6, 0, [FOKUSZEIT_CATEG_ID])],
            }
            record.message_post(body='⚠️ Keine freie Fokuszeit vor der Frist gefunden — bitte manuell einplanen oder Frist pruefen.')

        if existing:
            existing.write(vals)
            event = existing
        else:
            event = env['calendar.event'].create(vals)

        if slot_start and slot_end:
            activity = env['mail.activity'].search([
                ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
                ('res_id', '=', record.id),
                ('user_id', '=', user.id),
                ('activity_type_id', '=', 3),
                ('active', '=', True),
            ], limit=1)
            activity_vals = {
                'res_model_id': PROJECT_TASK_MODEL_ID,
                'res_id': record.id,
                'activity_type_id': 3,
                'summary': 'Rückmeldung: ' + record.name,
                'date_deadline': slot_end.date(),
                'user_id': user.id,
                'calendar_event_id': event.id,
            }
            if activity:
                activity.write(activity_vals)
            else:
                env['mail.activity'].create(activity_vals)
elif not record.date_deadline:
    events = env['calendar.event'].search([
        ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
        ('res_id', '=', record.id),
    ])
    env['mail.activity'].search([
        ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
        ('res_id', '=', record.id),
        ('calendar_event_id', 'in', events.ids),
    ]).unlink()
    events.unlink()

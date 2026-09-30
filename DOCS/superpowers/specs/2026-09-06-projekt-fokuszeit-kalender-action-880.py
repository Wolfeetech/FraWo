WORK_START, WORK_END = 8, 18
PROJECT_TASK_MODEL_ID = 522
FOKUSZEIT_CATEG_ID = 8
RUECKMELDUNG_ACTIVITY_TYPE_ID = 15
BUFFER = datetime.timedelta(minutes=60)


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
                    ('start', '<', candidate + duration + BUFFER),
                    ('stop', '>', candidate - BUFFER),
                ]
                if exclude_event_id:
                    domain.append(('id', '!=', exclude_event_id))
                clash = Event.search_count(domain)
                if not clash:
                    return candidate, candidate + duration
                candidate += datetime.timedelta(minutes=30)
        day += datetime.timedelta(days=1)
    return None, None


# --- Meldungstext (Fassung 30.09.2026, Claude) ------------------------------
# Wolf 30.09.: "Ich kann mit solchen Nachrichten im Chatter nichts anfangen".
# Der Text landet 1:1 als Notiz der Meeting-Aktivitaet im Chatter
# ("Heute: <Titel> fuer Wolf Prinz"). Frueher: Projekt + Frist mit 00:00 +
# die ersten 500 Zeichen der Beschreibung + relativer Link. Jetzt vier Zeilen:
# Worum geht's / Was jetzt zu tun ist - liegt bei / Stand / voller Link.
# "Was jetzt zu tun ist" kommt aus der ersten Zeile der Beschreibung
# (Blocker-Format "Wartet auf: ... · Liegt bei: ... · Wieder pruefen: TT.MM."
# oder "Naechster Schritt: ... · Liegt bei: ...") oder der naechsten offenen
# Aktivitaet. Fehlt beides, steht das ehrlich da. "Worum geht's" kommt aus
# einer Zeile "Ziel: ..." der Beschreibung, sonst aus Projekt + Oberaufgabe.
# safe_eval: kein hasattr, keine Imports; 'timezone' (pytz) ist im Kontext.

BLOCK_ENDE = ('/p', 'br', '/li', '/h1', '/h2', '/h3', '/h4', '/div', '/tr', '/ol', '/ul')
LEUTE = {6: 'Wolf', 10: 'Franz', 7: '🤖 Agent'}


def html_lines(value):
    if not value:
        return []
    text = []
    tag = []
    in_tag = False
    for ch in str(value):
        if ch == '<':
            in_tag = True
            tag = []
        elif ch == '>':
            in_tag = False
            name = ''.join(tag).strip().lower().split(' ')[0].rstrip('/')
            if name in BLOCK_ENDE:
                text.append('\n')
        elif in_tag:
            tag.append(ch)
        else:
            text.append(ch)
    result = ''.join(text)
    for entity, char in (('&nbsp;', ' '), ('&quot;', '"'), ('&#39;', "'"), ('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&')):
        result = result.replace(entity, char)
    return [z.strip() for z in result.split('\n') if z.strip()]


def esc(value):
    return str(value or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def kurz(value, n):
    value = (value or '').strip()
    return value if len(value) <= n else value[:n - 1].rstrip() + '…'


def teil(zeile, schluessel):
    if schluessel not in zeile:
        return ''
    rest = zeile.split(schluessel, 1)[1]
    return rest.split(' · ', 1)[0].strip()


def ist_status_zeile(zeile):
    return 'Wartet auf:' in zeile or 'Nächster Schritt:' in zeile


def datum_text(value):
    # Odoo speichert UTC. 00:00 (UTC oder Ortszeit) heisst "nur Datum".
    if not value:
        return ''
    lokal = timezone('UTC').localize(value).astimezone(timezone('Europe/Berlin'))
    if value.hour == 0 and value.minute == 0:
        return value.strftime('%d.%m.%Y')
    if lokal.hour == 0 and lokal.minute == 0:
        return lokal.strftime('%d.%m.%Y')
    return lokal.strftime('%d.%m.%Y, %H:%M Uhr')


def build_title(record):
    name = record.name.split(' — ')[0].strip()
    if record.partner_id:
        name = '%s · %s' % (record.partner_id.name, name)
    return kurz(name, 70)


def build_description(record):
    zeilen = html_lines(record.description)
    status = zeilen[0] if zeilen and ist_status_zeile(zeilen[0]) else ''
    # "Worum geht's" nur aus einer Zeile "Ziel: ..." - der Beschreibungsanfang
    # ist oft Historie ("Blockiert am ...", "Statuskorrektur ..."). Sonst die
    # Einordnung, die Odoo sicher kennt: Projekt und Oberaufgabe.
    worum = ''
    for z in zeilen:
        if 'Ziel:' in z[:12]:
            worum = z.split('Ziel:', 1)[1].strip()
            break
    if not worum:
        worum = record.project_id.name or ''
        if record.parent_id:
            worum += ' · Teil von „%s“' % kurz(record.parent_id.name, 60)
    worum = kurz(worum, 160)

    wartet = teil(status, 'Wartet auf:')
    schritt = teil(status, 'Nächster Schritt:')
    wer = teil(status, 'Liegt bei:')
    pruefen = teil(status, 'Wieder prüfen:')
    if not wartet and not schritt:
        naechste = env['mail.activity'].search([
            ('res_model', '=', 'project.task'), ('res_id', '=', record.id),
            ('calendar_event_id', '=', False)], order='date_deadline asc', limit=1)
        if naechste:
            schritt = '%s (bis %s)' % (naechste.summary or naechste.activity_type_id.name,
                                       naechste.date_deadline.strftime('%d.%m.'))
            wer = LEUTE.get(naechste.user_id.id, naechste.user_id.name)

    if wartet:
        tun = 'Warten auf: %s' % esc(wartet)
    elif schritt:
        tun = esc(schritt)
    else:
        tun = '⚠️ Nächster Schritt fehlt in der Aufgabe.'
    if (wartet or schritt) and wer:
        tun += ' — <b>liegt bei: %s</b>' % esc(wer)

    stand = [esc(record.stage_id.name or 'ohne Stufe')]
    if pruefen:
        stand.append('wieder prüfen %s' % esc(pruefen))
    if record.date_deadline:
        stand.append('Frist %s' % datum_text(record.date_deadline))

    basis = env['ir.config_parameter'].sudo().get_param('web.base.url') or 'https://frawo.tech'
    link = '%s/odoo/project.task/%d' % (basis.rstrip('/'), record.id)

    teile = []
    if worum:
        teile.append("<p><b>Worum geht's:</b> %s</p>" % esc(worum))
    teile.append('<p><b>Was jetzt zu tun ist:</b> %s</p>' % tun)
    teile.append('<p><b>Stand:</b> %s</p>' % ' · '.join(stand))
    teile.append('<p>→ <a href="%s">%s</a></p>' % (link, link))
    return ''.join(teile)


def sync_now(env, user):
    try:
        env['res.users'].sudo().browse(user.id)._sync_all_google_calendar()
    except Exception:
        pass


if record.date_deadline and record.user_ids:
    title = build_title(record)
    description = build_description(record)
    reminder_id = env.ref('calendar.alarm_notif_1', raise_if_not_found=False)
    for user in record.user_ids:
        existing = env['calendar.event'].search([
            ('res_model_id', '=', PROJECT_TASK_MODEL_ID),
            ('res_id', '=', record.id),
            ('user_id', '=', user.id),
        ], limit=1)

        slot_start, slot_end = find_free_slot(env, user, record.allocated_hours, record.date_deadline, existing.id if existing else None)

        if slot_start and slot_end:
            vals = {
                'name': title,
                'description': description,
                'start': slot_start,
                'stop': slot_end,
                'duration': (slot_end - slot_start).total_seconds() / 3600.0,
                'allday': False,
                'user_id': user.id,
                'res_model_id': PROJECT_TASK_MODEL_ID,
                'res_id': record.id,
                'categ_ids': [(6, 0, [FOKUSZEIT_CATEG_ID])],
            }
            if reminder_id:
                vals['alarm_ids'] = [(6, 0, [reminder_id.id])]
        else:
            vals = {
                'name': '⏰ Frist: ' + title,
                'description': description,
                'start': record.date_deadline,
                'stop': record.date_deadline,
                'duration': 0,
                'allday': True,
                'user_id': user.id,
                'res_model_id': PROJECT_TASK_MODEL_ID,
                'res_id': record.id,
                'categ_ids': [(6, 0, [FOKUSZEIT_CATEG_ID])],
            }
            if reminder_id:
                vals['alarm_ids'] = [(6, 0, [reminder_id.id])]
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
                ('activity_type_id', '=', RUECKMELDUNG_ACTIVITY_TYPE_ID),
                ('active', '=', True),
            ], limit=1)
            activity_vals = {
                'res_model_id': PROJECT_TASK_MODEL_ID,
                'res_id': record.id,
                'activity_type_id': RUECKMELDUNG_ACTIVITY_TYPE_ID,
                'summary': 'Rückmeldung: ' + record.name,
                'date_deadline': slot_end.date(),
                'user_id': user.id,
                'calendar_event_id': event.id,
            }
            if activity:
                activity.write(activity_vals)
            else:
                env['mail.activity'].create(activity_vals)

        sync_now(env, user)
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

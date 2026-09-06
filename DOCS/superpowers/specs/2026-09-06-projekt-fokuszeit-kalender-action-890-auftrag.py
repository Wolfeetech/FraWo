"""Auftrag: Liefertermin -> Kalendertermin (ir.actions.server id 890,
base.automation id 18). Spiegelt die Aufgaben-Fokuszeit-Automatik
(Action 880) fuer sale.order. Kein partner_ids-Eintrag (siehe Nachtrag:
das machte den Termin faelschlich als "Meeting" sichtbar). Eigene
Kategorie "Verleih" (id 10) + Emoji-Praefix im Titel, da Farbe/Kategorie
selbst nicht zu Google synct, ein Emoji im Titel aber schon.
"""

ORDER_MODEL_ID = 545
VERLEIH_CATEG_ID = 10


def strip_html(value):
    if not value:
        return ''
    text = []
    in_tag = False
    for ch in value:
        if ch == '<':
            in_tag = True
        elif ch == '>':
            in_tag = False
        elif not in_tag:
            text.append(ch)
    result = ''.join(text)
    for entity, char in (('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&quot;', '"'), ("&#39;", "'"), ('&nbsp;', ' ')):
        result = result.replace(entity, char)
    return result.strip()


def build_description(order):
    parts = []
    if order.partner_id:
        parts.append('Kunde: %s' % order.partner_id.name)
    lines = order.order_line.filtered(lambda l: not l.display_type)
    if lines:
        parts.append('Positionen:\n' + '\n'.join('- %s' % strip_html(l.name).split(chr(10))[0] for l in lines[:10]))
    parts.append('Auftrag in Odoo: /odoo/sale.order/%d' % order.id)
    return '\n\n'.join(parts)


def sync_now(env, user):
    try:
        env['res.users'].sudo().browse(user.id)._sync_all_google_calendar()
    except Exception:
        pass


existing = env['calendar.event'].search([
    ('res_model_id', '=', ORDER_MODEL_ID),
    ('res_id', '=', record.id),
], limit=1)

if record.state == 'sale' and record.commitment_date:
    user = record.user_id
    reminder_id = env.ref('calendar.alarm_notif_1', raise_if_not_found=False)
    vals = {
        'name': '📦 ' + (record.partner_id.name if record.partner_id else record.name),
        'description': build_description(record),
        'start': record.commitment_date,
        'stop': record.commitment_date + datetime.timedelta(hours=2),
        'duration': 2.0,
        'allday': False,
        'user_id': user.id if user else False,
        'res_model_id': ORDER_MODEL_ID,
        'res_id': record.id,
        'categ_ids': [(6, 0, [VERLEIH_CATEG_ID])],
    }
    if reminder_id:
        vals['alarm_ids'] = [(6, 0, [reminder_id.id])]

    if existing:
        existing.write(vals)
    else:
        env['calendar.event'].create(vals)

    if user:
        sync_now(env, user)
else:
    if existing:
        existing.write({'active': False})

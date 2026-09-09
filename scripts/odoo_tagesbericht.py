# Tagesbericht an Wolf - Regel 7. Fassung 5 vom 09.09.2026.
#
# Wolf: "in der tagesordnung fehlt mir klare anweisung was ich heute wann zu
# tun habe ... du hast heute frei, also stehen zuhause xyz an oder in der
# villa xyz oder du faehrst nach stockenweiler fuer xyz"
#
# Deshalb steht jetzt ein TAGESPLAN ganz oben: Dienstplan aus dem Kalender,
# danach je Ort das, was dort machbar ist. Nur Stufen 'Als Naechstes' und
# 'In Arbeit' - Backlog und Ideen sind kein Tagesplan.
#
# STOLPERSTEINE (haben Laeufe gekostet):
#   date_deadline ist DATETIME -> .date() vor Vergleichen.
#   safe_eval kennt KEIN hasattr(). isinstance gibt es.
#   compile() findet beides nicht.
#
# FASSUNG 5 (09.09.2026):
#   Ergänzt: TAG_BEANTWORTET (160) - Aufgaben, die Wolf/Kunde beantwortet hat
#   und die auf Abarbeitung durch den Agenten warten (#1415 Punkt 4).

HEUTE = datetime.date.today()
ERLEDIGT = [6, 35]
MACHBAR = [2, 3]           # Als Naechstes, In Arbeit
IN_ARBEIT = 3
WIP_GRENZE = 6
STILL_TAGE = 14
VORSCHAU = 7
TAG_WOLF = 153
TAG_BEANTWORTET = 160
MAX = 8
WOLF_UID = 6
FRANZ_UID = 10
FREMDE_PROJEKTE = [106, 107]
ORTE = [(154, 'Zuhause / RK22a'), (155, 'In der Villa'),
        (156, 'In Stockenweiler'), (158, 'Unterwegs erledigen'),
        (157, 'Am Rechner')]
EMPFAENGER = 'wolf@frawo.tech'
WOCHENTAG = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag',
             'Freitag', 'Samstag', 'Sonntag'][HEUTE.weekday()]

Task = env['project.task']
JETZT = datetime.datetime.now()
OFFEN = [('stage_id', 'not in', ERLEDIGT)]
EIGEN = OFFEN + [('project_id', 'not in', FREMDE_PROJEKTE)]

# --- Dienstplan aus dem Kalender ------------------------------------------
von = datetime.datetime.combine(HEUTE, datetime.time(0, 0))
bis = von + datetime.timedelta(days=1)
termine = env['calendar.event'].search([('start', '>=', von), ('start', '<', bis)],
                                       order='start asc')


def termine_von(uid):
    zs = []
    for e in termine:
        if e.user_id and e.user_id.id == uid:
            a = (e.start + datetime.timedelta(hours=2)).strftime('%H:%M')
            b = (e.stop + datetime.timedelta(hours=2)).strftime('%H:%M')
            zs.append('%s (%s&ndash;%s)' % (e.name[:44], a, b))
    return zs


wolf_heute = termine_von(WOLF_UID)
franz_heute = termine_von(FRANZ_UID)

teile = ['<h2>%s, %s</h2>' % (WOCHENTAG, HEUTE.strftime('%d.%m.%Y'))]

if wolf_heute:
    teile.append('<p><b>Du heute:</b> %s</p>' % ' &middot; '.join(wolf_heute))
else:
    teile.append('<p><b>Du hast heute frei.</b></p>')
if franz_heute:
    teile.append('<p><i>Franz: %s</i></p>' % ' &middot; '.join(franz_heute))

# --- Tagesplan nach Ort ---------------------------------------------------
plan = ''
for tag_id, ort in ORTE:
    a = Task.search(EIGEN + [('tag_ids', 'in', [tag_id]),
                             ('stage_id', 'in', MACHBAR)],
                    order='priority desc, date_deadline asc')
    if not a:
        continue
    zeilen = ''
    for t in a[:3]:
        ueber = ''
        if t.date_deadline and t.date_deadline.date() < HEUTE:
            ueber = ' <b>(&uuml;berf&auml;llig)</b>'
        elif t.date_deadline:
            ueber = ' <i>(bis %s)</i>' % t.date_deadline.strftime('%d.%m.')
        zeilen += '<li>%s%s</li>' % (t.name[:72], ueber)
    mehr = (' <i>&hellip; und %d weitere</i>' % (len(a) - 3)) if len(a) > 3 else ''
    plan += '<p><b>%s</b> &mdash; %d%s</p><ul>%s</ul>' % (ort, len(a), mehr, zeilen)

if plan:
    teile.append('<h3>Was heute wo geht</h3>' + plan)
else:
    teile.append('<p><i>Keine Aufgabe hat einen Ort. Schlagwoerter: @rk22, @villa, '
                 '@stockenweiler, @unterwegs, @remote.</i></p>')

ohne_ort = Task.search_count(EIGEN + [('stage_id', 'in', MACHBAR),
                                      ('tag_ids', 'not in', [o[0] for o in ORTE])])
if ohne_ort:
    teile.append('<p style="color:#777"><i>%d machbare Aufgaben haben keinen Ort '
                 '&mdash; deshalb stehen sie oben nicht drin.</i></p>' % ohne_ort)

teile.append('<hr>')

# --- Lage ------------------------------------------------------------------
ueberfaellig = Task.search(EIGEN + [('date_deadline', '<', HEUTE)],
                           order='date_deadline asc')
laufend = Task.search([('stage_id', '=', IN_ARBEIT),
                       ('project_id', 'not in', FREMDE_PROJEKTE)])
liegen = laufend.filtered(lambda t: t.write_date and (JETZT - t.write_date).days >= STILL_TAGE)
braucht_wolf = Task.search(OFFEN + [('tag_ids', 'in', [TAG_WOLF])])
beantwortet = Task.search(OFFEN + [('tag_ids', 'in', [TAG_BEANTWORTET])])
meilensteine = env['project.milestone'].search(
    [('is_reached', '=', False), ('deadline', '<', HEUTE)],
    order='deadline asc').filtered(lambda m: not m.name.startswith('[FREMD]'))
entwuerfe = env['account.move'].search([('state', '=', 'draft'),
    ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'])])


def block(titel, records):
    if not records:
        return ''
    zs = ''
    for t in records[:MAX]:
        d = t.date_deadline.strftime('%d.%m.') if t.date_deadline else '&ndash;'
        zs += ('<tr><td><tt>%s</tt>&nbsp;&nbsp;</td><td>%s</td></tr>'
               % (d, t.name[:80]))
    rest = ('<p><i>&hellip; und %d weitere</i></p>' % (len(records) - MAX)) if len(records) > MAX else ''
    return '<p><b>%s (%d)</b></p><table>%s</table>%s' % (titel, len(records), zs, rest)


warn = []
if ueberfaellig:
    warn.append('%d ueberfaellig' % len(ueberfaellig))
if meilensteine:
    warn.append('%d Meilenstein(e)' % len(meilensteine))
if len(laufend) > WIP_GRENZE:
    warn.append('%d in Arbeit (max %d)' % (len(laufend), WIP_GRENZE))
if liegen:
    warn.append('%d seit %d Tagen unbewegt' % (len(liegen), STILL_TAGE))
if beantwortet:
    warn.append('%d Antwort(en) warten auf Agent' % len(beantwortet))

if warn:
    teile.append('<p><b>Achtung:</b> %s</p>' % ' &middot; '.join(warn))
else:
    teile.append('<p><b>Nichts Ueberfaelliges.</b> <i>Diese Zeile ist der Zweck des '
                 'Berichts &mdash; bliebe die Mail aus, waere das selbst die Meldung.</i></p>')

teile.append(block('Ueberfaellig', ueberfaellig))
teile.append(block('Wartet auf deine Entscheidung', braucht_wolf))
teile.append(block('Beantwortet (wartet auf Agenten-Verarbeitung)', beantwortet))
teile.append(block('Seit %d Tagen unbewegt' % STILL_TAGE, liegen))

if meilensteine:
    zs = ''.join('<tr><td><tt>%s</tt>&nbsp;&nbsp;</td><td>%s</td></tr>'
                 % (m.deadline.strftime('%d.%m.'), m.name[:78]) for m in meilensteine)
    teile.append('<p><b>Meilensteine ueberfaellig (%d)</b></p><table>%s</table>'
                 % (len(meilensteine), zs))

if entwuerfe:
    teile.append('<p><b>%d Rechnungen im Entwurf</b>, zusammen %.2f EUR</p>'
                 % (len(entwuerfe), sum(entwuerfe.mapped('amount_total'))))

teile.append('<p style="color:#888;font-size:11px">Sicherungen meldet die Ueberwachung '
             'getrennt. Odoo-Cron 44, Aktion 828.</p>')

betreff = 'FraWo %s %s' % (WOCHENTAG, HEUTE.strftime('%d.%m.'))
if wolf_heute:
    betreff += ' - Arbeit'
else:
    betreff += ' - frei'
if warn:
    betreff += ' (%s)' % warn[0]

env['mail.mail'].sudo().create({
    'subject': betreff, 'body_html': ''.join(teile),
    'email_to': EMPFAENGER, 'auto_delete': False,
}).send()

env['project.task'].browse(600).message_post(
    body='Tagesbericht %s verschickt.' % HEUTE.strftime('%d.%m.%Y'),
    message_type='comment', subtype_xmlid='mail.mt_note')

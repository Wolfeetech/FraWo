# -*- coding: utf-8 -*-
# Code der Odoo-Server-Aktion 828 ("Tagesbericht an Wolf"),
# ausgeloest von Cron 44, taeglich.
#
# NEUFASSUNG 09.09.2026 — Regel 7 der Sicherheitsstandards.
#
# WAS VORHER FALSCH WAR
# Die alte Fassung ("Live-Stand Tages-Snapshot") zaehlte offene Aufgaben je
# Projekt und schrieb das Ergebnis in den Chatter von Aufgabe 600. Zwei
# Probleme:
#   1. Der Bericht kam nie bei Wolf an. Er lag in einer Aufgabe, die niemand
#      oeffnet — also genau das "man muesste mal nachsehen", das bei einer
#      sprunghaften Arbeitsweise keine Sicherung ist.
#   2. Sie filterte auf stage_id != 6 und uebersah Stufe 35 (Abgebrochen).
#      Abgebrochene Aufgaben zaehlten als offen.
#
# WAS SIE JETZT TUT
# Beantwortet taeglich die Fragen aus Regel 7, soweit Odoo sie beantworten
# kann, und schickt das Ergebnis per E-Mail an Wolf — ueber denselben
# Brevo-Relay, den die Ueberwachung schon benutzt. Kein neuer Kanal, kein
# neuer Bot, kein neuer Systemdienst, kein neuer Cron: die Aufgabe lief
# bereits taeglich, nur ins Leere.
#
# WICHTIG: Der Bericht geht AUCH RAUS, WENN NICHTS BRENNT. Stille darf nie
# "alles gut" bedeuten — sie ist auch das Bild eines toten Systems.
#
# Sicherungen und Anlagenzustand deckt die Ueberwachung ab (Prometheus →
# Alertmanager → dieselbe Adresse). Aus einer Server-Aktion heraus sind keine
# HTTP-Abfragen moeglich, deshalb steht das hier bewusst nicht drin.
#
# Der HTML-Teil ist absichtlich schlicht: wenig Auszeichnung kommt in jedem
# Mailprogramm richtig an.

HEUTE = datetime.date.today()
ERLEDIGT = [6, 35]
IN_ARBEIT = 3
WIP_GRENZE = 8
STILL_TAGE = 14
VORSCHAU = 7
TAG_WOLF = 153
EMPFAENGER = 'wolf@frawo.tech'

Task = env['project.task']
JETZT = datetime.datetime.now()

ueberfaellig = Task.search([('date_deadline', '<', HEUTE),
                            ('stage_id', 'not in', ERLEDIGT)],
                           order='date_deadline asc')
demnaechst = Task.search([('date_deadline', '>=', HEUTE),
                          ('date_deadline', '<=', HEUTE + datetime.timedelta(days=VORSCHAU)),
                          ('stage_id', 'not in', ERLEDIGT)],
                         order='date_deadline asc')
meilensteine = env['project.milestone'].search([('is_reached', '=', False),
                                                ('deadline', '<', HEUTE)],
                                               order='deadline asc')
laufend = Task.search([('stage_id', '=', IN_ARBEIT)])
liegen = laufend.filtered(lambda t: t.write_date and (JETZT - t.write_date).days >= STILL_TAGE)
braucht_wolf = Task.search([('tag_ids', 'in', [TAG_WOLF]),
                            ('stage_id', 'not in', ERLEDIGT)])
entwuerfe = env['account.move'].search([('state', '=', 'draft'),
                                        ('move_type', 'in', ['out_invoice', 'out_refund',
                                                             'in_invoice', 'in_refund'])],
                                       order='invoice_date asc')
offen_gesamt = Task.search_count([('stage_id', 'not in', ERLEDIGT)])


def zeile(datum, text, rechts):
    return '<tr><td><tt>%s</tt>&nbsp;&nbsp;</td><td>%s&nbsp;&nbsp;</td><td><i>%s</i></td></tr>' % (
        datum, text, rechts)


def aufgaben_block(titel, records):
    if not records:
        return '<p><b>%s</b> &mdash; keine.</p>' % titel
    zs = ''.join(zeile(t.date_deadline.strftime('%d.%m.') if t.date_deadline else '&ndash;',
                       t.name[:80],
                       (t.project_id.name or '')[:34]) for t in records[:15])
    rest = '<p><i>&hellip; und %d weitere</i></p>' % (len(records) - 15) if len(records) > 15 else ''
    return '<p><b>%s (%d)</b></p><table>%s</table>%s' % (titel, len(records), zs, rest)


brennt = []
if ueberfaellig:
    brennt.append('%d ueberfaellige Frist(en)' % len(ueberfaellig))
if meilensteine:
    brennt.append('%d ueberfaellige(r) Meilenstein(e)' % len(meilensteine))
if braucht_wolf:
    brennt.append('%d Entscheidung(en) fuer dich' % len(braucht_wolf))
if len(laufend) > WIP_GRENZE:
    brennt.append('%d Aufgaben gleichzeitig in Arbeit (Richtwert %d)' % (len(laufend), WIP_GRENZE))
if liegen:
    brennt.append('%d davon seit ueber %d Tagen unbewegt' % (len(liegen), STILL_TAGE))
if entwuerfe:
    brennt.append('%d Rechnung(en) im Entwurf' % len(entwuerfe))

if brennt:
    kopf = '<p><b>Heute wichtig:</b> %s</p>' % ' &middot; '.join(brennt)
else:
    kopf = ('<p><b>Nichts Ueberfaelliges, nichts Liegengebliebenes, keine offene '
            'Entscheidung.</b><br><i>Diese Zeile ist der eigentliche Zweck des Berichts: '
            'sie beweist, dass das System noch lebt. Bliebe die Mail aus, waere das '
            'selbst die Meldung.</i></p>')

teile = ['<h2>Tagesbericht %s</h2>' % HEUTE.strftime('%d.%m.%Y'),
         '<p><i>FraWo GbR &middot; Regel 7 der Sicherheitsstandards &middot; %d offene '
         'Aufgaben insgesamt, %d davon in Arbeit</i></p><hr>' % (offen_gesamt, len(laufend)),
         kopf,
         aufgaben_block('Ueberfaellige Fristen', ueberfaellig),
         aufgaben_block('Faellig in den naechsten %d Tagen' % VORSCHAU, demnaechst),
         aufgaben_block('Wartet auf deine Entscheidung', braucht_wolf),
         aufgaben_block('Steht auf in Arbeit, bewegt sich aber seit %d Tagen nicht' % STILL_TAGE,
                        liegen)]

if meilensteine:
    zs = ''.join(zeile(m.deadline.strftime('%d.%m.'), m.name[:80],
                       (m.project_id.name or '')[:34]) for m in meilensteine)
    teile.append('<p><b>Ueberfaellige Meilensteine (%d)</b></p><table>%s</table>'
                 % (len(meilensteine), zs))

if entwuerfe:
    zs = ''.join(zeile(r.invoice_date.strftime('%d.%m.%Y') if r.invoice_date else '&ndash;',
                       (r.partner_id.name or r.name or '')[:56],
                       '%.2f EUR' % r.amount_total) for r in entwuerfe[:15])
    teile.append('<p><b>Rechnungen im Entwurf (%d)</b> &mdash; <i>gebucht wird bewusst, '
                 'aber ein Entwurf zaehlt fuer nichts.</i></p><table>%s</table>'
                 % (len(entwuerfe), zs))

teile.append('<hr><p><i>Sicherungen und Anlagenzustand meldet die Ueberwachung getrennt an '
             'dieselbe Adresse. Erzeugt von Odoo-Cron 44, Server-Aktion 828. Quelle: '
             'scripts/odoo_tagesbericht.py. Abschalten: Cron 44 deaktivieren.</i></p>')

betreff = 'FraWo Tagesbericht %s' % HEUTE.strftime('%d.%m.%Y')
if brennt:
    betreff = '%s (%s)' % (betreff, brennt[0])

env['mail.mail'].sudo().create({
    'subject': betreff,
    'body_html': ''.join(teile),
    'email_to': EMPFAENGER,
    'auto_delete': True,
}).send()

env['project.task'].browse(600).message_post(
    body='Tagesbericht %s verschickt: %s' % (
        HEUTE.strftime('%d.%m.%Y'),
        ' / '.join(brennt) if brennt else 'nichts Auffaelliges'),
    message_type='comment', subtype_xmlid='mail.mt_note')

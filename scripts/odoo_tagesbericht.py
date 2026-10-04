# Tagesbericht an Wolf - Regel 7. Fassung 7.1 vom 04.10.2026.
# 7.1: Review Jarvis #22850 - Teil 1 erst zusammenfuehren/entdoppeln, dann
#   insgesamt auf MAX begrenzen; Termine und Franz ebenfalls auf MAX.
#
# Wolf (04.10.2026): "den taeglichen bericht wuensche ich mir besser...
# aktuell zuviel blabla". Vereinbart: nur noch drei Teile:
#   1. Was heute bei dir liegt   2. Termine heute   3. Was kaputt ist
# Alles, was nur die Agenten betrifft (Ueberfaelliges ohne Wolf, WIP-Grenze,
# unbewegte Aufgaben, Blockiert ohne Grund, beantwortete Fragen, Meilensteine,
# Aufgaben ohne Ort), steht nicht mehr in Wolfs Mail, sondern als interne
# Notiz an #600 - die Agenten lesen es dort.
#
# Teil 3 "Was kaputt ist": Alarme der Ueberwachung kommen noch nicht in Odoo
# an (Server-Aktionen koennen kein HTTP). Bis Jarvis sie liefert, steht dort
# nur, was Odoo selbst sieht: Aufgaben mit dem Schlagwort TAG_STOERUNG.
#
# STOLPERSTEINE (haben Laeufe gekostet):
#   date_deadline ist DATETIME -> .date() vor Vergleichen.
#   safe_eval kennt KEIN hasattr(). isinstance gibt es.
#   compile() findet beides nicht.
#   Keine Closures (Odoo verbietet LOAD_CLOSURE/MAKE_CELL in Server-Aktionen).
#   Kalenderzeiten sind UTC - Sommer-/Winterzeit selbst rechnen (bis Fassung 6
#   stand hier fest +2 h, ab 25.10. waere das eine Stunde falsch gewesen).

HEUTE = datetime.date.today()
ERLEDIGT = [6, 35]
IN_ARBEIT = 3
BLOCKIERT = 5
WIP_GRENZE = 6
STILL_TAGE = 14
TAG_WOLF = 153
TAG_BEANTWORTET = 160
TAG_STOERUNG = 0           # 0 = noch kein Schlagwort festgelegt
MAX = 5
WOLF_UID = 6
FRANZ_UID = 10
FREMDE_PROJEKTE = [106, 107]
ORTE = [154, 155, 156, 157, 158]
EMPFAENGER = 'wolf@frawo.tech'
WOCHENTAG = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag',
             'Freitag', 'Samstag', 'Sonntag'][HEUTE.weekday()]

Task = env['project.task']
JETZT = datetime.datetime.now()
OFFEN = [('stage_id', 'not in', ERLEDIGT)]
EIGEN = OFFEN + [('project_id', 'not in', FREMDE_PROJEKTE)]


def letzter_sonntag(jahr, monat):
    d = datetime.date(jahr, monat, 31)
    return d - datetime.timedelta(days=(d.weekday() + 1) % 7)


# Mitteleuropaeische Sommerzeit: letzter Sonntag Maerz bis letzter Sonntag Oktober.
if letzter_sonntag(HEUTE.year, 3) <= HEUTE < letzter_sonntag(HEUTE.year, 10):
    VERSATZ = datetime.timedelta(hours=2)
else:
    VERSATZ = datetime.timedelta(hours=1)


def zeile(text, rest=''):
    return '<li>%s%s</li>' % (text, rest)


def liste(zeilen):
    # Hoechstens MAX Zeilen je Liste, Rest als eine Zaehlzeile (Review Jarvis #22850).
    mehr = ('<li><i>&hellip; und %d weitere</i></li>' % (len(zeilen) - MAX)
            if len(zeilen) > MAX else '')
    return '<ul>%s%s</ul>' % (''.join(zeilen[:MAX]), mehr)


# --- Teil 1: Was heute bei dir liegt ----------------------------------------
braucht_wolf = Task.search(OFFEN + [('tag_ids', 'in', [TAG_WOLF])],
                           order='priority desc, date_deadline asc')
wolf_ueberfaellig = Task.search(EIGEN + [('date_deadline', '<', HEUTE),
                                         ('user_ids', 'in', [WOLF_UID])],
                                order='date_deadline asc')
wolf_ueberfaellig = wolf_ueberfaellig - braucht_wolf

blockiert = Task.search([('stage_id', '=', BLOCKIERT),
                         ('project_id', 'not in', FREMDE_PROJEKTE)])


def blocker_teil(t, schluessel, ende):
    s = str(t.description or '')
    if schluessel not in s:
        return ''
    return s.split(schluessel, 1)[1].split(ende, 1)[0]


def pruef_datum(t):
    teil = blocker_teil(t, 'Wieder prüfen:</b> ', '</p>')[:6]
    if len(teil) < 5 or not (teil[0:2].isdigit() and teil[3:5].isdigit()):
        return None
    tag, mon = int(teil[0:2]), int(teil[3:5])
    if not (1 <= mon <= 12 and 1 <= tag <= 31):
        return None
    d = datetime.date(HEUTE.year, mon, min(tag, 28 if mon == 2 else 30 if mon in (4, 6, 9, 11) else 31))
    if (HEUTE - d).days > 180:
        d = datetime.date(HEUTE.year + 1, d.month, d.day)
    return d


blockiert_bei_wolf = blockiert.filtered(
    lambda t: 'Liegt bei:</b> Wolf' in str(t.description or '')
    and pruef_datum(t) is not None and pruef_datum(t) <= HEUTE) - braucht_wolf
wolf_ueberfaellig = wolf_ueberfaellig - blockiert_bei_wolf

entwuerfe = env['account.move'].search([('state', '=', 'draft'),
    ('move_type', 'in', ['out_invoice', 'out_refund', 'in_invoice', 'in_refund'])])

# Erst alle Kandidaten zusammenfuehren (oben entdoppelt), dann einmal insgesamt begrenzen.
z1 = []
for t in braucht_wolf:
    z1.append(zeile(t.name[:80], ' <i>(bis %s)</i>' % t.date_deadline.strftime('%d.%m.')
                    if t.date_deadline else ''))
for t in blockiert_bei_wolf:
    grund = blocker_teil(t, 'Wartet auf:</b> ', ' · <b>Liegt bei')[:100]
    z1.append(zeile(t.name[:60], ' &mdash; <i>wartet auf %s</i>' % grund if grund else ''))
for t in wolf_ueberfaellig:
    z1.append(zeile(t.name[:70], ' <b>(&uuml;berf&auml;llig seit %s)</b>'
                    % t.date_deadline.strftime('%d.%m.')))
anzahl_wolf = len(z1)
if entwuerfe:
    z1.append(zeile('%d Rechnung(en) im Entwurf, zusammen %.2f EUR'
                    % (len(entwuerfe), sum(entwuerfe.mapped('amount_total')))))

teile = ['<h2>%s, %s</h2>' % (WOCHENTAG, HEUTE.strftime('%d.%m.%Y'))]
teile.append('<h3>1. Bei dir heute</h3>')
if z1:
    teile.append(liste(z1))
else:
    teile.append('<p>Nichts. Heute liegt keine Aufgabe bei dir.</p>')

# --- Teil 2: Termine heute --------------------------------------------------
von = datetime.datetime.combine(HEUTE, datetime.time(0, 0)) - VERSATZ
bis = von + datetime.timedelta(days=1)
termine = env['calendar.event'].search([('start', '<', bis), ('stop', '>', von)],
                                       order='start asc')


def termine_von(uid):
    zs = []
    for e in termine:
        if e.user_id and e.user_id.id == uid:
            if e.allday:
                zs.append('%s (ganztags)' % e.name[:60])
            else:
                zs.append('%s&ndash;%s %s' % ((e.start + VERSATZ).strftime('%H:%M'),
                                             (e.stop + VERSATZ).strftime('%H:%M'),
                                             e.name[:60]))
    return zs


wolf_heute = termine_von(WOLF_UID)
franz_heute = termine_von(FRANZ_UID)
teile.append('<h3>2. Termine heute</h3>')
if wolf_heute:
    teile.append(liste([zeile(z) for z in wolf_heute]))
else:
    teile.append('<p>Keine Termine &ndash; du hast frei.</p>')
if franz_heute:
    teile.append('<p><i>Franz: %s%s</i></p>' % (
        ' &middot; '.join(franz_heute[:MAX]),
        ' &middot; &hellip; und %d weitere' % (len(franz_heute) - MAX) if len(franz_heute) > MAX else ''))

# --- Teil 3: Was kaputt ist -------------------------------------------------
teile.append('<h3>3. Kaputt</h3>')
stoerungen = Task.search(OFFEN + [('tag_ids', 'in', [TAG_STOERUNG])]) if TAG_STOERUNG else Task
if stoerungen:
    teile.append(liste([zeile(t.name[:80]) for t in stoerungen]))
else:
    teile.append('<p>Nichts bekannt. <i>Alarme der &Uuml;berwachung kommen weiter '
                 'direkt per Telegram.</i></p>')

betreff = 'FraWo %s %s' % (WOCHENTAG, HEUTE.strftime('%d.%m.'))
if anzahl_wolf:
    betreff += ' - %d bei dir' % anzahl_wolf
else:
    betreff += ' - nichts bei dir'
if stoerungen:
    betreff += ', %d kaputt' % len(stoerungen)

env['mail.mail'].sudo().create({
    'subject': betreff, 'body_html': ''.join(teile),
    'email_to': EMPFAENGER, 'auto_delete': False,
}).send()

# --- Nur fuer die Agenten: interne Notiz an #600, keine Mail ------------------
ueberfaellig = Task.search(EIGEN + [('date_deadline', '<', HEUTE)])
laufend = Task.search([('stage_id', '=', IN_ARBEIT),
                       ('project_id', 'not in', FREMDE_PROJEKTE)])
liegen = laufend.filtered(lambda t: t.write_date and (JETZT - t.write_date).days >= STILL_TAGE)
beantwortet = Task.search(OFFEN + [('tag_ids', 'in', [TAG_BEANTWORTET])])
meilensteine = env['project.milestone'].search(
    [('is_reached', '=', False), ('deadline', '<', HEUTE)]).filtered(
    lambda m: not m.name.startswith('[FREMD]'))
BLOCKER_MARKER = ('Wartet auf:</b>', 'Liegt bei:</b>', 'Wieder prüfen:</b>')


def hat_alle_blocker_marker(beschreibung):
    for marker in BLOCKER_MARKER:
        if marker not in beschreibung:
            return False
    return True


blockiert_ohne_grund = blockiert.filtered(
    lambda t: not hat_alle_blocker_marker(str(t.description or '')))
ohne_ort = Task.search_count(EIGEN + [('stage_id', 'in', [2, 3]),
                                      ('tag_ids', 'not in', ORTE)])

agenten = []
if ueberfaellig:
    agenten.append('%d ueberfaellig (gesamt)' % len(ueberfaellig))
if len(laufend) > WIP_GRENZE:
    agenten.append('%d in Arbeit (max %d)' % (len(laufend), WIP_GRENZE))
if liegen:
    agenten.append('%d seit %d Tagen unbewegt: %s' % (
        len(liegen), STILL_TAGE, ', '.join('#%d' % t.id for t in liegen[:10])))
if blockiert_ohne_grund:
    agenten.append('%d blockiert ohne Grund-Zeile: %s' % (
        len(blockiert_ohne_grund), ', '.join('#%d' % t.id for t in blockiert_ohne_grund[:10])))
if beantwortet:
    agenten.append('%d Antwort(en) warten auf Agent: %s' % (
        len(beantwortet), ', '.join('#%d' % t.id for t in beantwortet[:10])))
if meilensteine:
    agenten.append('%d Meilenstein(e) ueberfaellig' % len(meilensteine))
if ohne_ort:
    agenten.append('%d machbare Aufgaben ohne Ort' % ohne_ort)

notiz = 'Tagesbericht %s verschickt (%d bei Wolf).' % (HEUTE.strftime('%d.%m.%Y'), anzahl_wolf)
if agenten:
    notiz += ' Fuer Agenten: ' + ' · '.join(agenten)
env['project.task'].browse(600).message_post(
    body=notiz, message_type='comment', subtype_xmlid='mail.mt_note')

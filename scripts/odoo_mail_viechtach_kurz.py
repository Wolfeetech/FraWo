# -*- coding: utf-8 -*-
# Viechtach: vollstaendiges Paket in einer Mail, 09.09.2026.
#
# Wolf: "jetzt eben alles per Mail raus an mich".
# Ersetzt die drei Einzelmails des Tages durch eine, die alles enthaelt -
# damit nichts zusammengesucht werden muss und beim Weiterleiten nichts fehlt.
#
# Laeuft in der Odoo-Shell auf CT140.

import base64
import os

from markupsafe import Markup

ORDNER = '/tmp/viechtach'
EMPFAENGER = 'wolf@frawo.tech'

DATEIEN = [
    # Das, was gedruckt wird
    'Viechtach_kompakt_4-auf-1.pdf',
    'Viechtach_kompakt_2-auf-1.pdf',
    # Einzelteile, falls etwas nachgedruckt werden muss
    '00_Anschreiben_Amtsgericht_Viechtach.pdf',
    'Anlage_1_Gehaltsabrechnung_August_2026.pdf',
    'Anlage_2_Kontoauszug_08-2026.pdf',
    'Anlage_2b_Kontoauszug_09-2026.pdf',
    'Anlage_3_Zahlung_100EUR_30-08-2026.pdf',
    # Zum Nachlesen, geht NICHT ans Gericht
    'Schreiben_des_Gerichts_03.09.2026.pdf',
]

anhaenge = []
gesamt = 0
for name in DATEIEN:
    pfad = os.path.join(ORDNER, name)
    if not os.path.exists(pfad):
        raise Exception('Fehlt: %s - nichts verschickt.' % name)
    with open(pfad, 'rb') as f:
        roh = f.read()
    gesamt += len(roh)
    a = env['ir.attachment'].sudo().create({
        'name': name,
        'datas': base64.b64encode(roh),
        'mimetype': 'application/pdf',
        'res_model': 'project.task',
        'res_id': 1360,
    })
    anhaenge.append(a.id)
    print('  angehaengt: %-46s %7.1f KB' % (name, len(roh) / 1024.0))

print('')
print('  %d Anhaenge, %.2f MB' % (len(anhaenge), gesamt / 1048576.0))

koerper = Markup("""
<div style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:1.6;
color:#191B1E;max-width:720px">

<h2 style="margin:0 0 4px">Amtsgericht Viechtach &ndash; vollst&auml;ndiges Paket</h2>
<p style="margin:0 0 18px;color:#666">Aktenzeichen 6 OWi 7409-001490-21/2 &middot;
Wolfgang Ferdinand Prinz &middot; gek&uuml;rzte Fassung, 09.09.2026</p>

<p style="background:#FBEEE6;border-left:4px solid #C0521C;padding:12px 16px;margin:0 0 20px">
<b>Bitte bis sp&auml;testens 17.09.2026 beim Gericht.</b> Ma&szlig;geblich ist der
<b>Eingang</b>, nicht das Absendedatum.</p>

<h3 style="margin:20px 0 6px">Zum Drucken reicht eine Datei</h3>
<p style="margin:0 0 10px"><b>Viechtach_kompakt_4-auf-1.pdf</b> &ndash; darin ist
alles enthalten, in der richtigen Reihenfolge.</p>

<table style="border-collapse:collapse;font-size:13.5px;margin:0 0 16px">
  <tr>
    <th style="text-align:left;padding:5px 18px 5px 0;border-bottom:1px solid #ccc">Datei</th>
    <th style="text-align:right;padding:5px 18px 5px 0;border-bottom:1px solid #ccc">Seiten</th>
    <th style="text-align:right;padding:5px 0;border-bottom:1px solid #ccc">Bl&auml;tter beidseitig</th>
  </tr>
  <tr>
    <td style="padding:5px 18px 5px 0"><b>4-auf-1</b> &ndash; empfohlen</td>
    <td style="text-align:right;padding:5px 18px 5px 0"><b>28</b></td>
    <td style="text-align:right"><b>14</b></td>
  </tr>
  <tr>
    <td style="padding:5px 18px 5px 0">2-auf-1 &ndash; falls die Schrift zu klein ist</td>
    <td style="text-align:right;padding:5px 18px 5px 0">51</td>
    <td style="text-align:right">26</td>
  </tr>
  <tr>
    <td style="padding:5px 18px 5px 0;color:#888">(unverkleinert w&auml;ren es)</td>
    <td style="text-align:right;padding:5px 18px 5px 0;color:#888">55</td>
    <td style="text-align:right;color:#888">51</td>
  </tr>
</table>
<p style="margin:0 0 8px"><b>Beidseitig drucken</b> &ndash; dann liegen acht
Originalseiten auf einem Blatt Papier.</p>

<h3 style="margin:22px 0 6px">Von Hand einzutragen</h3>
<ol style="margin:0 0 14px;padding-left:22px">
  <li><b>Seite 1:</b> rechts oben bei &bdquo;Hergensweiler, den ______&ldquo; das
      Absendedatum eintragen.</li>
  <li><b>Seite 2:</b> auf der Linie &uuml;ber dem Namen unterschreiben.</li>
</ol>

<h3 style="margin:22px 0 6px">Wohin</h3>
<table style="border-collapse:collapse;font-size:13.5px;margin:0 0 14px">
  <tr><td style="padding:4px 16px 4px 0;vertical-align:top"><b>Post</b></td>
      <td>Amtsgericht Viechtach<br>Postfach 1365<br>94230 Viechtach</td></tr>
  <tr><td style="padding:4px 16px 4px 0;vertical-align:top"><b>Fax</b></td>
      <td>+49 9621 96241 4140 &ndash; bei knapper Frist der sichere Weg.
          Sendebericht aufheben.</td></tr>
</table>
<p style="margin:0 0 8px"><b>Nur Kopien senden, keine Originale.</b> Eine Kopie des
unterschriebenen Schreibens f&uuml;r die eigenen Unterlagen behalten. Der
<b>Brief</b> geht ans <b>Amtsgericht</b>, <b>Zahlungen</b> an die <b>Zentrale
Bu&szlig;geldstelle</b> (IBAN DE25 7415 1450 0240 000414, immer mit Aktenzeichen).</p>

<h3 style="margin:22px 0 6px">Was im Anhang liegt</h3>
<ul style="margin:0 0 14px;padding-left:22px">
  <li><b>Viechtach_kompakt_4-auf-1</b> &ndash; das Druckst&uuml;ck (31 Seiten)</li>
  <li><b>Viechtach_kompakt_2-auf-1</b> &ndash; gr&ouml;&szlig;ere Schrift (54 Seiten)</li>
  <li><b>00_Anschreiben</b> &ndash; nur der Brief, jetzt <b>2 Seiten</b></li>
  <li><b>Anlage 1</b> Lohnbescheinigung August 2026</li>
  <li><b>Anlage 2</b> Kontoauszug August &middot; <b>Anlage 2b</b> September bis 09.09.</li>
  <li><b>Anlage 3</b> Zahlung 100,00 EUR vom 30.08.2026</li>
  <li><b>Schreiben des Gerichts vom 03.09.2026</b> &ndash; nur zum Nachlesen,
      das geht <u>nicht</u> mit ans Gericht</li>
</ul>

<p style="margin-top:24px;padding-top:12px;border-top:1px solid #DDD;color:#888;
font-size:11.5px">
Alle Angaben im Schreiben stammen aus den eigenen Unterlagen. Diese Mail enthaelt
alles; die beiden vorherigen Mails von heute sind damit ueberholt.
Kein Ersatz fuer anwaltliche Beratung.
</p>
</div>
""")

mail = env['mail.mail'].sudo().create({
    'subject': 'Viechtach - GEKUERZTE Fassung, 2-Seiten-Anschreiben '
               '(Frist 17.09.2026)',
    'body_html': koerper,
    'email_to': EMPFAENGER,
    'attachment_ids': [(6, 0, anhaenge)],
    'auto_delete': False,
})
mail.send()
env.cr.commit()

mail.invalidate_recordset()
print('')
print('  Mail-ID %s an %s -> %s' % (mail.id, EMPFAENGER, mail.state))
if mail.state == 'exception':
    print('  FEHLER: %s' % mail.failure_reason)

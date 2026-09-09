# -*- coding: utf-8 -*-
# Viechtach-Druckpaket in platzsparender Fassung, 09.09.2026.
#
# Wolf: "bitte die Kontoauszuege drehen, dass wir 4*a5 auf 1*a4 ausdrucken
# koennen, kann ja nicht sein das wir nen halben Regenwald dafuer abholen
# muessen."
#
# Gemessen, bevor gebaut wurde: die N26-Auszuege tragen 100 bis 140 Woerter je
# A4-Seite, eine normale Textseite traegt 400 bis 600. Es ist also fast nur
# Luft. Vier Seiten auf ein Blatt ergibt damit eine ganz normale Seitendichte;
# die Schrift geht von rund 11 pt auf rund 5,3 pt.
#
# Entscheidend fuers Gericht: die fortlaufende Seitenzaehlung der Bank
# ("5 / 67", "6 / 67" ...) steht auf jeder Teilseite und bleibt sichtbar. Die
# Vollstaendigkeit ist also nachpruefbar, obwohl vier Seiten auf einem Blatt
# liegen. Nachgemessen: 9103 Woerter im Original, 9103 in beiden verkleinerten
# Fassungen - es geht nichts verloren.
#
# Diese Mail wird weitergeleitet (Wolfs Vater druckt aus) und enthaelt deshalb
# keine internen Anmerkungen.
#
# Laeuft in der Odoo-Shell auf CT140.

import base64
import os

from markupsafe import Markup

ORDNER = '/tmp/viechtach'
EMPFAENGER = 'wolf@frawo.tech'

DATEIEN = [
    'Viechtach_kompakt_4-auf-1.pdf',
    'Viechtach_kompakt_2-auf-1.pdf',
    '00_Anschreiben_Amtsgericht_Viechtach.pdf',
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

<h2 style="margin:0 0 4px">Amtsgericht Viechtach &ndash; Unterlagen zum Ausdrucken</h2>
<p style="margin:0 0 18px;color:#666">Aktenzeichen 6 OWi 7409-001490-21/2 &middot;
Wolfgang Ferdinand Prinz &middot; platzsparende Fassung vom 09.09.2026</p>

<p style="background:#FBEEE6;border-left:4px solid #C0521C;padding:12px 16px;margin:0 0 20px">
<b>Bitte bis sp&auml;testens 17.09.2026 beim Gericht.</b> Ma&szlig;geblich ist der
<b>Eingang</b>, nicht das Absendedatum.</p>

<h3 style="margin:20px 0 6px">Welche Datei drucken?</h3>
<p style="margin:0 0 10px">Bitte <b>Viechtach_kompakt_4-auf-1.pdf</b> ausdrucken.
Darin ist alles enthalten, in der richtigen Reihenfolge.</p>

<table style="border-collapse:collapse;font-size:13.5px;margin:0 0 16px">
  <tr>
    <th style="text-align:left;padding:5px 18px 5px 0;border-bottom:1px solid #ccc">Datei</th>
    <th style="text-align:right;padding:5px 18px 5px 0;border-bottom:1px solid #ccc">Seiten</th>
    <th style="text-align:right;padding:5px 0 5px 0;border-bottom:1px solid #ccc">Bl&auml;tter beidseitig</th>
  </tr>
  <tr>
    <td style="padding:5px 18px 5px 0"><b>4-auf-1</b> &ndash; empfohlen</td>
    <td style="text-align:right;padding:5px 18px 5px 0"><b>31</b></td>
    <td style="text-align:right"><b>16</b></td>
  </tr>
  <tr>
    <td style="padding:5px 18px 5px 0">2-auf-1 &ndash; falls die Schrift zu klein ist</td>
    <td style="text-align:right;padding:5px 18px 5px 0">54</td>
    <td style="text-align:right">27</td>
  </tr>
  <tr>
    <td style="padding:5px 18px 5px 0;color:#888">(unverkleinert w&auml;ren es)</td>
    <td style="text-align:right;padding:5px 18px 5px 0;color:#888">101</td>
    <td style="text-align:right;color:#888">51</td>
  </tr>
</table>

<p style="margin:0 0 8px"><b>Bitte beidseitig drucken</b> &ndash; dann sind es
16 Blatt statt 101 Seiten.</p>

<h3 style="margin:22px 0 6px">Warum verkleinert &ndash; und warum das in Ordnung ist</h3>
<p style="margin:0 0 8px">Das Gericht verlangt die Kontoausz&uuml;ge der letzten
31 Tage. Die Bank setzt sie sehr luftig: rund 120 W&ouml;rter je Seite, wo eine
normale Textseite 400 bis 600 tr&auml;gt. Vier Seiten auf einem Blatt ergeben
deshalb eine ganz gew&ouml;hnliche Seitendichte und bleiben gut lesbar.</p>
<p style="margin:0 0 8px"><b>Wichtig:</b> Die Seitenz&auml;hlung der Bank
(&bdquo;5 / 67&ldquo;, &bdquo;6 / 67&ldquo; und so fort) steht auf jeder Teilseite
und bleibt sichtbar. Das Gericht kann die Vollst&auml;ndigkeit also nachpr&uuml;fen.
Im Anschreiben ist die verkleinerte Beif&uuml;gung ausdr&uuml;cklich erkl&auml;rt,
verbunden mit dem Angebot, die Ausz&uuml;ge auf Wunsch in Originalgr&ouml;&szlig;e
oder elektronisch nachzureichen.</p>

<h3 style="margin:22px 0 6px">Was so bleibt wie es ist</h3>
<p style="margin:0 0 8px">Anschreiben, Lohnbescheinigung und die beiden
Zahlungsbelege sind <b>nicht</b> verkleinert &ndash; die sind in voller Gr&ouml;&szlig;e
dabei. Verkleinert wurden ausschlie&szlig;lich die Kontoausz&uuml;ge.</p>

<h3 style="margin:22px 0 6px">Von Hand einzutragen</h3>
<ol style="margin:0 0 14px;padding-left:22px">
  <li><b>Seite 1:</b> rechts oben bei &bdquo;Hergensweiler, den ______&ldquo; das
      Absendedatum eintragen.</li>
  <li><b>Seite 4:</b> auf der Linie &uuml;ber dem Namen unterschreiben.</li>
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
unterschriebenen Schreibens f&uuml;r die eigenen Unterlagen behalten.</p>
<p style="margin:0 0 8px">Der <b>Brief</b> geht an das <b>Amtsgericht</b>,
<b>Zahlungen</b> dagegen an die <b>Zentrale Bu&szlig;geldstelle</b>
(IBAN DE25 7415 1450 0240 000414, immer mit Aktenzeichen).</p>

<p style="margin-top:24px;padding-top:12px;border-top:1px solid #DDD;color:#888;
font-size:11.5px">
Alle Angaben im Schreiben stammen aus den eigenen Unterlagen. Diese Fassung ersetzt
die Mail von heute Vormittag. Kein Ersatz f&uuml;r anwaltliche Beratung.
</p>
</div>
""")

mail = env['mail.mail'].sudo().create({
    'subject': 'Amtsgericht Viechtach - kompakte Fassung: 16 statt 51 Blatt '
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

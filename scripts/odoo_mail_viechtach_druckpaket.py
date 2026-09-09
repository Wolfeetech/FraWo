# -*- coding: utf-8 -*-
# Verschickt das vollstaendige Viechtach-Druckpaket, 09.09.2026.
#
# Wolf am 09.09.2026: "so jetzt auch noch der September Auszug im Ordner, das
# alles jetzt per Mail an mich, dass ich es meinem Vater zusenden kann dass er
# das ausdrucken kann"
#
# ABSICHT DIESER FASSUNG
# Die Mail wird WEITERGELEITET. Sie enthaelt deshalb bewusst KEINE internen
# Anmerkungen, Rueckfragen oder Bewertungen - nur das, was jemand braucht,
# der das Paket ausdruckt und nicht im Vorgang steckt. Alles Interne steht
# in Odoo-Aufgabe #1360 und in der vorherigen Mail an Wolf.
#
# Laeuft in der Odoo-Shell auf CT140.

import base64
import os

from markupsafe import Markup

ORDNER = '/tmp/viechtach'
EMPFAENGER = 'wolf@frawo.tech'

DATEIEN = [
    'Viechtach_komplett_zum_Ausdrucken.pdf',   # alles in einem, 101 Seiten
    '00_Anschreiben_Amtsgericht_Viechtach.pdf',
    'Anlage_1_Gehaltsabrechnung_August_2026.pdf',
    'Anlage_2_Kontoauszug_08-2026.pdf',
    'Anlage_2b_Kontoauszug_09-2026.pdf',
    'Anlage_3_Zahlung_100EUR_30-08-2026.pdf',
    'Anlage_4_Zahlung_32-99EUR_03-09-2026.pdf',
]

anhaenge = []
fehlend = []
gesamt = 0

for name in DATEIEN:
    pfad = os.path.join(ORDNER, name)
    if not os.path.exists(pfad):
        fehlend.append(name)
        continue
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
    print('  angehaengt: %-48s %7.1f KB' % (name, len(roh) / 1024.0))

if fehlend:
    print('')
    print('  FEHLT: %s' % ', '.join(fehlend))
    raise Exception('Unvollstaendig - nichts verschickt.')

print('')
print('  %d Anhaenge, %.2f MB' % (len(anhaenge), gesamt / 1048576.0))

koerper = Markup("""
<div style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:1.6;
color:#191B1E;max-width:720px">

<h2 style="margin:0 0 4px">Amtsgericht Viechtach &ndash; Unterlagen zum Ausdrucken</h2>
<p style="margin:0 0 18px;color:#666">Aktenzeichen 6 OWi 7409-001490-21/2 &middot;
Wolfgang Ferdinand Prinz &middot; Stand 09.09.2026</p>

<p style="background:#FBEEE6;border-left:4px solid #C0521C;padding:12px 16px;margin:0 0 20px">
<b>Bitte bis sp&auml;testens 17.09.2026 beim Gericht.</b> Ma&szlig;geblich ist der
<b>Eingang</b>, nicht das Absendedatum.</p>

<h3 style="margin:20px 0 6px">Zum Drucken</h3>
<p style="margin:0 0 10px">Es reicht <b>eine</b> Datei:
<b>Viechtach_komplett_zum_Ausdrucken.pdf</b> &ndash; darin ist alles in der richtigen
Reihenfolge enthalten.</p>
<table style="border-collapse:collapse;font-size:13.5px;margin:0 0 14px">
  <tr><td style="padding:3px 16px 3px 0">Umfang</td><td><b>101 Seiten, DIN A4</b></td></tr>
  <tr><td style="padding:3px 16px 3px 0">Seiten 1&ndash;4</td><td>das Anschreiben</td></tr>
  <tr><td style="padding:3px 16px 3px 0">Seite 5</td><td>Anlage 1 &ndash; Lohnbescheinigung August 2026</td></tr>
  <tr><td style="padding:3px 16px 3px 0">Seiten 6&ndash;72</td><td>Anlage 2 &ndash; Kontoauszug August 2026</td></tr>
  <tr><td style="padding:3px 16px 3px 0">Seiten 73&ndash;99</td><td>Anlage 2 &ndash; Kontoauszug September 2026 (bis 09.09.)</td></tr>
  <tr><td style="padding:3px 16px 3px 0">Seite 100</td><td>Anlage 3 &ndash; Zahlungsbeleg 100,00 EUR</td></tr>
  <tr><td style="padding:3px 16px 3px 0">Seite 101</td><td>Anlage 4 &ndash; Zahlungsbeleg 32,99 EUR</td></tr>
</table>
<p style="margin:0 0 8px">Die Kontoausz&uuml;ge machen den gr&ouml;&szlig;ten Teil aus.
Das Gericht verlangt sie ausdr&uuml;cklich f&uuml;r die letzten 31 Tage, deshalb sind
sie vollst&auml;ndig dabei. <b>Beidseitig drucken</b> spart die H&auml;lfte Papier.</p>
<p style="margin:0 0 8px">Die Einzeldateien h&auml;ngen zus&auml;tzlich an, falls
etwas einzeln nachgedruckt werden muss.</p>

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
<p style="margin:0 0 8px">Wichtig: Der <b>Brief</b> geht an das <b>Amtsgericht</b>,
<b>Zahlungen</b> dagegen an die <b>Zentrale Bu&szlig;geldstelle</b>
(IBAN DE25 7415 1450 0240 000414, immer mit Aktenzeichen). Das nicht verwechseln.</p>

<p style="margin-top:24px;padding-top:12px;border-top:1px solid #DDD;color:#888;
font-size:11.5px">
Alle Angaben im Schreiben stammen aus den eigenen Unterlagen (Lohnabrechnung,
Kontoausz&uuml;ge, Zahlungsbelege). Kein Ersatz f&uuml;r anwaltliche Beratung.
</p>
</div>
""")

mail = env['mail.mail'].sudo().create({
    'subject': 'Amtsgericht Viechtach - Unterlagen zum Ausdrucken '
               '(101 Seiten, Frist 17.09.2026)',
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

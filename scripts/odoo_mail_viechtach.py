# -*- coding: utf-8 -*-
# Verschickt das Viechtach-Paket per E-Mail an Wolf, 09.09.2026.
#
# Wolf am 09.09.2026: "bitte alles fuer Viechtach per Mail an mich.
# zum kontrollieren und ausdrucken."
#
# Die Dateien liegen in /tmp/viechtach im Odoo-Container. Der Versand laeuft
# ueber Odoos eigenen Postausgang (Brevo) - derselbe Weg wie der Tagesbericht,
# nachweislich funktionsfaehig (417 gesendete Mails, 0 Fehler).
#
# Laeuft in der Odoo-Shell auf CT140.

import base64
import os

from markupsafe import Markup

ORDNER = '/tmp/viechtach'
EMPFAENGER = 'wolf@frawo.tech'

# Reihenfolge = Reihenfolge im Mailprogramm.
DATEIEN = [
    ('00_Anschreiben_Amtsgericht_Viechtach.pdf',
     'Das Anschreiben - ausdrucken, Datum eintragen, unterschreiben'),
    ('Anlage_1_Gehaltsabrechnung_August_2026.pdf',
     'Anlage 1 - Lohnbescheinigung August 2026'),
    ('Anlage_2_Kontoauszug_08-2026.pdf',
     'Anlage 2 - Kontoauszug August (September fehlt noch!)'),
    ('Anlage_3_Zahlung_100EUR_30-08-2026.pdf',
     'Anlage 3 - Teilzahlung 100 EUR vom 30.08.2026'),
    ('Anlage_4_Zahlung_32-99EUR_03-09-2026.pdf',
     'Anlage 4 - Zahlung 32,99 EUR an das Finanzamt'),
    ('Schreiben_des_Gerichts_03.09.2026.pdf',
     'Zum Nachlesen: das Schreiben des Gerichts, auf das geantwortet wird'),
]

anhaenge = []
fehlend = []
gesamt = 0

for name, _zweck in DATEIEN:
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
        'res_id': 1360,          # haengt am Vorgang, nicht lose herum
    })
    anhaenge.append(a.id)
    print('  angehaengt: %-52s %7.1f KB' % (name, len(roh) / 1024.0))

if fehlend:
    print('')
    print('  FEHLT: %s' % ', '.join(fehlend))

print('')
print('  %d Anhaenge, %.2f MB gesamt' % (len(anhaenge), gesamt / 1048576.0))

koerper = Markup("""
<div style="font-family:Helvetica,Arial,sans-serif;font-size:14px;line-height:1.55">
<h2 style="margin:0 0 4px">Viechtach - Antwortschreiben zum Pruefen und Ausdrucken</h2>
<p style="margin:0 0 16px;color:#666">Az. 6 OWi 7409-001490-21/2 &middot;
erstellt am 09.09.2026</p>

<p style="background:#FBEEE6;border-left:4px solid #C0521C;padding:12px 16px;margin:0 0 16px">
<b>Frist: rund 17.09.2026.</b> Das Gericht hat am 03.09.2026 eine <b>Nachfrist von
zwei Wochen</b> gesetzt. Woertlich: <i>"Bei nicht rechtzeitiger Beantwortung gilt Ihr
Gesuch auf Zahlungserleichterung als abgelehnt. Eine erneute Information hierueber
erfolgt nicht."</i> Es kommt also keine Erinnerung mehr.</p>

<h3 style="margin:18px 0 6px">Was du noch tun musst</h3>
<ol>
  <li><b>September-Kontoauszug exportieren</b> und als Teil von Anlage 2 beilegen.
      Das Gericht will die letzten 31 Tage; ab dem 03.09. reicht das bis zum 03.08.
      zurueck. Nur der August-Auszug liegt bisher vor.</li>
  <li><b>Datum eintragen und unterschreiben</b> im Anschreiben.</li>
  <li><b>Absenden - Eingang bei Gericht zaehlt</b>, nicht das Absendedatum.
      Bei knapper Frist faxen: <b>+49 9621 96241 4140</b>, Sendebericht aufheben.</li>
  <li>Getrennt davon: Die <b>100-EUR-Rate an das Polizeiverwaltungsamt</b> ist seit
      dem 08.09. faellig. Ob sie geflossen ist, geht aus den Unterlagen nicht
      hervor - bitte gegenpruefen. Der Brief geht ans <b>Amtsgericht</b>,
      das Geld an die <b>Zentrale Bussgeldstelle</b>.</li>
</ol>

<h3 style="margin:18px 0 6px">Was sich gegenueber der Fassung von gestern geaendert hat</h3>
<p><b>1. Es gibt ein neues Schreiben vom 03.09.2026</b>, das mir gestern noch nicht
vorlag (der Dateiname traegt dein Scandatum). Das Gericht sagt darin, eine
ausreichende Begruendung sei bisher nicht eingegangen - die Teilzahlung ist also
angekommen, es fehlt die Begruendung mit Belegen. Der Brief ist deshalb jetzt
<b>entlang der vier geforderten Punkte gegliedert</b>, damit das Gericht abhaken kann.</p>

<p><b>2. Ich hatte dein Einkommen zu hoch angesetzt.</b> Mein erster Entwurf nannte
2.402,76 EUR als Nettoeinkommen. Das ist der <i>Auszahlungsbetrag</i> und enthaelt
einmalige Nachberechnungen aus 2025. Das laufende Netto sind laut Abrechnung
<b>2.159,26 EUR</b>. Der Brief nennt jetzt beide Zahlen und erklaert den Unterschied -
das ist ehrlicher und fuer dich guenstiger, weil das Gericht sonst von rund 240 EUR
mehr ausgegangen waere.</p>

<h3 style="margin:18px 0 6px">Ein Punkt, den ich bewusst NICHT hineingeschrieben habe</h3>
<p>Auf der Gehaltsabrechnung stehen zwei Positionen <b>"9810 gewoehnliche Pfaendung"</b>
als Nachberechnung fuer 08/2025 und 09/2025 (zusammen rund 269 EUR, als Gutschrift).
Das deutet auf eine Lohnpfaendung hin, die rueckabgewickelt wurde.</p>
<p>Eine <b>laufende</b> Lohnpfaendung waere ein starkes Argument fuer deine
Zahlungsunfaehigkeit - eine beendete ist es nicht. Da ich das aus der Abrechnung
allein nicht sicher sagen kann, steht es nicht im Brief.
<b>Falls aktuell eine Pfaendung laeuft, sag Bescheid</b> - dann gehoert sie mit
Nachweis hinein, und zwar prominent.</p>

<h3 style="margin:18px 0 6px">Im Anhang</h3>
<ul>
  <li><b>00_Anschreiben</b> - der Brief selbst, druckfertig</li>
  <li><b>Anlage 1</b> - Lohnbescheinigung August 2026</li>
  <li><b>Anlage 2</b> - Kontoauszug August (September ergaenzen)</li>
  <li><b>Anlage 3</b> - Teilzahlung 100 EUR vom 30.08.2026</li>
  <li><b>Anlage 4</b> - Zahlung 32,99 EUR an das Finanzamt</li>
  <li><b>Schreiben des Gerichts</b> vom 03.09.2026 zum Nachlesen</li>
</ul>

<p style="margin-top:22px;padding-top:12px;border-top:1px solid #DDD;color:#888;
font-size:11.5px">
Alle Zahlen stammen aus deinen eigenen Unterlagen; die Quelle jeder Zahl steht in
<code>DOCS/2026-09-09_Antwort_Amtsgericht_Viechtach.md</code>.
Vorgang in Odoo: Aufgabe #1360. Kein Ersatz fuer anwaltliche Beratung.<br>
Erstellt von Claude Code, verschickt ueber Odoo.
</p>
</div>
""")

mail = env['mail.mail'].sudo().create({
    'subject': 'Viechtach: Antwortschreiben + Anlagen zum Pruefen '
               '(Frist ~17.09.2026)',
    'body_html': koerper,
    'email_to': EMPFAENGER,
    'attachment_ids': [(6, 0, anhaenge)],
    'auto_delete': False,      # bleibt stehen, damit der Versand nachweisbar ist
})
mail.send()

env.cr.commit()

# Regel 1: das Ergebnis am Ziel pruefen, nicht dem Aufruf glauben.
mail.invalidate_recordset()
print('')
print('  Mail-ID %s an %s' % (mail.id, EMPFAENGER))
print('  Zustand: %s' % mail.state)
if mail.state == 'exception':
    print('  FEHLER: %s' % mail.failure_reason)
elif mail.state == 'sent':
    print('  Versendet.')
else:
    print('  Steht in der Warteschlange - Cron "Mail: Email Queue Manager" holt sie ab.')

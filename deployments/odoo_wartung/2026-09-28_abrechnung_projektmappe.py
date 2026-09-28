# 🤖 [Claude] 28.09.2026, Odoo #1595 — Abrechnung aus der Projektmappe.
# Ablauf: (1) Einrichtung anlegen, (2) Wasserburg-Szenario komplett durchspielen,
# (3) IMMER zuruecksetzen, (4) nur wenn COMMIT und alle Pruefungen gruen: Einrichtung erneut anlegen + commit.
COMMIT = __COMMIT__
import datetime
ctx = dict(tracking_disable=True, mail_notrack=True, dont_notify=True,
           mail_auto_subscribe_no_notify=True, mail_create_nolog=True, no_mail_to_attendees=True)
E = env(context=dict(env.context, **ctx))

CODE = '''
# FraWo (Claude, 28.09.2026, Odoo #1595): Einsatztage aus der Zeiterfassung.
# Tagessatz-Position (Ist-Menge manuell, mit Aufgabe in der Mappe) = Anzahl Tage mit Zeiteintrag je Person,
# hoechstens die beauftragte Menge. Mehr = Hinweis "Nachtrag", nie automatisch berechnet.
# Anfahrt (SRV-ANFAHRT) gilt als erbracht, sobald im Auftrag ein Einsatztag erfasst ist.
ausschluss = records.ids if AUSSCHLUSS else []
zeilen = records.mapped('task_id.sale_line_id').filtered(
    lambda l: l.qty_delivered_method == 'manual' and l.task_id and l.state == 'sale')
for zeile in zeilen:
    eintraege = env['account.analytic.line'].search([
        ('task_id.sale_line_id', '=', zeile.id), ('unit_amount', '>', 0), ('id', 'not in', ausschluss)])
    tage = len(set([(t.employee_id.id, t.date) for t in eintraege]))
    neu = min(tage, zeile.product_uom_qty)
    if zeile.qty_delivered != neu:
        zeile.write({'qty_delivered': neu})
    if tage > zeile.product_uom_qty and not AUSSCHLUSS:
        zeile.order_id.message_post(
            body="Mehrleistung: %s Einsatztage erfasst, beauftragt %s (%s). Nicht berechnet - Nachtrag noetig?"
                 % (tage, zeile.product_uom_qty, zeile.name.split(chr(10))[0]),
            message_type='comment', subtype_xmlid='mail.mt_note')
for auftrag in zeilen.mapped('order_id'):
    einsatz = any(l.qty_delivered > 0 for l in auftrag.order_line.filtered(lambda l: l.qty_delivered_method == 'manual' and l.task_id))
    for anfahrt in auftrag.order_line.filtered(
            lambda l: l.product_id.default_code == 'SRV-ANFAHRT' and l.qty_delivered_method == 'manual'):
        soll = anfahrt.product_uom_qty if einsatz else 0
        if anfahrt.qty_delivered != soll:
            anfahrt.write({'qty_delivered': soll})
'''

def einrichten():
    t2, t6, t153 = E['product.template'].browse([2, 6, 153])
    for t in (t2, t153):
        t.write({'project_id': False, 'service_policy': 'delivered_manual',
                 'service_tracking': 'task_in_project', 'project_template_id': 164})
    t6.write({'service_policy': 'delivered_manual'})
    E['project.project'].browse(164).write({'allow_billable': True, 'allow_timesheets': True, 'name': 'Projektmappe'})
    E['project.task'].browse(1449).write({'name': '🎪 Einsatz: Planung, Packliste, Live-Betrieb, Abbau'})
    E['project.task'].browse(1420).write({'active': False})
    if not E['project.task'].search_count([('project_id', '=', 164), ('name', 'like', 'Leistungsnachweis')]):
        E['project.task'].create({'project_id': 164, 'name': '🧾 Leistungsnachweis & Abrechnung', 'description': (
            '<p><b>So wird aus dieser Mappe abgerechnet:</b></p><ol>'
            '<li>Pro Person und Einsatztag <b>einen Zeiteintrag</b> auf ihrer Aufgabe (echte Stunden, Uhrzeit in die Beschreibung, z. B. „Sa 09:00–22:00 VA-Tag“).</li>'
            '<li>Odoo zählt daraus die <b>Einsatztage</b> (höchstens die beauftragten) und hakt die Anfahrt ab.</li>'
            '<li>Abweichungen (jemand fehlt, Tag entfällt) = <b>kein Eintrag</b> + kurze Notiz hier im Chatter.</li>'
            '<li>Hinweis „Mehrleistung“ im Auftrag = mehr Tage als beauftragt → Nachtrag mit dem Kunden klären, erst dann Position ergänzen.</li>'
            '<li>Oben in der Mappe <b>„Rechnung erstellen“</b> → Entwurf prüfen → Buchen.</li></ol>'
            '<p>Ein Auftrag pro Einsatz. Kundenreferenz = Eventname (wird Mappenname).</p>')})
    modell =E['ir.model']._get('account.analytic.line')
    ergebnis = []
    for name, trigger, aus in (('erfassen/aendern', 'on_create_or_write', 'False'), ('loeschen', 'on_unlink', 'True')):
        sa = E['ir.actions.server'].create({
            'name': 'FraWo: Einsatztage aus Zeiterfassung (%s)' % name, 'model_id': modell.id,
            'state': 'code', 'usage': 'base_automation', 'code': 'AUSSCHLUSS = %s\n' % aus + CODE})
        vals = {'name': 'FraWo: Einsatztage aus Zeiterfassung (%s)' % name, 'model_id': modell.id,
                'trigger': trigger, 'action_server_ids': [(6, 0, [sa.id])], 'active': True}
        if trigger == 'on_create_or_write':
            vals['trigger_field_ids'] = [(6, 0, E['ir.model.fields'].search([
                ('model', '=', 'account.analytic.line'),
                ('name', 'in', ['unit_amount', 'date', 'employee_id', 'task_id'])]).ids)]
        ergebnis.append(E['base.automation'].create(vals))
    return ergebnis

fehler = []
def pruefe(name, ist, soll):
    ok = abs((ist or 0) - soll) < 0.001
    print(("OK   " if ok else "FAIL ") + "%s: ist %s, soll %s" % (name, ist, soll))
    if not ok:
        fehler.append(name)

# ---------- (1)+(2) Test ----------
autos = einrichten()
print("Automatiken:", [(a.id, a.name) for a in autos])
so = E['sale.order'].create({'partner_id': 10, 'client_order_ref': 'Wasserburg Closing 26.09.', 'order_line': [
    (0, 0, {'display_type': 'line_section', 'name': 'TEST Wasserburg'}),
    (0, 0, {'product_id': 6, 'product_uom_qty': 1, 'price_unit': 20, 'discount': 50}),
    (0, 0, {'product_id': 2, 'name': 'Helfer Tagessatz [WOLFI] pauschal Fr+Sa', 'product_uom_qty': 1, 'price_unit': 350}),
    (0, 0, {'product_id': 2, 'name': 'Helfer Tagessatz [FRANZ]', 'product_uom_qty': 2, 'price_unit': 300, 'discount': 25}),
]})
so.action_confirm()
anf, wolfi, franz = so.order_line.filtered(lambda l: not l.display_type)
print("Projekt:", so.project_ids.mapped('name'), "abrechenbar:", so.project_ids.mapped('allow_billable'),
      "Aufgaben:", len(so.tasks_ids), "| Einheit Helfer:", wolfi.product_uom_id.name, "| Methode:", wolfi.qty_delivered_method)
pruefe("eigene Mappe angelegt", len(so.project_ids), 1)
pruefe("Wolfi und Franz je eigene Aufgabe", 1 if (wolfi.task_id and franz.task_id and wolfi.task_id != franz.task_id) else 0, 1)
print("Aufgaben der Mappe:", so.project_ids.task_ids.mapped("name"))

fr = datetime.date(2026, 9, 25); sa = datetime.date(2026, 9, 26)
def buche(zeile, emp, tag, std, txt):
    return E['account.analytic.line'].create({'task_id': zeile.task_id.id, 'project_id': zeile.task_id.project_id.id,
                                              'employee_id': emp, 'date': tag, 'unit_amount': std, 'name': txt})
buche(franz, 3, fr, 8, 'Fr Aufbau 08:00-16:00')
x = buche(franz, 3, sa, 13, 'Sa VA-Tag 09:00-22:00')
buche(wolfi, 2, fr, 6, 'Fr Aufbau 08:00-14:00')
buche(wolfi, 2, sa, 13, 'Sa Betreuung 09:00-22:00')
so.invalidate_recordset()
pruefe("Franz 2 Tage (8 h + 13 h, keine 2,6)", franz.qty_delivered, 2)
pruefe("Wolfi pauschal: 2 Tage erfasst, beauftragt 1", wolfi.qty_delivered, 1)
pruefe("Anfahrt erbracht", anf.qty_delivered, 1)
pruefe("Hinweis Mehrleistung Wolfi", len(so.message_ids.filtered(lambda m: 'Mehrleistung' in (m.body or ''))), 1)
x.unlink(); so.invalidate_recordset()
pruefe("Loeschen: Franz faellt auf 1", franz.qty_delivered, 1)
buche(franz, 3, sa, 13, 'Sa VA-Tag 09:00-22:00'); so.invalidate_recordset()
pruefe("wieder 2", franz.qty_delivered, 2)

aktion = so.project_ids[0].action_create_invoice()
print("Rechnen aus Projekt oeffnet:", aktion.get('res_model'), aktion.get('context', {}).get('active_ids') if isinstance(aktion.get('context'), dict) else '')
wiz = E['sale.advance.payment.inv'].with_context(active_model='sale.order', active_ids=so.ids).create(
    {'advance_payment_method': 'delivered', 'sale_order_ids': [(6, 0, so.ids)]})
wiz.create_invoices()
rech = so.invoice_ids
print("Rechnung:", rech.state, rech.amount_total, [(l.name.split(chr(10))[0][:30], l.quantity, l.price_subtotal) for l in rech.invoice_line_ids if l.display_type == 'product'])
pruefe("Rechnungssumme = 810 (10 + 350 + 450)", rech.amount_total, 810)
pruefe("Rechnung nur Entwurf", 1 if rech.state == 'draft' else 0, 1)

# ---------- (3) immer zuruecksetzen ----------
env.cr.rollback()
print("TEST zurueckgesetzt. Fehler:", fehler or "keine")

# ---------- (4) Einrichtung dauerhaft ----------
if COMMIT and not fehler:
    autos = einrichten()
    env.cr.commit()
    print("COMMIT Einrichtung:", [(a.id, a.name) for a in autos])
else:
    print("KEIN COMMIT")

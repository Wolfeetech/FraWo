# 🤖 [Claude] 29.09.2026, Odoo #1640 — Angebotsvorlagen fuer die freigegebenen Pakete (Wolf 28.09.) + Ablauftest.
# Alte Mietpark-Vorlagen mit widerspruechlichen Preisen werden ARCHIVIERT (nicht geloescht). Idempotent ueber den Namen.
COMMIT = __COMMIT__
TEST = __TEST__
E = env(context=dict(env.context, tracking_disable=True, mail_notrack=True, dont_notify=True,
                     mail_create_nolog=True, mail_auto_subscribe_no_notify=True))
n0 = E['mail.notification'].search_count([('res_partner_id', '=', 7)])
mm0 = E['mail.mail'].search_count([])
P = lambda code: E['product.product'].search([('default_code', '=', code)], limit=1)
NOTIZ = ('<p>Alle Preise sind Endpreise. Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.</p>'
         '<p>Im Paket enthalten: Anlieferung, Aufbau, Betreuung vor Ort und Abbau bis 30 km. '
         'Zusatzstunden und weitere Kilometer nach Aufwand (siehe optionale Positionen).</p>')
VORLAGEN = [
    ('📦 Paket S · Hoffest & Vereinsabend (bis 100 Pers.)', 'PAKET-S', ['SRV-ZUSATZSTUNDE', 'SRV-KM', 'VER-005'], NOTIZ),
    ('📦 Paket M · Fest & Feier (bis 250 Pers.)', 'PAKET-M', ['SRV-ZUSATZSTUNDE', 'SRV-KM', 'VER-005'], NOTIZ),
    ('📦 Paket L · Open Air & Event (bis 500 Pers.)', 'PAKET-L', ['SRV-ZUSATZSTUNDE', 'SRV-KM', 'VER-005'], NOTIZ),
    ('⚽ Fußballdart – Event-Modul (pro Tag)', 'VER-005', ['SRV-LIEFERUNG', 'SRV-KM-LIEFERUNG', 'SRV-ZUSATZSTUNDE'],
     '<p>Alle Preise sind Endpreise. Gemäß § 19 UStG wird keine Umsatzsteuer berechnet.</p>'
     '<p>Mit Betreuung: Aufbau, Einweisung und Abbau durch FraWo. Nur Lieferung: Pauschale plus Kilometer (optionale Positionen).</p>'),
]
T = E['sale.order.template']
neu = {}
for i, (name, haupt, optionen, notiz) in enumerate(VORLAGEN):
    for c in [haupt] + optionen:
        assert P(c), 'Artikel fehlt: ' + c
    t = T.with_context(active_test=False).search([('name', '=', name)], limit=1)
    zeilen = [(5, 0, 0), (0, 0, {'product_id': P(haupt).id, 'product_uom_qty': 1, 'sequence': 10})]
    # Optionale Zeilen zaehlen in Odoo 19 in die Summe (Test 29.09.: Paket S 749,50 statt 449) -> Zusaetze nur im Hinweistext.
    zusatz = ''.join('<li>%s: %s €</li>' % (P(c).name, ('%.2f' % P(c).list_price).replace('.', ',')) for c in optionen)
    notiz = notiz + '<p><b>Auf Wunsch zubuchbar:</b></p><ul>' + zusatz + '</ul>'
    vals = {'name': name, 'active': True, 'number_of_days': 14, 'note': notiz, 'sequence': 1 + i,
            'sale_order_template_line_ids': zeilen}
    t = t.write(vals) and t if t else T.create(vals)
    neu[haupt] = t
    print('VORLAGE', t.id, t.name, [(l.product_id.default_code, l.is_optional, l.product_id.list_price) for l in t.sale_order_template_line_ids])
alt = T.browse([4, 5, 6, 7]).exists()
print('ARCHIVIERT', [(x.id, x.name) for x in alt])
alt.write({'active': False})

if TEST:
    # Ablauf: Anfrage -> Angebot aus Vorlage -> Bestaetigung -> Mappe
    kunde = E['res.partner'].create({'name': 'Testkunde Claude #1640', 'email': 'test-1640@example.invalid'})
    lead = E['crm.lead'].create({'name': 'Hoffest Test #1640', 'partner_id': kunde.id, 'type': 'opportunity'})
    so = E['sale.order'].create({'partner_id': kunde.id, 'opportunity_id': lead.id, 'sale_order_template_id': neu['PAKET-S'].id})
    so._onchange_sale_order_template_id()
    feste = so.order_line.filtered(lambda l: not l.display_type and not getattr(l, 'is_optional', False))
    opt = so.order_line.filtered(lambda l: getattr(l, 'is_optional', False))
    print('ANGEBOT', so.name, '| Summe', so.amount_total, '| feste Zeilen', [(l.product_id.default_code, l.price_unit) for l in feste],
          '| optional', [(l.product_id.default_code, l.price_unit) for l in opt], '| Steuer', so.amount_tax)
    so.action_confirm()
    proj = so.project_ids if 'project_ids' in so._fields else E['project.project']
    auf = E['project.task'].search([('sale_order_id', '=', so.id)])
    print('BESTAETIGT', so.state, '| Mappe(n)', [(p.id, p.name) for p in proj], '| Aufgaben', len(auf))
    print('Mails', E['mail.mail'].search_count([]) - mm0)

print('neue Benachrichtigungen:', E['mail.notification'].search_count([('res_partner_id', '=', 7)]) - n0)
if COMMIT:
    env.cr.commit(); print('COMMIT')
else:
    env.cr.rollback(); print('ROLLBACK (Probelauf)')

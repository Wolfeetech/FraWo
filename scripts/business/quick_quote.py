#!/usr/bin/env python3
"""
FraWo Quick-Quote Engine
Creates a complete, professional draft quotation in Odoo in under 2 seconds.
Usage:
    python quick_quote.py --lead 72 --template 7 --date 2027-08-15
    python quick_quote.py --partner "Gierer" --template "Event"
"""

import sys
import os
import argparse
from pathlib import Path

# Add shared business path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mcp_odoo_pro_server as odoo

def create_quick_quote(partner_query=None, lead_id=None, template_query=None, event_date=None, salesperson_id=6):
    """Generates a sale.order from a template and links it to lead/partner."""
    # 1. Resolve Partner & Lead
    partner_id = None
    partner_name = "Kunde"
    
    if lead_id:
        leads = odoo.odoo_search_read('crm.lead', [('id', '=', int(lead_id))], ['id', 'name', 'partner_id', 'user_id', 'team_id'])
        if not leads:
            print(f"Error: Lead #{lead_id} not found.")
            return None
        lead = leads[0]
        if lead.get('partner_id'):
            partner_id = lead['partner_id'][0]
            partner_name = lead['partner_id'][1]
        team_id = lead.get('team_id')[0] if lead.get('team_id') else 1
    elif partner_query:
        partners = odoo.odoo_search_read('res.partner', [('name', 'ilike', partner_query)], ['id', 'name'], limit=1)
        if not partners:
            print(f"Error: Partner matching '{partner_query}' not found.")
            return None
        partner_id = partners[0]['id']
        partner_name = partners[0]['name']
        team_id = 1
        # Check if there is an open lead for this partner
        open_leads = odoo.odoo_search_read('crm.lead', [('partner_id', '=', partner_id), ('active', '=', True)], ['id', 'name'], limit=1)
        lead_id = open_leads[0]['id'] if open_leads else None
    else:
        print("Error: Specify either --lead or --partner.")
        return None

    if not partner_id:
        print(f"Error: Lead #{lead_id} has no partner attached.")
        return None

    # 2. Resolve Quotation Template
    if template_query and str(template_query).isdigit():
        tmpl_domain = [('id', '=', int(template_query))]
    elif template_query:
        tmpl_domain = [('name', 'ilike', template_query)]
    else:
        tmpl_domain = [('name', 'ilike', 'Event-Paket')]

    templates = odoo.odoo_search_read('sale.order.template', tmpl_domain, ['id', 'name', 'note'], limit=1)
    if not templates:
        print(f"Error: Template matching '{template_query}' not found.")
        return None
    template = templates[0]
    template_id = template['id']

    # 3. Read template lines
    tmpl_lines = odoo.odoo_search_read('sale.order.template.line', [('sale_order_template_id', '=', template_id)], [
        'product_id', 'name', 'product_uom_qty', 'product_uom_id', 'display_type'
    ])

    order_lines = []
    for tl in tmpl_lines:
        line_vals = {
            'display_type': tl['display_type'],
            'name': tl['name'],
            'product_uom_qty': tl['product_uom_qty'],
        }
        if tl['product_id']:
            p_id = tl['product_id'][0]
            line_vals['product_id'] = p_id
            prod = odoo.odoo_search_read('product.product', [('id', '=', p_id)], ['list_price'])
            if prod:
                line_vals['price_unit'] = prod[0]['list_price']
        order_lines.append((0, 0, line_vals))

    # 4. Build Sale Order
    so_vals = {
        'partner_id': partner_id,
        'opportunity_id': lead_id,
        'sale_order_template_id': template_id,
        'user_id': salesperson_id,
        'team_id': team_id,
        'note': template.get('note') or "Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleinunternehmerstatus).",
        'order_line': order_lines,
    }
    if event_date:
        so_vals['commitment_date'] = f"{event_date} 10:00:00"

    so_id = odoo.odoo_execute('sale.order', 'create', [so_vals])
    so_data = odoo.odoo_search_read('sale.order', [('id', '=', so_id)], ['name', 'amount_total'])
    so_name = so_data[0]['name'] if so_data else f"SO#{so_id}"
    so_amount = so_data[0]['amount_total'] if so_data else 0.0

    print(f"==================================================")
    print(f"✅ ANGEBOT ERFOLGREICH ERSTELLT!")
    print(f"  Angebot:     {so_name} (ID: {so_id})")
    print(f"  Kunde:       {partner_name}")
    print(f"  Vorlage:     {template['name']}")
    print(f"  Gesamtbetrag: {so_amount:.2f} EUR (netto = brutto gem. §19 UStG)")
    if event_date:
        print(f"  Eventdatum:  {event_date}")
    print(f"  Odoo-Link:   http://10.1.0.112:8069/odoo/sales/orders/{so_id}")
    print(f"==================================================")
    return so_id

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="FraWo Quick-Quote Generator")
    parser.add_argument('--lead', help="CRM Lead ID (z.B. 72)")
    parser.add_argument('--partner', help="Partner Name / Suchbegriff (z.B. Gierer)")
    parser.add_argument('--template', help="Template Name oder ID (z.B. Event, Fussballdart, 7)")
    parser.add_argument('--date', help="Eventdatum im Format YYYY-MM-DD")
    args = parser.parse_args()

    create_quick_quote(
        partner_query=args.partner,
        lead_id=args.lead,
        template_query=args.template,
        event_date=args.date
    )

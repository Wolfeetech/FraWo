"""
Automated Inbound Quote & Rental Ingestion Engine for FraWo
Converts incoming web leads into draft sale.order records in Odoo automatically.
"""
import sys
from pathlib import Path

sys.path.insert(0, r"C:\Users\StudioPC\FraWo\scripts\business")
import mcp_odoo_pro_server as s

# Package mapping to product IDs and standard prices
PACKAGE_CATALOG = {
    'paket_01': {'name': 'Paket 01: Pro-Licht-Paket (Wolfmix + Moving Heads)', 'price': 140.0, 'deposit': 100.0},
    'paket_02': {'name': 'Paket 02: Club & Open-Air Sound-System (Martin Audio)', 'price': 220.0, 'deposit': 150.0},
    'paket_03': {'name': 'Paket 03: 5m Riesen-Fußballdart Modul', 'price': 180.0, 'deposit': 100.0},
    'paket_04': {'name': 'Paket 04: Compact Party PA-Set (12 Zoll Fullrange)', 'price': 90.0, 'deposit': 50.0},
    'paket_05': {'name': 'Paket 05: Ambient & Dance Licht-Set', 'price': 80.0, 'deposit': 50.0},
}

def process_new_leads():
    """Scans for unprocessed CRM leads and converts them to draft sale.order."""
    # Find leads created in last 7 days without a sale order
    leads = s.odoo_search_read('crm.lead', [
        ('type', '=', 'opportunity'),
        ('active', '=', True),
        ('order_ids', '=', False)
    ], ['id', 'name', 'contact_name', 'partner_name', 'email_from', 'phone', 'description', 'partner_id'], limit=5)
    
    print(f"Found {len(leads)} unprocessed leads for quote generation.")
    
    for lead in leads:
        lead_id = lead['id']
        name = lead.get('contact_name') or lead.get('partner_name') or lead.get('name') or 'Neuer Interessent'
        email = lead.get('email_from') or ''
        phone = lead.get('phone') or ''
        desc = (lead.get('description') or '').lower()
        
        # 1. Partner matching or creation
        partner_id = lead['partner_id'][0] if lead.get('partner_id') else None
        if not partner_id:
            if email:
                existing_p = s.odoo_search_read('res.partner', [('email', '=', email)], ['id'], limit=1)
                if existing_p:
                    partner_id = existing_p[0]['id']
            if not partner_id:
                partner_id = s.odoo_execute('res.partner', 'create', [{
                    'name': name,
                    'email': email,
                    'phone': phone,
                    'customer_rank': 1
                }])
                print(f"Created new Partner #{partner_id} for {name}")

        # 2. Package detection
        selected_pkg = 'paket_04' # default to Party PA
        for key in PACKAGE_CATALOG.keys():
            if key in desc or PACKAGE_CATALOG[key]['name'].lower() in desc:
                selected_pkg = key
                break

        pkg_info = PACKAGE_CATALOG[selected_pkg]

        # 3. Create draft sale.order
        order_vals = {
            'partner_id': partner_id,
            'opportunity_id': lead_id,
            'state': 'draft',
            'note': "Gemäß § 19 UStG wird keine Umsatzsteuer berechnet (Kleinunternehmerstatus).",
            'order_line': [
                (0, 0, {
                    'name': f"{pkg_info['name']} (Mietdauer: 24h Standard)",
                    'product_uom_qty': 1.0,
                    'price_unit': pkg_info['price'],
                }),
                (0, 0, {
                    'name': f"Kaution (wird bei unversehrter Rückgabe vollständig erstattet)",
                    'product_uom_qty': 1.0,
                    'price_unit': pkg_info['deposit'],
                })
            ]
        }
        
        order_id = s.odoo_execute('sale.order', 'create', [order_vals])
        print(f"✅ Generated Draft Sale Order #{order_id} for Lead #{lead_id} ({name}): {pkg_info['name']} ({pkg_info['price']} €)")
        
        # Post note on lead
        s.odoo_execute('crm.lead', 'message_post', [[lead_id]], {
            'body': f"🤖 [Antigravity] Automatisch Angebot #{order_id} ({pkg_info['name']}, {pkg_info['price']} €) vorbereitet.",
            'message_type': 'comment'
        })

if __name__ == '__main__':
    process_new_leads()

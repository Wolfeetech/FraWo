# IDs
COMPANY_ID = 1
WEBSITE_ID = 1

FOOTER_CSS = """
/* Footer and Branding Fixes */
footer {
    border-top: 1px solid rgba(112, 128, 144, 0.3);
}
.o_footer_copyright {
    background-color: #001f3f !important;
    color: #708090 !important;
}
"""

def apply_ui_polish():
    try:
        # 1. Add Footer CSS
        # We can add this to the website's custom CSS
        website = env['website'].browse(WEBSITE_ID)
        # website.custom_footer_template can be used in some versions, 
        # but we'll focus on the menu links first for legality.

        # 2. Add Legal Links to Footer Menu
        Menu = env['website.menu']
        root_menu = website.menu_id
        
        # Check if Impressum/Privacy are in the menu
        if not Menu.search([('url', '=', '/impressum'), ('website_id', '=', WEBSITE_ID)]):
            Menu.create({
                'name': 'Impressum',
                'url': '/impressum',
                'parent_id': root_menu.id,
                'website_id': WEBSITE_ID,
                'sequence': 90,
            })
            
        if not Menu.search([('url', '=', '/datenschutz'), ('website_id', '=', WEBSITE_ID)]):
            Menu.create({
                'name': 'Datenschutz',
                'url': '/datenschutz',
                'parent_id': root_menu.id,
                'website_id': WEBSITE_ID,
                'sequence': 91,
            })
            
        print("Footer Menu links added.")

        # 3. Finalize Contact Page contents
        # We update the contact form or just the info block
        # Usually website.contactus view
        
        # 4. Fix Company Name (ensure GbR is not truncated)
        company = env['res.company'].browse(COMPANY_ID)
        company.write({'name': 'FraWo GbR'})
        
        env.cr.commit()
    except Exception as e:
        print(f"Error: {e}")
        env.cr.rollback()

apply_ui_polish()

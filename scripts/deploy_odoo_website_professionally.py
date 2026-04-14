import xmlrpc.client
import sys

URL = "http://192.168.2.22:8069"
DB = "FraWo_Live"
USER = "admin"
PASSWORD = "OD-Wolf-2026!"

def deploy():
    print(f"Connecting to Odoo at {URL}...")
    try:
        common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common")
        uid = common.authenticate(DB, USER, PASSWORD, {})
        if not uid:
            print("Authentication failed!")
            return
        
        models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object")
        
        # 1. Update Company Information
        print("Updating Company Information (Rothkreuz 14)...")
        company_ids = models.execute_kw(DB, uid, PASSWORD, 'res.company', 'search', [[['name', '=', 'FraWo_GbR']]])
        if company_ids:
            models.execute_kw(DB, uid, PASSWORD, 'res.company', 'write', [company_ids, {
                'street': 'Rothkreuz 14',
                'zip': '88138',
                'city': 'Weissensberg',
                'mobile': '015155243164',
                'email': 'wprinz1101@gmail.com',
                'website': 'https://frawo-tech.de'
            }])
            print("Company info updated.")

        # 2. Inject Custom CSS
        # In Odoo 16+, custom CSS is often stored in 'website.custom_css' or a specialized view
        print("Deploying Professional CSS...")
        with open('Codex/website/frawo_custom_css.css', 'r') as f:
            css_content = f.read()
        
        # We look for the 'website.custom_css' or similar view to inject our styles
        # If not found, we'll try to find any CSS view linked to the website
        view_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['name', '=', 'Custom CSS']]])
        if not view_ids:
            view_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.user_custom_css']]])
            
        if view_ids:
            # We wrap the CSS in the expected XML format for Odoo views
            full_css = f"<style>{css_content}</style>"
            models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [view_ids, {'arch': full_css}])
            print("Professional CSS deployed.")

        # 3. Update Homepage Content
        print("Deploying Macher Homepage Content...")
        with open('Codex/website/frawo_homepage_blocks.html', 'r', encoding='utf-8') as f:
            homepage_html = f.read()

        # Find the homepage view (usually key='website.homepage')
        homepage_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.homepage']]])
        if homepage_ids:
            # Wrap the content in Odoo architecture XML
            # Note: We keep the main structure but replace the content inside the wrap
            arch = f'<?xml version="1.0"?>\n<t name="Homepage" t-name="website.homepage">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty">\n            {homepage_html}\n        </div>\n    </t>\n</t>'
            models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [homepage_ids, {'arch_db': arch}])
            print("Homepage content deployed.")

        # 4. Update Contact Us Page
        print("Deploying Professional Contact Form...")
        with open('Codex/website/frawo_contactus.html', 'r', encoding='utf-8') as f:
            contact_html = f.read()
        
        contact_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', 'ilike', 'contactus']]])
        if contact_ids:
            arch_contact = f'<?xml version="1.0"?>\n<t name="Contact us" t-name="website.contactus">\n    <t t-call="website.layout">\n        <div id="wrap" class="oe_structure oe_empty">\n            {contact_html}\n        </div>\n    </t>\n</t>'
            models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [contact_ids, {'arch_db': arch_contact}])
            print("Contact Us page deployed.")

        print("\nSUCCESS: All professional assets deployed via Odoo API.")

    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    deploy()

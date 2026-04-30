import xmlrpc.client
import os

# Configuration
url = 'http://172.21.0.3:8069' # Internal Odoo IP
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'Wolf2024!Frawo'

# SEO Data
meta_description = "FraWo GbR - Professionelle Veranstaltungstechnik am Bodensee. Event-Infrastruktur, Smart Home, Heimkino & Streaming. Ton, Licht, Automation für Clubs, Firmen, Privat."
og_url = "https://www.frawo-tech.de/"

def update_seo():
    print(f"Connecting to Odoo at {url}...")
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("[X] Authentication failed")
        return

    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

    # 1. Update Homepage (Page ID 7 as per latest report)
    print("Updating Homepage Meta Description...")
    page_ids = models.execute_kw(db, uid, password, 'website.page', 'search', [[('url', '=', '/')]])
    
    if page_ids:
        models.execute_kw(db, uid, password, 'website.page', 'write', [page_ids, {
            'website_meta_description': meta_description,
            'website_meta_title': "FraWo GbR | Veranstaltungstechnik & Event-Infrastruktur Bodensee",
        }])
        print(f"   [OK] Meta Description updated for Page IDs: {page_ids}")
    else:
        print("   [!] Homepage (/) not found in website.page")

    # 2. Update Website-wide OG:URL and SEO defaults if possible
    # In Odoo, some of these are computed or set in the layout.
    # We can try to update the website record itself.
    website_ids = models.execute_kw(db, uid, password, 'website', 'search', [[]])
    if website_ids:
        models.execute_kw(db, uid, password, 'website', 'write', [website_ids, {
            'social_og_image': True, # Ensure OG images are active
            # Note: OG:URL is usually computed from the base URL. 
            # We should ensure the system parameter 'web.base.url' is correct.
        }])
        print(f"   [OK] Website settings updated.")

    # 3. Fix OG:URL via System Parameters
    print("Setting web.base.url to HTTPS...")
    param_ids = models.execute_kw(db, uid, password, 'ir.config_parameter', 'search', [[('key', '=', 'web.base.url')]])
    if param_ids:
        models.execute_kw(db, uid, password, 'ir.config_parameter', 'write', [param_ids, {
            'value': 'https://www.frawo-tech.de'
        }])
        print("   [OK] web.base.url set to HTTPS.")

    print("\nSEO Boost Complete!")

if __name__ == "__main__":
    update_seo()

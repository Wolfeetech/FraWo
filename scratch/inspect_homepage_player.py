import xmlrpc.client
import json

ODOO_URL = 'http://10.1.0.112:8069'
ODOO_DB = 'FraWo_GbR'
ODOO_USER = 'wolf@frawo-tech.de'
ODOO_PASSWORD = '__ROTATED_SECRET__'

def main():
    print("[*] Connecting to Odoo at", ODOO_URL)
    common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
    uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
    if not uid:
        print("[FAIL] Auth failed")
        return
    print("[OK] Authenticated, UID:", uid)
    
    models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
    
    # 1. Search for website pages
    pages = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'website.page', 'search_read',
        [[['url', '=', '/']]],
        {'fields': ['id', 'name', 'url', 'view_id', 'website_id', 'arch_db']}
    )
    
    print("\n--- Homepage Pages ---")
    for page in pages:
        print(f"Page ID: {page['id']}, Name: {page['name']}, URL: {page['url']}, Website ID: {page['website_id']}, View ID: {page['view_id']}")
        arch = page.get('arch_db', '')
        if 'radio' in arch.lower() or 'player' in arch.lower():
            print("  -> Contains 'radio' or 'player' in arch_db!")
        else:
            print("  -> Does NOT contain 'radio' or 'player' in arch_db.")
            
    # Let's inspect views with 'radio' or 'player' in key or name
    views = models.execute_kw(
        ODOO_DB, uid, ODOO_PASSWORD,
        'ir.ui.view', 'search_read',
        [[['name', 'ilike', 'radio'], ['active', '=', True]]],
        {'fields': ['id', 'name', 'key', 'active', 'type', 'inherit_id']}
    )
    print("\n--- Active Views with 'radio' in name ---")
    for view in views:
        print(f"View ID: {view['id']}, Name: {view['name']}, Key: {view['key']}, Active: {view['active']}, Type: {view['type']}, Inherit ID: {view['inherit_id']}")

    # Let's search in page view ID 12 and 15 specifically
    for pid in [12, 15]:
        page_info = models.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'website.page', 'read',
            [pid],
            {'fields': ['arch_db', 'name']}
        )
        if page_info:
            print(f"\n--- Page {pid} Arch (Length {len(page_info[0]['arch_db'])}) ---")
            arch = page_info[0]['arch_db']
            # print first 500 chars and last 500 chars, and if there's player block
            if 'frawo-radio-player' in arch:
                idx = arch.find('frawo-radio-player')
                print(f"Found 'frawo-radio-player' at index {idx}. Context:")
                print(arch[max(0, idx-200):min(len(arch), idx+600)])
            else:
                print("No 'frawo-radio-player' in this page's arch_db.")

if __name__ == '__main__':
    main()

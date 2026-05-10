import os
import sys
import base64
import xmlrpc.client
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
IMAGE_DIR = REPO_ROOT / 'apps' / 'yourparty' / 'apps' / 'web' / 'assets' / 'images'
WEBSITE_DIR = REPO_ROOT / 'Codex' / 'website'
HOMEPAGE_HTML = WEBSITE_DIR / 'frawo_homepage_v4_OPTIMIZED.html'

# Connection
URL = os.getenv("ODOO_RPC_URL", "http://10.4.0.22:8069")
DB = os.getenv("ODOO_RPC_DB", "FraWo_GbR")
USER = os.getenv("ODOO_RPC_USER", "admin@frawo-tech.de")
PASSWORD = os.getenv("ODOO_RPC_PASSWORD", "Anker")

def upload_image(models, db, uid, filepath, name):
    print(f"Uploading {name} from {filepath}...")
    with open(filepath, "rb") as f:
        img_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Check if exists
    existing = models.execute_kw(DB, uid, PASSWORD, 'ir.attachment', 'search',
                                [[['name', '=', name], ['res_model', '=', 'ir.ui.view']]])
    if existing:
        att_id = existing[0]
        models.execute_kw(DB, uid, PASSWORD, 'ir.attachment', 'write',
                         [[att_id], {'datas': img_data}])
        print(f"  Updated existing attachment ID: {att_id}")
        return att_id
    else:
        att_id = models.execute_kw(DB, uid, PASSWORD, 'ir.attachment', 'create', [{
            'name': name,
            'type': 'binary',
            'datas': img_data,
            'res_model': 'ir.ui.view',
            'public': True,
        }])
        print(f"  Created new attachment ID: {att_id}")
        return att_id

def main():
    common = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(DB, USER, PASSWORD, {})
    if not uid:
        print("Auth failed!")
        return 1
    
    models = xmlrpc.client.ServerProxy(f"{URL}/xmlrpc/2/object", allow_none=True)
    
    # Upload images
    images = {
        '__IMG_HERO_BODENSEE__': IMAGE_DIR / 'hero-bodensee.jpg',
        '__IMG_TEAM_OR_REFERENCE__': IMAGE_DIR / 'about-console.jpg',
        '__IMG_REFERENCE_EVENT__': IMAGE_DIR / 'reference-event.jpg'
    }
    
    image_ids = {}
    for placeholder, filepath in images.items():
        if filepath.exists():
            att_id = upload_image(models, DB, uid, filepath, filepath.name)
            image_ids[placeholder] = att_id
        else:
            print(f"Warning: {filepath} not found!")

    # Read Homepage HTML
    print("\nUpdating Homepage HTML...")
    with open(HOMEPAGE_HTML, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace placeholders
    # In deploy_website_complete.py it replaces them with /web/image/website.placeholder_image if left as __IMG...
    # We will replace them directly in the Odoo View.
    # Actually, we should just update the HTML file in the repo so deploy script uses the real URLs!
    for placeholder, att_id in image_ids.items():
        url = f"/web/image/{att_id}/{images[placeholder].name}"
        content = content.replace(placeholder, url)
        # Also replace the placeholder image paths if the deploy script already replaced them in previous runs
        # No, the deploy script replaces them ON THE FLY without modifying the source file! 
        # So we must modify the deploy script or the HTML file. Let's just modify the deploy script to use these new IDs, 
        # OR just change the HTML file to have the correct URLs and remove the placeholder text!
        print(f"Replaced {placeholder} with {url}")
    
    with open(HOMEPAGE_HTML, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("\nDone! Now run deploy_website_complete.py to publish the changes.")

if __name__ == "__main__":
    sys.exit(main())

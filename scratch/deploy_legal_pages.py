import xmlrpc.client
import os
import re
from pathlib import Path
from dotenv import load_dotenv

env_path = Path.home() / '.ai-tools-shared' / '.env'
load_dotenv(env_path)

ODOO_URL = os.getenv('ODOO_URL', 'http://10.1.0.112:8069')
ODOO_DB = 'FraWo_GbR'
ODOO_USER = os.getenv('ODOO_USER', 'wolf@frawo-tech.de')
ODOO_PASSWORD = os.getenv('ODOO_PASSWORD', '__ROTATED_SECRET__')

common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

def read_file(name):
    with open(f"C:\\Users\\StudioPC\\OneDrive\\Dokumente\\GitHub\\FraWo\\scratch\\legal_{name}.html", "r", encoding="utf-8") as f:
        return f.read()

pages = {
    'impressum': read_file('impressum'),
    'datenschutz': read_file('datenschutz'),
    'agb': read_file('agb')
}

v2_styles = """
  <style>
    :root {
      --fw-bg: #030303;
      --fw-surface: rgba(20, 20, 20, 0.6);
      --fw-tech-blue: #3b82f6;
      --fw-text: #e2e8f0;
      --fw-text-2: #94a3b8;
    }
    body {
      background-color: var(--fw-bg) !important;
    }
    .legal-page {
      background: var(--fw-bg);
      color: var(--fw-text);
      padding: 80px 0;
      min-height: 100vh;
    }
    .legal-card {
      background: var(--fw-surface);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1px solid rgba(255,255,255,0.05);
      border-radius: 1.5rem;
      padding: 3rem;
      box-shadow: 0 25px 50px -12px rgba(0,0,0,0.5);
    }
    .legal-card h1 {
      font-weight: 800;
      color: #ffffff;
      border-bottom: 2px solid rgba(59, 130, 246, 0.3);
      padding-bottom: 1rem;
      margin-bottom: 2rem;
      font-family: 'Inter', sans-serif;
    }
    .legal-card h2, .legal-card .h4 {
      color: var(--fw-tech-blue);
      font-weight: 700;
      margin-top: 2rem;
      font-family: 'Inter', sans-serif;
    }
    .legal-card h3, .legal-card .h5 {
      color: #cbd5e1;
      font-weight: 600;
      font-family: 'Inter', sans-serif;
    }
    .legal-card p, .legal-card li {
      color: var(--fw-text-2) !important;
      line-height: 1.7;
      font-size: 1.05rem;
      font-family: 'Inter', sans-serif;
    }
    .legal-card strong {
      color: #ffffff;
    }
    .legal-card a {
      color: var(--fw-tech-blue);
      text-decoration: none;
    }
    .legal-card a:hover {
      text-decoration: underline;
    }
    .legal-card .text-muted {
      color: #64748b !important;
    }
    .legal-card hr {
      border-color: rgba(255,255,255,0.1);
    }
  </style>
"""

for url_key, html in pages.items():
    # Extract inner content between the innermost wrapper.
    # We look for <h1 and capture up to the end before the closing divs
    h1_index = html.find('<h1')
    if h1_index != -1:
        # Find the last </div> we want to exclude.
        # Since the structure is usually:
        # <h1... > ... </p> ... </div></div></div>
        # We can just use regex to capture from <h1 to the end, then strip trailing </div>
        content = html[h1_index:]
        # Remove trailing </div> and </t>
        content = re.sub(r'</div\s*>', '', content)
        content = re.sub(r'</t\s*>', '', content)
        # Re-add just the necessary closing tags for the content if it had inner divs, 
        # but usually legal pages just have h1, h2, p, ul.
        # Let's do something safer: just strip all known Odoo wrappers before <h1
        
        # Actually, let's parse with basic regex.
        # Everything from <h1 to the end, except closing tags of the outer wrappers.
        # We know outer wrappers are: 
        # <t...><div wrap><div container><div row><div col>
        
        content = html[h1_index:]
        content = re.sub(r'</div>\s*</div>\s*</div>\s*</div>\s*</div>\s*</t>\s*</t>', '', content)
        content = re.sub(r'</div>\s*</div>\s*</div>\s*</div>\s*</t>', '', content)
        content = re.sub(r'</div>\s*</div>\s*</div>\s*</div>', '', content)
        content = re.sub(r'</div>\s*</div>\s*</div>', '', content)
        content = re.sub(r'</div>\s*</div>', '', content)
        content = re.sub(r'</div>\s*$', '', content)
    else:
        content = html

    # Clean up empty lines
    content = '\n'.join([line for line in content.split('\n') if line.strip()])

    new_arch = f"""<t t-name="website.{url_key}">
  <t t-call="website.layout">
    <div id="wrap" class="oe_structure oe_empty">
      {v2_styles}
      <div class="legal-page">
        <div class="container">
          <div class="row">
            <div class="col-lg-10 offset-lg-1">
              <div class="legal-card">
                {content}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </t>
</t>"""
    
    # Push to Odoo
    search_url = f"/{url_key}"
    page_records = models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'website.page', 'search_read', [[('url', '=', search_url)]], {'fields': ['view_id']})
    if page_records:
        view_id = page_records[0]['view_id'][0]
        models.execute_kw(ODOO_DB, uid, ODOO_PASSWORD, 'ir.ui.view', 'write', [view_id, {'arch': new_arch}])
        print(f"SUCCESS: Deployed new V2 {url_key.capitalize()} Page")
    else:
        print(f"Error: {search_url} page not found in Odoo")

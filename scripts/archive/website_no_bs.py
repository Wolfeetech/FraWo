# -*- coding: utf-8 -*-
import xmlrpc.client
import base64

# Config
url = 'http://10.1.0.22:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Read Logo (1.png)
with open('/tmp/logo_1.png', 'rb') as f:
    logo_1 = base64.b64encode(f.read()).decode('utf-8')

# Update Website Logo
models.execute_kw(db, uid, password, 'website', 'write', [[1], {
    'logo': logo_1,
    'name': 'FraWo GbR',
}])

# Homepage (No-BS Version)
home_arch = """<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">
      <style>
        body { background: #0d1117; color: #fff; font-family: sans-serif; }
        .hero { padding: 100px 0; }
        h1 { font-size: 5rem; font-weight: 900; }
        p { font-size: 1.5rem; color: #94a3b8; }
        .btn { background: #a855f7; color: #fff; padding: 15px 30px; border-radius: 5px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 20px; }
        .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; padding: 50px 0; }
        .card { background: #161b22; padding: 20px; border-radius: 10px; border: 1px solid #30363d; }
      </style>
      <section class="hero container">
        <h1>Technik, die abliefert.</h1>
        <p>Planung. Expertise. Manpower.<br/>Wir machen dein Projekt sicher.</p>
        <a href="/contactus" class="btn">Projekt anfragen</a>
      </section>
      <section class="container">
        <div class="grid">
          <div class="card"><h3>Smart Media</h3><p>Medientechnik. Sauber integriert.</p></div>
          <div class="card"><h3>Event Engineering</h3><p>Planung und Umsetzung.</p></div>
          <div class="card"><h3>Manpower</h3><p>Wir packen an.</p></div>
        </div>
      </section>
    </div>
  </t>
</t>"""

# Push content
models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3644], {'arch_db': home_arch}])

# SEO on Page
page_ids = models.execute_kw(db, uid, password, 'website.page', 'search', [[['view_id', '=', 3644]]])
if page_ids:
    models.execute_kw(db, uid, password, 'website.page', 'write', [page_ids, {
        'website_meta_title': 'FraWo | Technik. Planung. Manpower.',
        'website_meta_description': 'Wir bringen deine Technik zum Laufen. Expertise, Geschick und Manpower.',
    }])

print("Done.")

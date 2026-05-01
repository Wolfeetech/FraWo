# -*- coding: utf-8 -*-
import xmlrpc.client
import base64

url = "http://10.1.0.22:8069"
db = "FraWo_GbR"
username = "wolf@frawo-tech.de"
password = "Wolf2024!Frawo"

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 1. Premium CSS v3.5.2
premium_css = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
:root { 
  --fw-bg: #0a0a0a; 
  --fw-text: #f0f0f0; 
  --fw-text-dim: #999999;
  --fw-border: rgba(255, 255, 255, 0.08); 
  --fw-uv: #a855f7;
}
/* Visibility Fix */
html, body, #wrapwrap { 
  background-color: var(--fw-bg) !important; 
  color: var(--fw-text) !important; 
  opacity: 1 !important; 
  visibility: visible !important; 
  display: block !important; 
}
body { font-family: 'Inter', sans-serif !important; margin: 0; }

/* Premium Header */
header#top { 
  background: rgba(10,10,10,0.85) !important; 
  backdrop-filter: blur(20px) saturate(180%); 
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-bottom: 1px solid var(--fw-border) !important; 
}
.navbar-brand img { height: 18px !important; filter: brightness(0) invert(1); }

/* Animation */
.fw-fade-in { animation: fadeIn 0.8s ease-out forwards; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

/* Fix Odoo ghost blocks */
.oe_structure { display: none !important; }
main { background: var(--fw-bg) !important; }
</style>"""

# 2. Homepage Architecture (Clean)
homepage_arch = """
<t t-name="website.homepage_v3_5">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
            <section class="fw-hero fw-fade-in" style="padding: 140px 0 80px; background: #0a0a0a;">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-lg-6">
                            <div style="font-size: 0.7rem; letter-spacing: 0.3em; text-transform: uppercase; color: #a855f7; margin-bottom: 2rem; font-weight: 600;">FraWo GbR</div>
                            <h1 style="font-size: clamp(2.5rem, 6vw, 4.5rem); font-weight: 700; line-height: 1.05; color: #f0f0f0; margin-bottom: 1.5rem; letter-spacing: -0.04em;">Veranstaltungstechnik<br/>&amp; Event-Infrastruktur</h1>
                            <p style="color: #999; font-size: 1.1rem; line-height: 1.7; max-width: 40rem; margin-bottom: 2.5rem;">Ton, Licht, Automation. Vom Bodensee. Für Events, Clubs, Firmen, Privathaushalte.</p>
                            <div class="d-flex gap-3">
                                <a href="/contactus" class="btn" style="background: #f0f0f0; color: #0a0a0a; border-radius: 0; padding: 14px 28px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Kontakt</a>
                                <a href="/b2b" class="btn" style="border: 1px solid rgba(255,255,255,0.1); color: #f0f0f0; border-radius: 0; padding: 14px 28px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">Services</a>
                            </div>
                        </div>
                        <div class="col-lg-6">
                            <div style="border: 1px solid rgba(255,255,255,0.1); background: #111;">
                                <img src="/web/image/hero-bodensee.jpg" class="img-fluid" style="width: 100%; height: auto; display: block; opacity: 0.8;"/>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>
"""

print("Applying Premium CSS...")
models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': premium_css}])

print("Cleaning & Updating Homepage View...")
# Find the homepage view
page = models.execute_kw(db, uid, password, 'website.page', 'search_read', [[['url', '=', '/']]], {'fields': ['view_id']})
if page:
    view_id = page[0]['view_id'][0]
    models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[view_id], {'arch_db': homepage_arch}])
    print(f"Updated view {view_id}")

print("Fixing Base URL...")
param_ids = models.execute_kw(db, uid, password, 'ir.config_parameter', 'search', [[['key', '=', 'web.base.url']]])
if param_ids: models.execute_kw(db, uid, password, 'ir.config_parameter', 'write', [param_ids, {'value': 'https://www.frawo-tech.de'}])

print("SUCCESS")

# -*- coding: utf-8 -*-
import xmlrpc.client

# Configuration (based on frawo_update_b2c_fixed.py)
url = 'http://10.1.0.22:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# 1. Technical Branding: Set Website Logo (Fixing 500 error)
# We use Attachment ID 1824 (FraWo_Logo1x1.jpeg) which was found by the audit
attachment = models.execute_kw(db, uid, password, 'ir.attachment', 'read', [[1824], ['datas']])
if attachment:
    logo_data = attachment[0]['datas']
    models.execute_kw(db, uid, password, 'website', 'write', [[1], {
        'logo': logo_data,
        'name': 'FraWo GbR',
        'social_twitter': '', # Clean up social noise for WOW effect
        'social_facebook': '',
        'social_github': '',
        'social_linkedin': '',
        'social_youtube': '',
        'social_instagram': ''
    }])
    print("Logo and Website Metadata updated (WOW Fix).")

# 2. SEO Content Injection: Staccato Headings (Manpower/Expertise soul)
# We update the homepage view (ID 3644)
home_arch = """<t name="Home" t-name="website.homepage">
  <t t-call="website.layout">
    <t t-set="pageName" t-value="'homepage'"/>
    <div id="wrap" class="oe_structure">
      <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&amp;display=swap');
        :root{
          --fw-bg:#0d1117;
          --fw-acc:#a855f7;
          --fw-acc-rgb:168,85,247;
          --fw-forest:#064e3b;
        }
        body { font-family: 'Poppins', sans-serif !important; background: #0d1117; color: #fff; }
        .fw-hero{ padding: 110px 0 90px; background: linear-gradient(135deg, #0d1117 0%, #111827 55%, #0d1117 100%); position: relative; overflow: hidden; }
        .fw-eyebrow{ font-size:.78rem; font-weight:700; letter-spacing:.25em; text-transform:uppercase; color:#a855f7; }
        .fw-h1{ font-size:clamp(2.5rem,6vw,4.5rem); font-weight:900; line-height:1.0; background:linear-gradient(135deg,#ffffff 0%,#d8b4fe 100%); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
        .fw-lead{ color:#94a3b8; font-size:1.1rem; line-height:1.7; max-width:38rem; }
        .fw-btn-primary{ background:linear-gradient(135deg,#7c3aed,#a855f7) !important; border:none !important; border-radius:12px !important; padding:14px 32px !important; font-weight:700 !important; color:#fff !important; }
        .fw-card{ height:100%; border-radius:1.4rem; background:rgba(22,27,34,.85); border:1px solid rgba(255,255,255,.07); padding:2.2rem; backdrop-filter:blur(12px); transition:.3s ease; }
        .fw-card:hover{ border-color:rgba(168,85,247,.4); transform:translateY(-6px); }
        .fw-num{ font-size:2rem; font-weight:900; color:#a855f7; margin-bottom:.8rem; }
        .fw-band{ background:linear-gradient(135deg,#052e16 0%,#064e3b 100%); border-radius:1.8rem; padding:3rem; border:1px solid rgba(167,243,208,.1); }
      </style>

      <section class="fw-hero">
        <div class="container position-relative" style="z-index:1;">
          <div class="row align-items-center g-5">
            <div class="col-lg-6">
              <div class="fw-eyebrow mb-3">Expertise &amp; Geschick</div>
              <h1 class="fw-h1 mb-4">Eventtechnik.<br/>Planung. Umsetzung.</h1>
              <p class="fw-lead mb-5">
                FraWo liefert pr&#xe4;zises Engineering und technische Manpower f&#xfc;r anspruchsvolle Projekte.
                Vom High-End Home Cinema bis zur komplexen technischen Veranstaltungsbetreuung.
              </p>
              <div class="d-flex flex-wrap gap-3">
                <a class="fw-btn-primary btn btn-lg" href="/contactus">Projekt anfragen</a>
                <a class="btn btn-outline-light btn-lg" style="border-radius:12px; font-weight:600;" href="#services">Leistungen</a>
              </div>
            </div>
            <div class="col-lg-6">
              <div style="border-radius:1.5rem; overflow:hidden; box-shadow:0 30px 60px rgba(0,0,0,.5); border:1px solid rgba(168,85,247,.2);">
                <img src="/web/image/1803" style="width:100%; height:auto; display:block;" alt="FraWo Event Engineering"/>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="services" class="fw-section" style="padding: 100px 0; background:#0d1117;">
        <div class="container">
          <div class="row g-4">
            <div class="col-md-4">
              <div class="fw-card">
                <div class="fw-num">01</div>
                <h3 style="color:#fff;">Smart Media &amp; Integration</h3>
                <p>Ma&#xdf;geschneiderte Medientechnik und vernetzte Systeme f&#xfc;r Home und Business.</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="fw-card">
                <div class="fw-num">02</div>
                <h3 style="color:#fff;">Event Engineering</h3>
                <p>Pr&#xe4;zise Planung und fachgerechte Umsetzung Ihrer Veranstaltungstechnik.</p>
              </div>
            </div>
            <div class="col-md-4">
              <div class="fw-card">
                <div class="fw-num">03</div>
                <h3 style="color:#fff;">Technische Manpower</h3>
                <p>Expertise und Geschick vor Ort. Wir bringen die n&#xf6;tige Fachkraft in Ihr Projekt.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section class="fw-section" style="padding: 60px 0; background:#0d1117;">
        <div class="container">
          <div class="fw-band">
            <div class="row align-items-center">
              <div class="col-lg-7">
                <h2 style="color:#fff; font-weight:800;">Expertise und Geschick f&#xfc;r Ihren Erfolg.</h2>
                <p style="color:#a7f3d0; font-size:1.1rem;">Wir bringen die erforderliche Manpower und technisches Know-how auf Ihre Veranstaltung.</p>
              </div>
              <div class="col-lg-5 text-lg-end">
                <a class="btn btn-light btn-lg" style="border-radius:12px; font-weight:700; color:#064e3b;" href="/contactus">Jetzt anfragen</a>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </t>
</t>"""

# Update the view
models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3644], {'arch_db': home_arch}])
print("Homepage Content updated with Staccato Branding.")

# 3. SEO Optimization
# Set Page Title and Meta Description for Homepage
# We need to find the ir.ui.view for the page title or use website.page
page_id = models.execute_kw(db, uid, password, 'website.page', 'search', [[['view_id', '=', 3644]]])
if page_id:
    models.execute_kw(db, uid, password, 'website.page', 'write', [page_id, {
        'website_meta_title': 'FraWo GbR | Eventtechnik & Smart Media Solutions',
        'website_meta_description': 'Expertise, Geschick und technische Manpower für Ihre Veranstaltung. FraWo GbR liefert präzise Planung und Umsetzung in den Bereichen Event-Engineering und Smart Media Integration.',
        'website_meta_keywords': 'Eventtechnik, Smart Media, Manpower, Planung, Umsetzung, Medientechnik, FraWo'
    }])
    print("SEO Meta-Data updated.")

print("Website WOW Polish Complete!")

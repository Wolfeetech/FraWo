import xmlrpc.client
import sys

# Odoo Connection Parameters
URL = "http://10.1.0.22:8069"
DB = "FraWo_Live"
USER = "admin"
PASSWORD = "OD-Wolf-2026!"

# INLINED ASSETS
CSS_CONTENT = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

:root {
  --frawo-bg: #090b0a;
  --frawo-accent: #b0ff00;
  --frawo-text: #f0f4f2;
  --frawo-muted: #8a948e;
  --frawo-card: rgba(255, 255, 255, 0.03);
  --frawo-border: rgba(255, 255, 255, 0.08);
}

body {
    background-color: var(--frawo-bg) !important;
    color: var(--frawo-text) !important;
    font-family: 'Inter', sans-serif !important;
}

.frawo-display {
    font-family: 'Outfit', sans-serif;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1.05;
    color: var(--frawo-text);
}

.frawo-section {
    padding: 120px 0;
}

.frawo-container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 40px;
}

.frawo-btn-primary {
    display: inline-block;
    background: var(--frawo-accent);
    color: #000 !important;
    padding: 20px 48px;
    font-weight: 600;
    text-decoration: none !important;
    font-size: 1.1rem;
    border-radius: 4px;
    transition: transform 0.2s ease;
}

.frawo-btn-primary:hover {
    transform: translateY(-2px);
    background: #c4ff33;
}

/* Add more CSS if needed */
"""

HOMEPAGE_HTML = """
<div class="frawo-homepage">
  <section class="frawo-hero frawo-section">
    <div class="frawo-container">
      <p class="frawo-label" style="color:#b0ff00; font-weight:600; letter-spacing:0.1em; margin-bottom:1.5rem;">FRAWO GBR</p>
      <h1 class="frawo-display" style="font-size:clamp(3.5rem, 8vw, 6.5rem); margin-bottom:2rem;">Planung, Betrieb,<br/>digitale Begleitung.</h1>
      <p class="frawo-copy" style="font-size:1.4rem; max-width:700px; color:rgba(255,255,255,0.7); margin-bottom:3.5rem; line-height:1.6;">
        Wir sorgen dafuer, dass Veranstaltungstechnik nicht zum Hindernis wird. 
        Vom sauberen Signalweg bis zur digitalen Besucherführung.
      </p>
      <a href="/contactus" class="frawo-btn-primary">Projekt anreissen</a>
    </div>
  </section>
  
  <section class="frawo-section" style="background:rgba(255,255,255,0.02);">
    <div class="frawo-container">
        <h2 class="frawo-display" style="font-size:3rem; margin-bottom:4rem;">Macher statt Blabla.</h2>
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap:40px;">
            <div style="padding:40px; border:1px solid rgba(255,255,255,0.1);">
                <h3 style="font-family:'Outfit'; font-size:1.8rem; margin-bottom:1rem;">Event-Technik</h3>
                <p style="color:rgba(255,255,255,0.6); line-height:1.6;">Ton, Licht, Video – wir planen Gewerke so, dass sie am Abend reibungsfrei ineinandergreifen.</p>
            </div>
            <div style="padding:40px; border:1px solid rgba(255,255,255,0.1);">
                <h3 style="font-family:'Outfit'; font-size:1.8rem; margin-bottom:1rem;">Netzwerk & IT</h3>
                <p style="color:rgba(255,255,255,0.6); line-height:1.6;">Stabile Infrastruktur vor Ort. Damit Produktion, Kasse und Publikum immer verbunden bleiben.</p>
            </div>
            <div style="padding:40px; border:1px solid rgba(255,255,255,0.1);">
                <h3 style="font-family:'Outfit'; font-size:1.8rem; margin-bottom:1rem;">Begleitung</h3>
                <p style="color:rgba(255,255,255,0.6); line-height:1.6;">Wir begleiten den gesamten Ablauf. Wenn es eng wird, sorgen wir fuer die technische Ruhe.</p>
            </div>
        </div>
    </div>
  </section>
</div>
"""

CONTACT_HTML = """
<div class="frawo-contact-page">
    <section class="frawo-section">
        <div class="frawo-container">
            <h1 class="frawo-display" style="font-size:4rem; margin-bottom:2rem;">Sprechen wir drueber.</h1>
            <p style="font-size:1.2rem; color:rgba(255,255,255,0.7); margin-bottom:4rem;">Einfach Mail schreiben oder kurz anrufen. Den Rest klaeren wir im Gespraech.</p>
            
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:60px;">
                <div>
                     <a href="mailto:info@frawo-tech.de" style="font-size:2rem; color:#b0ff00; text-decoration:none; display:block; margin-bottom:1rem;">info@frawo-tech.de</a>
                     <a href="tel:+4915155243164" style="font-size:1.5rem; color:white; text-decoration:none; display:block;">+49 151 55243164</a>
                </div>
                <div style="padding:40px; background:rgba(255,255,255,0.05);">
                    <h3 style="margin-bottom:1rem;">Impressum & Standort</h3>
                    <p style="color:rgba(255,255,255,0.5);">FraWo GbR<br/>Rothkreuz 14<br/>88138 Weissensberg</p>
                </div>
            </div>
        </div>
    </section>
</div>
"""

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
        print("Updating Company Information...")
        company_ids = models.execute_kw(DB, uid, PASSWORD, 'res.company', 'search', [[['name', 'ilike', 'FraWo']]])
        if company_ids:
            models.execute_kw(DB, uid, PASSWORD, 'res.company', 'write', [company_ids, {
                'name': 'FraWo GbR',
                'street': 'Rothkreuz 14',
                'zip': '88138',
                'city': 'Weissensberg',
                'mobile': '015155243164',
                'email': 'info@frawo-tech.de',
                'website': 'https://frawo-tech.de'
            }])

        # 2. Inject Custom CSS
        print("Deploying Professional CSS...")
        view_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.user_custom_css']]])
        if view_ids:
            full_css = f"<style>{CSS_CONTENT}</style>"
            models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [view_ids, {'arch': full_css}])

        # 3. Update Homepage Content
        print("Deploying Macher Homepage...")
        homepage_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', '=', 'website.homepage']]])
        if homepage_ids:
            arch = f'<?xml version="1.0"?>\\n<t name="Homepage" t-name="website.homepage">\\n    <t t-call="website.layout">\\n        <div id="wrap" class="oe_structure oe_empty">\\n            {HOMEPAGE_HTML}\\n        </div>\\n    </t>\\n</t>'
            models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [homepage_ids, {'arch_db': arch}])

        # 4. Update Contact Page
        print("Deploying Contact Page...")
        contact_ids = models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'search', [[['key', 'ilike', 'contactus']]])
        if contact_ids:
            arch_contact = f'<?xml version="1.0"?>\\n<t name="Contact us" t-name="website.contactus">\\n    <t t-call="website.layout">\\n        <div id="wrap" class="oe_structure oe_empty">\\n            {CONTACT_HTML}\\n        </div>\\n    </t>\\n</t>'
            models.execute_kw(DB, uid, PASSWORD, 'ir.ui.view', 'write', [contact_ids, {'arch_db': arch_contact}])

        print("\nSUCCESS: Professional assets deployed.")

    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    deploy()

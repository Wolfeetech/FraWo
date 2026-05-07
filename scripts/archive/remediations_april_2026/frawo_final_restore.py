# -*- coding: utf-8 -*-
import sys
import xmlrpc.client
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(SCRIPT_ROOT))

from odoo_env import resolve_connection

settings = resolve_connection("http://172.21.0.3:8069", "FraWo_GbR", "wolf@frawo-tech.de")
url = settings.url
db = settings.db
username = settings.user
password = settings.secret

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# --- CONFIGURATION (IHK-Compliant & B2B Focus) ---
# Hero Background ID: 1793 (Stage)

# Homepage (3644)
arch_homepage = """
<data name="Homepage" inherit_id="website.homepage">
    <xpath expr="//div[@id='wrap']" position="replace">
        <div id="wrap" class="oe_structure oe_empty">
            <!-- HERO SECTION (Stage Background) -->
            <section class="s_cover o_colored_level o_full_screen_height" data-snippet="s_cover" data-name="Cover" style="background-image: url('/web/image/1793'); background-position: 50% 50%;" data-scroll-background-fixed="true">
                <div class="o_we_bg_filter bg-black-50"/>
                <div class="container s_allow_columns">
                    <div class="row">
                        <div class="col-lg-12 text-center o_colored_level">
                            <h1 style="font-weight: 800; font-size: 4rem; color: #fff; text-shadow: 2px 2px 10px rgba(0,0,0,0.8);">
                                Audiovisuelle Exzellenz &#x26; technischer Service
                            </h1>
                            <p class="lead" style="font-size: 1.5rem; color: #e2e8f0; max-width: 800px; margin: 2rem auto;">
                                Fachpersonal f&#xfc;r Veranstaltungstechnik und medientechnische Installationen.
                                Pr&#xe4;zision f&#xfc;r B2B-Projekte und High-End Privatkunden.
                            </p>
                            <div class="mt-4">
                                <a href="/contactus" class="btn btn-primary btn-lg px-5 py-3" style="background-color: #a855f7; border: none; font-weight: 600;">Projekt anfragen</a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SERVICE PILLARS (Hybrid) -->
            <section class="s_features o_colored_level py-5" style="background-color: #0d1117;">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-6 text-white p-4 o_colored_level">
                            <h2 style="color: #a855f7;">B2B: Event &#x26; Personal</h2>
                            <p class="mt-3">Unterst&#xfc;tzung f&#xfc;r Veranstaltungsdienstleister. Fachpersonal f&#xfc;r Licht, Ton, Video sowie technische Projektrealisierung und Sonderbau.</p>
                        </div>
                        <div class="col-lg-6 text-white p-4 o_colored_level" style="border-left: 1px solid #30363d;">
                            <h2 style="color: #a855f7;">B2C: High-End Home</h2>
                            <p class="mt-3">Private R&#xe4;ume neu definiert. Planung und Realisierung von Heimkino-Systemen, audiophiler HiFi-Technik und Smart Living Integration.</p>
                        </div>
                    </div>
                </div>
            </section>

            <!-- THE DUO -->
            <section class="s_text_image o_colored_level py-5" style="background-color: #0d1117; border-top: 1px solid #30363d;">
                <div class="container">
                    <div class="row align-items-center">
                        <div class="col-lg-6 text-white o_colored_level">
                            <h3>Kompetenz im Doppelpack</h3>
                            <p class="lead mt-3">Wir sind zwei motivierte Fachkr&#xe4;fte mit langj&#xe4;hriger Erfahrung in der Veranstaltungstechnik und Bau-Montage. Inhabergef&#xfc;hrt, IHK-registriert und bereit f&#xfc;r Ihren Auftrag.</p>
                            <ul class="list-unstyled mt-4">
                                <li><i class="fa fa-check text-success me-2"/> Veranstaltungstechnik Specialists</li>
                                <li><i class="fa fa-check text-success me-2"/> Montage technischer Sonderbauten</li>
                                <li><i class="fa fa-check text-success me-2"/> Pr&#xe4;zise Projektdurchf&#xfc;hrung</li>
                            </ul>
                        </div>
                        <div class="col-lg-6 o_colored_level">
                            <img src="/web/image/1795" class="img-fluid rounded shadow" alt="Team Work"/>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </xpath>
</data>
"""

# Contact Page (3637)
arch_contact = """
<data name="Contact Us" inherit_id="website.contactus">
    <xpath expr="//div[@id='wrap']" position="replace">
        <div id="wrap" class="oe_structure oe_empty" style="background-color: #0d1117; color: #fff;">
            <section class="s_title py-5">
                <div class="container">
                    <h1 class="text-center" style="font-weight: 800;">Lassen Sie uns starten.</h1>
                    <p class="text-center lead">Egal ob B2B-Personalanfrage oder B2C-High-End-Projekt.</p>
                </div>
            </section>
            <div class="container pb-5">
                <div class="row">
                    <div class="col-lg-8 offset-lg-2">
                        <div class="p-4 rounded shadow" style="background-color: #161b22; border: 1px solid #30363d;">
                             <p>Bitte kontaktieren Sie uns direkt unter <strong>info@frawo-tech.de</strong> oder nutzen Sie das Portal f&#xfc;r bestehende Projekte.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </xpath>
</data>
"""

# Footer (4405)
arch_footer = """
<data name="Footer Custom" inherit_id="website.footer_custom">
    <xpath expr="//div[@id='footer']" position="replace">
        <div id="footer" class="oe_structure oe_empty" style="background-color: #0d1117; color: #94a3b8; border-top: 1px solid #30363d; padding: 3rem 0;">
            <div class="container text-center">
                <p>FraWo &#x2014; Audiovisuelle Exzellenz &#x26; technischer Service</p>
                <p>Wei&#xdf;ensberg | IHK-registriert</p>
                <div class="mt-4">
                    <a href="/" class="mx-2 text-decoration-none" style="color: #94a3b8;">Home</a>
                    <a href="/contactus" class="mx-2 text-decoration-none" style="color: #94a3b8;">Kontakt</a>
                </div>
                <p class="mt-4" style="font-size: 0.8rem;">&#xa9; 2026 FraWo GbR. Alle Rechte vorbehalten.</p>
            </div>
        </div>
    </xpath>
</data>
"""

# Apply Updates
print("Updating Homepage (3644)...")
models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3644], {'arch_db': arch_homepage}])

print("Updating Contact Page (3637)...")
models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3637], {'arch_db': arch_contact}])

print("Updating Footer (4405)...")
models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[4405], {'arch_db': arch_footer}])

# Global CSS for Header/Footer Fix
css_head = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800;900&display=swap');
  body, #wrap { font-family: 'Poppins', sans-serif !important; }
  .o_header_standard, .o_header_affixed, #top, footer { background-color: #0d1117 !important; border-color: #30363d !important; }
  .navbar-light .navbar-nav .nav-link, .navbar-light .navbar-brand { color: #fff !important; }
  .navbar-light .navbar-nav .nav-link:hover { color: #a855f7 !important; }
</style>
"""
print("Updating Global CSS...")
models.execute_kw(db, uid, password, 'website', 'write', [[1], {'custom_code_head': css_head}])

print("Done! All views updated with IHK-compliant B2B/B2C hybrid content.")

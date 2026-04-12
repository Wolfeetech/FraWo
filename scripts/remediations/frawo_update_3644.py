# -*- coding: utf-8 -*-
import xmlrpc.client

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = 'OD-Wolf-2026!'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# IHK-Compliant & B2B/B2C Balanced Homepage
arch_homepage = """
<data name="Homepage" inherit_id="website.homepage">
    <xpath expr="//div[@id='wrap']" position="replace">
        <div id="wrap" class="oe_structure oe_empty">
            <!-- HERO SECTION (Stage Background 1793) -->
            <section class="s_cover o_colored_level o_full_screen_height" data-snippet="s_cover" data-name="Cover" style="background-image: url('/web/image/1793'); background-position: 50% 50%;">
                <div class="o_we_bg_filter bg-black-50"/>
                <div class="container s_allow_columns">
                    <div class="row">
                        <div class="col-lg-12 text-center o_colored_level">
                            <h1 style="font-weight: 800; font-size: 4rem; color: #fff; text-shadow: 2px 2px 10px rgba(0,0,0,0.8);">
                                Audiovisuelle Exzellenz &#x26; technischer Service
                            </h1>
                            <p class="lead" style="font-size: 1.5rem; color: #e2e8f0; max-width: 900px; margin: 2rem auto;">
                                Ihr Team f&#xfc;r Veranstaltungstechnik, medientechnische Installationen und Montage. 
                                Professionelle Dienstleistungen f&#xfc;r IHK-zertifizierte Projekte.
                            </p>
                            <div class="mt-4">
                                <a href="/contactus" class="btn btn-primary btn-lg px-5 py-3" style="background-color: #a855f7; border: none; font-weight: 600;">Projekt anfragen</a>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <!-- SERVICE PILLARS -->
            <section class="s_features o_colored_level py-5" style="background-color: #0d1117;">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-6 text-white p-4 o_colored_level">
                            <h2 style="color: #a855f7;">B2B: Event &#x26; Personal</h2>
                            <p class="mt-3">Fachpersonal f&#xfc;r Veranstaltungsdienstleister. Medientechnik, Systemintegration und technischer Setbau.</p>
                        </div>
                        <div class="col-lg-6 text-white p-4 o_colored_level" style="border-left: 1px solid #30363d;">
                            <h2 style="color: #a855f7;">B2C: High-End Home</h2>
                            <p class="mt-3">Pr&#xe4;zision f&#xfc;r den privaten Raum. Heimkino, audiophile HiFi-Systeme und Smart Living Konzepte.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </xpath>
</data>
"""

models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [[3644], {'arch_db': arch_homepage}])
print("Homepage updated.")

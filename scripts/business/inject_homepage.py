import base64

# IDs
WEBSITE_ID = 1

HOMEPAGE_XML = """
<t name="Homepage" t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure oe_empty">
            <section class="s_banner o_colored_level" data-snippet="s_banner" data-name="Banner" style="background-image: url('/tmp/frawo_hero.png'); background-size: cover; background-position: center; min-height: 500px;">
                <div class="container">
                    <div class="row s_nb_column_fixed">
                        <div class="col-lg-12 jumbotron o_cc o_cc1 o_colored_level" style="background-color: rgba(0, 31, 63, 0.7); color: white; padding: 40px; border-radius: 10px;">
                            <h1 style="font-size: 3.5rem; font-weight: bold;">FraWo GbR – Souveräne IT für Visionäre</h1>
                            <p class="lead" style="font-size: 1.5rem;">Wir schaffen das digitale Fundament für Ihr Business und Ihr persönliches Erbe. Sicher. Redundant. Professionell.</p>
                            <div class="s_hr pt32 pb32" data-snippet="s_hr" data-name="Separator">
                                <hr class="w-25 mx-auto" style="border-top-width: 3px; border-top-color: #708090 !important;"/>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
            
            <section class="s_three_columns pt64 pb64 o_colored_level" data-snippet="s_three_columns" data-name="Columns">
                <div class="container">
                    <div class="row">
                        <div class="col-lg-4 s_col_no_bgcolor pt16 pb16" style="text-align: center;">
                            <div class="card bg-white border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h3 class="card-title" style="color: #001f3f;">Enterprise Cloud</h3>
                                    <p class="card-text">Ihre Daten, Ihre Regeln. Vollintegriertes Management Ihrer Geschäftsprozesse mit Odoo &amp; Nextcloud.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 s_col_no_bgcolor pt16 pb16" style="text-align: center;">
                            <div class="card bg-white border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h3 class="card-title" style="color: #001f3f;">Digital Archive</h3>
                                    <p class="card-text">Langzeitsicherheit für Ihr Wissen. Mit Paperless-ngx und redundanter Backup-Architektur.</p>
                                </div>
                            </div>
                        </div>
                        <div class="col-lg-4 s_col_no_bgcolor pt16 pb16" style="text-align: center;">
                            <div class="card bg-white border-0 shadow-sm h-100">
                                <div class="card-body">
                                    <h3 class="card-title" style="color: #001f3f;">Network Edge</h3>
                                    <p class="card-text">Gehärtete Infrastruktur. Maximale Performance und Sicherheit durch Cloudflare &amp; UniFi-Integration.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>
"""

def inject_content():
    try:
        # Load Hero
        with open('/tmp/frawo_hero.png', 'rb') as f:
            hero_data = base64.b64encode(f.read()).decode('utf-8')

        # Create attachment for hero image so it's accessible via URL in Odoo
        Attachment = env['ir.attachment']
        hero_attach = Attachment.search([('name', '=', 'frawo_hero_banner.png')], limit=1)
        if not hero_attach:
            hero_attach = Attachment.create({
                'name': 'frawo_hero_banner.png',
                'type': 'binary',
                'datas': hero_data,
                'public': True,
                'mimetype': 'image/png'
            })
        hero_url = f"/web/image/{hero_attach.id}"
        
        # Patch the XML with the real attachment URL
        final_xml = HOMEPAGE_XML.replace('/tmp/frawo_hero.png', hero_url)

        # Update Homepage View
        view = env.ref('website.homepage')
        view.write({'arch_db': final_xml})
        print("Updated Homepage successfully.")

        env.cr.commit()
    except Exception as e:
        print(f"Error: {e}")
        env.cr.rollback()

inject_content()

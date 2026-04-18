import base64

# IDs
COMPANY_ID = 1
WEBSITE_ID = 1

IMPRESSUM_HTML = """
<div id="wrap" class="oe_structure oe_empty">
    <section class="s_text_block pt40 pb40 o_colored_level" data-snippet="s_text_block">
        <div class="container">
            <h1 class="display-3-fs">Impressum</h1>
            <hr class="w-25 ml-0" style="border-top-width: 3px; border-top-color: #708090;"/>
            
            <div class="row pt32">
                <div class="col-lg-6">
                    <h3>Angaben gemäß § 5 TMG</h3>
                    <p>
                        <strong>FraWo GbR</strong><br/>
                        Wolfgang Prinz &amp; Florian Franz<br/>
                        Stockenweiler 3<br/>
                        88138 Hergensweiler<br/>
                        Deutschland
                    </p>
                </div>
                <div class="col-lg-6">
                    <h3>Kontakt</h3>
                    <p>
                        E-Mail: <a href="mailto:wolf@frawo-tech.de">wolf@frawo-tech.de</a><br/>
                        Internet: <a href="https://www.frawo-tech.de">www.frawo-tech.de</a>
                    </p>
                </div>
            </div>

            <div class="row pt32">
                <div class="col-lg-12">
                    <h3>Redaktionell Verantwortlicher</h3>
                    <p>
                        Wolfgang Prinz<br/>
                        Stockenweiler 3<br/>
                        88138 Hergensweiler
                    </p>
                    
                    <h3>EU-Streitschlichtung</h3>
                    <p>Die Europäische Kommission stellt eine Plattform zur Online-Streitbeilegung (OS) bereit: <a href="https://ec.europa.eu/consumers/odr/" target="_blank">https://ec.europa.eu/consumers/odr/</a>.<br/>Unsere E-Mail-Adresse finden Sie oben im Impressum.</p>
                    
                    <h3>Verbraucherstreitbeilegung/Universalschlichtungsstelle</h3>
                    <p>Wir sind nicht bereit oder verpflichtet, an Streitbeilegungsverfahren vor einer Verbraucherschlichtungsstelle teilzunehmen.</p>
                </div>
            </div>
        </div>
    </section>
</div>
"""

PRIVACY_HTML = """
<div id="wrap" class="oe_structure oe_empty">
    <section class="s_text_block pt40 pb40 o_colored_level" data-snippet="s_text_block">
        <div class="container">
            <h1 class="display-3-fs">Datenschutzerklärung</h1>
            <hr class="w-25 ml-0" style="border-top-width: 3px; border-top-color: #708090;"/>
            
            <div class="pt32">
                <h3>1. Datenschutz auf einen Blick</h3>
                <p>Wir freuen uns über Ihr Interesse an unserer Website. Der Schutz Ihrer persönlichen Daten ist uns ein wichtiges Anliegen. Nachfolgend informieren wir Sie über den Umgang mit Ihren Daten.</p>
                
                <h3>2. Verantwortliche Stelle</h3>
                <p>Verantwortlich für die Datenverarbeitung auf dieser Website ist:<br/>
                FraWo GbR<br/>
                Stockenweiler 3<br/>
                88138 Hergensweiler<br/>
                E-Mail: wolf@frawo-tech.de</p>
                
                <h3>3. Datenerfassung auf unserer Website</h3>
                <p>Ihre Daten werden zum einen dadurch erhoben, dass Sie uns diese mitteilen (z. B. im Kontaktformular). Andere Daten werden automatisch beim Besuch der Website durch unsere IT-Systeme (z. B. IP-Adresse, Browser) erfasst.</p>
                
                <h3>4. Hosting</h3>
                <p>Wir hosten die Inhalte unserer Website bei folgendem Anbieter: <strong>Eigener Betrieb (Homeserver 2027) mit Cloudflare Edge Protection</strong>. Die Datenübertragung wird durch SSL-Verschlüsselung gesichert.</p>
            </div>
        </div>
    </section>
</div>
"""

def execute_legal_migration():
    try:
        # 1. Update Company Record
        company = env['res.company'].browse(COMPANY_ID)
        company.write({
            'name': 'FraWo GbR',
            'street': 'Stockenweiler 3',
            'zip': '88138',
            'city': 'Hergensweiler',
            'country_id': env.ref('base.de').id,
            'email': 'wolf@frawo-tech.de',
            'website': 'https://www.frawo-tech.de',
            'phone': False, # Per research, keep empty/hidden for now
        })
        print(f"Updated Company: {company.name} at {company.street}")

        # 2. Add Legal Pages
        Page = env['website.page']
        View = env['ir.ui.view']
        
        # Impressum
        imp_page = Page.search([('url', '=', '/impressum')], limit=1)
        if not imp_page:
            view = View.create({
                'name': 'Impressum',
                'type': 'qweb',
                'arch': IMPRESSUM_HTML,
                'key': 'website.impressum_page_view',
            })
            imp_page = Page.create({
                'name': 'Impressum',
                'url': '/impressum',
                'view_id': view.id,
                'is_published': True,
            })
        else:
            imp_page.view_id.write({'arch': IMPRESSUM_HTML})
            imp_page.write({'is_published': True})
        
        # Privacy
        priv_page = Page.search([('url', '=', '/datenschutz')], limit=1)
        if not priv_page:
            view = View.create({
                'name': 'Datenschutz',
                'type': 'qweb',
                'arch': PRIVACY_HTML,
                'key': 'website.privacy_page_view',
            })
            priv_page = Page.create({
                'name': 'Datenschutz',
                'url': '/datenschutz',
                'view_id': view.id,
                'is_published': True,
            })
        else:
            priv_page.view_id.write({'arch': PRIVACY_HTML})
            priv_page.write({'is_published': True})

        # 3. Footer Update (Links)
        # We need to find the footer view and append links if they don't exist
        # Simplified: We ensure the URLs exist, user can link them in the menu as well.
        
        env.cr.commit()
        print("Legal migration successful.")
        
    except Exception as e:
        print(f"Error: {e}")
        env.cr.rollback()

execute_legal_migration()

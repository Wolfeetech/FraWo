CSS_CONTENT = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');

:root {
  --fw-bg: #0a0a0a;
  --fw-surface: #141414;
  --fw-text: #f0f0ee;
  --fw-text-2: #a0a09e;
  --fw-accent: #ff6b1a;
  --fw-border: #2a2a2a;
}

body, #wrapwrap {
    background-color: var(--fw-bg) !important;
    color: var(--fw-text) !important;
    font-family: 'Inter', sans-serif !important;
}

#wrap {
    background-color: var(--fw-bg) !important;
}

header#top, footer {
    background-color: var(--fw-bg) !important;
    border-color: var(--fw-border) !important;
    color: var(--fw-text) !important;
}

.fw-section {
    padding: 100px 0;
    border-bottom: 1px solid var(--fw-border);
}
.fw-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 40px;
}
.fw-hero {
    min-height: 80vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-bottom: 1px solid var(--fw-border);
    background: var(--fw-bg);
}
.fw-eyebrow {
    color: var(--fw-accent);
    text-transform: uppercase;
    font-weight: 800;
    letter-spacing: 0.1em;
    margin-bottom: 1rem;
    display: block;
    font-size: 0.9rem;
}
.fw-h1 {
    font-size: clamp(3.5rem, 8vw, 6rem);
    font-weight: 900;
    line-height: 1.0;
    margin-bottom: 2rem;
    letter-spacing: -0.03em;
    color: var(--fw-text);
}
.fw-h2 {
    font-size: clamp(2rem, 5vw, 4rem);
    font-weight: 900;
    line-height: 1.1;
    margin-bottom: 1.5rem;
    color: var(--fw-text);
}
.fw-h3 {
    font-size: 1.5rem;
    font-weight: 800;
    margin-bottom: 1rem;
    color: var(--fw-text);
}
.fw-lead {
    font-size: 1.25rem;
    color: var(--fw-text-2);
    line-height: 1.6;
    max-width: 800px;
    margin-bottom: 3rem;
}
.fw-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: var(--fw-text);
    color: var(--fw-bg) !important;
    padding: 16px 32px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    text-decoration: none !important;
    border: 2px solid var(--fw-text);
    transition: all 0.2s ease;
}
.fw-btn:hover {
    background: var(--fw-accent);
    border-color: var(--fw-accent);
    color: var(--fw-text) !important;
}
.fw-btn-outline {
    background: transparent;
    color: var(--fw-text) !important;
    border-color: var(--fw-border);
}
.fw-btn-outline:hover {
    background: var(--fw-surface);
    border-color: var(--fw-text);
}
.fw-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 40px;
}
.fw-card {
    background: var(--fw-surface);
    border: 1px solid var(--fw-border);
    padding: 40px;
    transition: border-color 0.2s ease;
}
.fw-card:hover {
    border-color: var(--fw-accent);
}
.fw-card p {
    color: var(--fw-text-2);
    line-height: 1.6;
}
.fw-img {
    width: 100%;
    height: 400px;
    object-fit: cover;
    border: 1px solid var(--fw-border);
    filter: grayscale(20%) contrast(120%);
}

.fw-b2b-teaser {
    background: var(--fw-surface);
    border-top: 1px solid var(--fw-border);
    padding: 80px 0;
    text-align: left;
}
.fw-b2b-teaser h2 {
    color: var(--fw-text);
}

.fw-player {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 70px;
    background: var(--fw-surface);
    border-top: 1px solid var(--fw-border);
    display: flex;
    align-items: center;
    padding: 0 20px;
    z-index: 9999;
    gap: 20px;
    font-family: 'Inter', sans-serif;
}
.fw-player-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    text-transform: uppercase;
    color: var(--fw-text);
}
.fw-player-dot {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: #555;
}
.fw-player-btn {
    background: none;
    border: 1px solid var(--fw-border);
    color: var(--fw-text-2);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
    cursor: not-allowed;
}
.fw-player-info {
    flex-grow: 1;
    color: var(--fw-text-2);
    font-size: 0.9rem;
}
.fw-player-controls {
    display: flex;
    gap: 15px;
    align-items: center;
}
"""

HOMEPAGE_HTML = """
<div class="fw-homepage">
    <style>
        {css_content}
    </style>
    <section class="fw-hero">
        <div class="fw-container">
            <span class="fw-eyebrow">FraWo Smart Media &amp; Event</span>
            <h1 class="fw-h1">Ton, Licht und<br/>gute Stimmung.</h1>
            <p class="fw-lead">
                Egal ob runder Geburtstag oder Gartenparty: Wir bringen die Technik, die deinen Abend unvergesslich macht. Hochzeiten auf Anfrage. Kein Stress, einfach feiern.
            </p>
            <div style="display:flex; gap:20px; flex-wrap:wrap;">
                <a href="/contactus" class="fw-btn">Projekt anfragen</a>
                <a href="#leistungen" class="fw-btn fw-btn-outline">Was wir machen</a>
            </div>
        </div>
    </section>

    <section id="leistungen" class="fw-section">
        <div class="fw-container">
            <span class="fw-eyebrow">Unsere Leistungen</span>
            <h2 class="fw-h2">Privat feiern,<br/>professionell klingen.</h2>
            <div class="fw-grid" style="margin-top: 60px;">
                <div class="fw-card">
                    <h3 class="fw-h3">Runde Geburtstage</h3>
                    <p>Fetter Sound und das richtige Licht für deine Party. Wir bauen auf, stellen ein und holen alles wieder ab.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Gartenpartys</h3>
                    <p>Outdoor-taugliche Beschallung und stimmungsvolle Beleuchtung für die perfekte Sommernacht.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Hochzeiten</h3>
                    <p>Auf spezielle Anfrage begleiten wir auch Hochzeiten mit Technik, die nicht im Weg steht, sondern unterstützt.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="fw-section" style="padding-top:0; border:none;">
        <div class="fw-container">
             <img src="/web/image/858" class="fw-img" alt="FraWo Eventtechnik" />
        </div>
    </section>

    <section class="fw-b2b-teaser">
        <div class="fw-container" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:40px;">
            <div style="max-width: 600px;">
                <span class="fw-eyebrow">Geschäftskunden &amp; Veranstalter</span>
                <h2 class="fw-h2" style="margin-bottom: 1rem;">Professionelle Eventtechnik &amp; Dienstleistung</h2>
                <p class="fw-lead" style="margin-bottom: 0;">
                    Fachkräfte für Veranstaltungstechnik, FOH, Bühnenbau und unser Bestseller: Das Fußball-Dart-Rental.
                </p>
            </div>
            <div>
                <a href="/b2b" class="fw-btn">Zum B2B Bereich</a>
            </div>
        </div>
    </section>
</div>
"""

B2B_HTML = """
<div class="fw-b2b-page">
    <style>
        {css_content}
    </style>
    <section class="fw-hero" style="min-height: 60vh;">
        <div class="fw-container">
            <span class="fw-eyebrow">B2B &amp; Veranstalter</span>
            <h1 class="fw-h1">Verlässliche Technik.<br/>Klarer Ablauf.</h1>
            <p class="fw-lead">
                Wir unterstützen Festivals, Konferenzen und Open Airs mit Fachpersonal, Material und Sonderbauten. 
            </p>
            <a href="/contactus" class="fw-btn">Anfrage senden</a>
        </div>
    </section>

    <section class="fw-section">
        <div class="fw-container">
            <h2 class="fw-h2" style="margin-bottom: 60px;">Unsere B2B Leistungen</h2>
            <div class="fw-grid">
                <div class="fw-card" style="border-color: var(--fw-accent);">
                    <span class="fw-eyebrow">Bestseller</span>
                    <h3 class="fw-h3">Fußball-Dart-Rental</h3>
                    <p>Der Publikumsmagnet für Firmenfeiern, Festivals und Fan-Zones. Komplett-Miete inklusive Aufbau und Betreuung.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">FOH &amp; Monitor</h3>
                    <p>Präziser Mix am Front of House und auf der Bühne. Erfahrene Techniker für den perfekten Sound.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Licht &amp; Medien</h3>
                    <p>Konferenz- und Eventtechnik. Vom Beamer-Setup bis zur komplexen Lichtshow für Präsentationen.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Fachpersonal</h3>
                    <p>Fachkraft für Veranstaltungstechnik, Stage Helfer für Open Airs und Festivals. Wir packen an und leiten an.</p>
                </div>
                <div class="fw-card">
                    <h3 class="fw-h3">Sonderbauten (Holz)</h3>
                    <p>Spezialanfertigungen für Bühne und Event vom Fachmann (Zimmermann). Maßgeschneidert und solide.</p>
                </div>
            </div>
        </div>
    </section>
    
    <section class="fw-section" style="padding-top:0;">
        <div class="fw-container">
             <img src="/web/image/859" class="fw-img" alt="FraWo B2B Eventtechnik" />
        </div>
    </section>
</div>
"""

CONTACT_HTML = """
<div class="fw-contact-page">
    <style>
        {css_content}
    </style>
    <section class="fw-hero" style="min-height: 70vh;">
        <div class="fw-container">
            <span class="fw-eyebrow">Kontakt</span>
            <h1 class="fw-h1">Lass uns reden.</h1>
            <p class="fw-lead">
                Egal ob privates Fest oder großes Festival: Ruf uns an oder schreib eine Mail. Wir kümmern uns.
            </p>
            <div class="fw-grid" style="margin-top: 60px;">
                <div class="fw-card">
                    <span class="fw-eyebrow">E-Mail</span>
                    <a href="mailto:info@frawo-tech.de" class="fw-h3" style="text-decoration:none; display:block; margin-bottom:10px;">info@frawo-tech.de</a>
                    <p>Für Anfragen, Details und Planung.</p>
                </div>
                <div class="fw-card">
                    <span class="fw-eyebrow">Telefon</span>
                    <a href="tel:+4915155243164" class="fw-h3" style="text-decoration:none; display:block; margin-bottom:10px;">+49 151 55243164</a>
                    <p>Für direkte Fragen und schnelle Abstimmung.</p>
                </div>
                <div class="fw-card">
                    <span class="fw-eyebrow">Standort</span>
                    <h3 class="fw-h3" style="margin-bottom:10px;">FraWo GbR</h3>
                    <p>Rothkreuz 14<br/>88138 Weißensberg</p>
                </div>
            </div>
        </div>
    </section>
</div>
"""

PLAYER_SKELETON = """
<div class="fw-player">
  <div class="fw-player-brand">
    <span class="fw-player-dot"></span>
    FraWo Funk
  </div>
  <button class="fw-player-btn">▶</button>
  <div class="fw-player-info">
    Stream offline — Coming soon
  </div>
  <div class="fw-player-controls">
    <span style="color:var(--fw-text-2);">🔈</span>
    <input type="range" min="0" max="100" value="50" disabled="disabled" style="width: 80px; opacity: 0.5;"/>
    <button class="fw-player-btn" style="width:30px; height:30px; font-size:12px;">👍</button>
    <button class="fw-player-btn" style="width:30px; height:30px; font-size:12px;">👎</button>
  </div>
</div>
"""

home_html = HOMEPAGE_HTML.format(css_content=CSS_CONTENT)
b2b_html = B2B_HTML.format(css_content=CSS_CONTENT)
contact_html = CONTACT_HTML.format(css_content=CSS_CONTENT)

# 1. Update Homepage
homepage = env['ir.ui.view'].search([('key', '=', 'website.homepage')])
if homepage:
    homepage.arch_db = f'<?xml version="1.0"?>\\n<t name="Homepage" t-name="website.homepage">\\n    <t t-call="website.layout">\\n        <div id="wrap" class="oe_structure oe_empty">\\n            {home_html}\\n        </div>\\n    </t>\\n</t>'
    print("Updated Homepage.")

# 2. Update Contact Page
contact = env['ir.ui.view'].search([('key', 'ilike', 'contactus')])
if contact:
    contact.arch_db = f'<?xml version="1.0"?>\\n<t name="Contact us" t-name="website.contactus">\\n    <t t-call="website.layout">\\n        <div id="wrap" class="oe_structure oe_empty">\\n            {contact_html}\\n        </div>\\n    </t>\\n</t>'
    print("Updated Contact Page.")

# 3. Create/Update B2B Page
b2b = env['ir.ui.view'].search([('key', '=', 'website.frawo_b2b')])
b2b_arch = f'<?xml version="1.0"?>\\n<t name="B2B" t-name="website.frawo_b2b">\\n    <t t-call="website.layout">\\n        <div id="wrap" class="oe_structure oe_empty">\\n            {b2b_html}\\n        </div>\\n    </t>\\n</t>'
if b2b:
    b2b.arch_db = b2b_arch
    print("Updated B2B Page.")
else:
    view = env['ir.ui.view'].create({
        'name': 'B2B',
        'type': 'qweb',
        'key': 'website.frawo_b2b',
        'arch_db': b2b_arch
    })
    env['website.page'].create({
        'url': '/b2b',
        'view_id': view.id,
        'is_published': True,
        'website_indexed': True
    })
    print("Created B2B Page.")

# 4. Inject Player Skeleton into Footer Layout
layout_override = env['ir.ui.view'].search([('key', '=', 'website.frawo_player_override')])
layout_override_arch = f'''<?xml version="1.0"?>
<data inherit_id="website.layout" name="FraWo Player Overlay" active="True">
    <xpath expr="//div[@id='wrapwrap']" position="inside">
        {PLAYER_SKELETON}
    </xpath>
</data>'''
if layout_override:
    layout_override.arch_db = layout_override_arch
    print("Updated Player Skeleton.")
else:
    layout = env['ir.ui.view'].search([('key', '=', 'website.layout')], limit=1)
    env['ir.ui.view'].create({
        'name': 'FraWo Player Overlay',
        'type': 'qweb',
        'key': 'website.frawo_player_override',
        'inherit_id': layout.id,
        'arch_db': layout_override_arch
    })
    print("Created Player Skeleton.")

env.cr.commit()
print("SUCCESS: Website v3 deployed via Odoo Shell.")

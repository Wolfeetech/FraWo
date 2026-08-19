$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$cssContent = @"
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&amp;display=swap');
:root { 
    --fw-bg: #0a0a0a; 
    --fw-surface: #141414; 
    --fw-text: #f0f0ee; 
    --fw-accent: #ff6b1a; 
    --fw-border: #2a2a2a; 
}
/* Global Reset */
html, body, #wrapwrap {
    background-color: var(--fw-bg) !important;
    color: var(--fw-text) !important;
    font-family: 'Inter', sans-serif !important;
}
/* REMOVE Odoo Admin Junk from the frontend */
.o_main_navbar, #oe_main_menu_wrapper, .o_notification_manager {
    display: none !important;
}
/* Fix Header */
header#top {
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
    background-color: rgba(10, 10, 10, 0.9) !important;
    backdrop-filter: blur(10px);
    border-bottom: 1px solid var(--fw-border) !important;
}
.navbar {
    padding: 20px 0 !important;
}
.navbar-brand img {
    height: 35px !important;
    width: auto !important;
    filter: brightness(0) invert(1); /* Make logo white if needed */
}
.nav-link {
    color: var(--fw-text) !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    padding: 10px 20px !important;
}
.nav-link:hover {
    color: var(--fw-accent) !important;
}
/* Hero Section Polish */
.fw-hero {
    padding: 180px 0 100px 0 !important;
}
.fw-h1 {
    font-size: clamp(3rem, 10vw, 7rem) !important;
    font-weight: 900 !important;
    line-height: 0.9 !important;
    letter-spacing: -0.05em !important;
    margin-bottom: 30px !important;
}
.fw-btn {
    background: var(--fw-accent) !important;
    color: white !important;
    border: none !important;
    padding: 20px 40px !important;
    font-size: 1rem !important;
    font-weight: 900 !important;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}
"@

$pythonCode = @"
css_content = '''$cssContent'''
homepage = env['ir.ui.view'].search([('key', '=', 'website.homepage')])
home_arch = '''<t t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="fw-hero" style="background: #0a0a0a;">
                <div class="container">
                    <span style="color: #ff6b1a; font-weight: 900; text-transform: uppercase; letter-spacing: 0.2em; font-size: 0.9rem;">FraWo Smart Media</span>
                    <h1 class="fw-h1">Ton, Licht<br/>Stimmung.</h1>
                    <p style="font-size: 1.4rem; color: #a0a09e; max-width: 700px; line-height: 1.5; margin-bottom: 50px;">
                        Professionelle Event-Infrastruktur fÃ¼r Privathausbehalte &amp; B2B. 
                        Vom Gartenfest bis zum Open Air â€“ wir liefern die Technik, die man nicht sieht, aber perfekt hÃ¶rt.
                    </p>
                    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                        <a href="/contactus" class="fw-btn">Projekt anfragen</a>
                        <a href="/b2b" style="display: inline-block; border: 2px solid #2a2a2a; color: white; padding: 18px 36px; font-weight: 800; text-decoration: none; text-transform: uppercase; letter-spacing: 0.1em;">B2B Bereich</a>
                    </div>
                </div>
            </section>
            
            <section style="padding: 100px 0; background: #0a0a0a; border-top: 1px solid #2a2a2a;">
                <div class="container">
                    <div class="row">
                        <div class="col-md-4 mb-5">
                            <h3 style="color: #ff6b1a; font-weight: 900; margin-bottom: 20px;">01. Private Events</h3>
                            <p style="color: #a0a09e; line-height: 1.6;">Runde Geburtstage, Hochzeiten (auf Anfrage) und Gartenpartys. Alles inklusive Auf- und Abbau.</p>
                        </div>
                        <div class="col-md-4 mb-5">
                            <h3 style="color: #ff6b1a; font-weight: 900; margin-bottom: 20px;">02. B2B &amp; Festivals</h3>
                            <p style="color: #a0a09e; line-height: 1.6;">Fachpersonal (Vt-Techniker, Stagehands), FOH &amp; Monitor-Mix, Sonderbauten aus Holz.</p>
                        </div>
                        <div class="col-md-4 mb-5">
                            <h3 style="color: #ff6b1a; font-weight: 900; margin-bottom: 20px;">03. Special Rental</h3>
                            <p style="color: #a0a09e; line-height: 1.6;">Unser Bestseller fÃ¼r Firmen-Events: Das FuÃŸball-Dart-Rental inklusive Betreuung.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>'''
homepage.write({'arch': home_arch})

# Force Global CSS
layout_override = env['ir.ui.view'].search([('key', '=', 'website.frawo_global_css')])
arch = f'<xpath expr="//head" position="inside"><style>{css_content}</style></xpath>'

if not layout_override:
    layout_id = env['ir.ui.view'].search([('key', '=', 'website.layout')], limit=1).id
    env['ir.ui.view'].create({
        'name': 'FraWo Global CSS',
        'key': 'website.frawo_global_css',
        'type': 'qweb',
        'mode': 'extension',
        'inherit_id': layout_id,
        'arch': arch,
        'active': True,
        'priority': 99
    })
else:
    layout_override.write({'arch': arch})

env.cr.commit()
"@

$pyBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pythonCode))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$pyBase64" | base64 -d > /tmp/clean_v3_design.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=__ROTATED_SECRET__ --no-http < /tmp/clean_v3_design.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Cleaning and Forcing Premium v3 Design..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Premium design forced."

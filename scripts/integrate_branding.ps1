$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

# Encoding fix: Using Unicode escape sequences for German characters
# Ã¼ = \u00fc, ÃŸ = \u00df, Ã¤ = \u00e4, Ã¶ = \u00f6

$cssContent = @"
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&amp;display=swap');
:root { 
    --fw-bg: #0a0a0a; 
    --fw-surface: #141414;
    --fw-text: #f0f0ee; 
    --fw-accent: #ff6b1a; 
    --fw-border: #2a2a2a; 
}
html, body, #wrapwrap {
    background-color: var(--fw-bg) !important;
    color: var(--fw-text) !important;
    font-family: 'Inter', sans-serif !important;
    margin: 0 !important; padding: 0 !important;
}
header, #oe_main_menu_wrapper, .o_main_navbar, .o_header_mobile {
    display: none !important;
}
.fw-custom-header {
    background: rgba(10, 10, 10, 0.9);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--fw-border);
    position: fixed;
    top: 0; left: 0; width: 100%; z-index: 99999;
    padding: 15px 0;
}
.fw-nav {
    max-width: 1200px; margin: 0 auto; padding: 0 40px;
    display: flex; justify-content: space-between; align-items: center;
}
.fw-logo-img { height: 40px; width: auto; filter: brightness(0) invert(1); }
.fw-menu { display: flex; gap: 40px; }
.fw-menu a { color: #888; text-decoration: none; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.15em; transition: all 0.3s ease; }
.fw-menu a:hover { color: white; }
.fw-hero { padding: 180px 0 120px 0; }
.fw-h1 { font-size: clamp(3rem, 10vw, 7rem); font-weight: 900; line-height: 0.9; letter-spacing: -0.05em; margin: 20px 0; }
.fw-accent-text { color: var(--fw-accent); }
.fw-btn { background: white; color: black !important; padding: 20px 40px; font-weight: 900; text-transform: uppercase; letter-spacing: 0.1em; text-decoration: none !important; display: inline-block; }
.fw-btn:hover { background: var(--fw-accent); color: white !important; }
"@

$pythonCode = @"
import json

css_content = '''$cssContent'''
logo_url = '/web/image/website/1/logo/FraWo%20GbR%20-%20Veranstaltungstechnik%20%26%20Event-Infrastruktur'

# 1. Update Layout (Header & CSS)
layout_override = env['ir.ui.view'].search([('key', '=', 'website.frawo_global_css')])
layout_id = env['ir.ui.view'].search([('key', '=', 'website.layout')], limit=1).id

layout_arch = f'''
<data>
    <xpath expr="//head" position="inside">
        <style>{css_content}</style>
    </xpath>
    <xpath expr="//div[@id='wrapwrap']" position="after">
        <div class="fw-custom-header">
            <div class="fw-nav">
                <a href="/"><img src="{logo_url}" class="fw-logo-img" alt="FraWo Logo"/></a>
                <div class="fw-menu">
                    <a href="/">Home</a>
                    <a href="/b2b">B2B</a>
                    <a href="/contactus">Kontakt</a>
                </div>
            </div>
        </div>
    </xpath>
</data>'''

if not layout_override:
    env['ir.ui.view'].create({
        'name': 'FraWo Global CSS',
        'key': 'website.frawo_global_css',
        'type': 'qweb',
        'mode': 'extension',
        'inherit_id': layout_id,
        'arch': layout_arch,
        'active': True,
        'priority': 1
    })
else:
    layout_override.write({'arch': layout_arch})

# 2. Update Homepage (Content & Encoding Fix)
homepage = env['ir.ui.view'].search([('key', '=', 'website.homepage')])
# Using unicode escapes for German characters to avoid encoding mess
home_arch = u'''<t t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="fw-hero">
                <div class="container">
                    <span class="fw-accent-text" style="font-weight: 900; text-transform: uppercase; letter-spacing: 0.3em; font-size: 0.8rem;">FraWo Smart Media &amp; Event</span>
                    <h1 class="fw-h1">Ton, Licht<br/>Stimmung.</h1>
                    <p style="font-size: 1.5rem; color: #a0a09e; max-width: 750px; line-height: 1.4; margin-bottom: 50px;">
                        Professionelle Event-Infrastruktur f\u00fcr Privathaushalte &amp; B2B. 
                        Vom Gartenfest bis zum Open Air \u2013 wir liefern die Technik, die man nicht sieht, aber perfekt h\u00f6rt.
                    </p>
                    <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                        <a href="/contactus" class="fw-btn">Projekt anfragen</a>
                        <a href="/b2b" style="display: inline-block; border: 2px solid #2a2a2a; color: white; padding: 18px 36px; font-weight: 800; text-decoration: none; text-transform: uppercase; letter-spacing: 0.1em;">B2B Bereich</a>
                    </div>
                </div>
            </section>
            
            <section style="padding: 100px 0; border-top: 1px solid #2a2a2a;">
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
                            <p style="color: #a0a09e; line-height: 1.6;">Unser Bestseller f\u00fcr Firmen-Events: Das Fu\u00dfball-Dart-Rental inklusive Betreuung.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </t>
</t>'''
homepage.write({'arch': home_arch})

env.cr.commit()
print("SUCCESS: Logo, Encoding and Design Integrated")
"@

$pyBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pythonCode))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$pyBase64" | base64 -d > /tmp/integrate_branding.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=__ROTATED_SECRET__ --no-http < /tmp/integrate_branding.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Integrating FraWo Logo and Fixing Encoding..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Branding integrated."

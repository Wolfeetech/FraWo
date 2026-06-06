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
html, body, #wrapwrap {
    background-color: var(--fw-bg) !important;
    color: var(--fw-text) !important;
    font-family: 'Inter', sans-serif !important;
}
header#top, .navbar, .o_header_mobile, .o_header_mobile_buttons_wrap, .o_main_nav {
    background-color: var(--fw-bg) !important;
    border-bottom: 1px solid var(--fw-border) !important;
    color: var(--fw-text) !important;
}
.navbar-brand, .nav-link, .btn-link, .text-muted, .text-bg-light {
    color: var(--fw-text) !important;
    background-color: transparent !important;
}
input.search-query {
    background-color: var(--fw-surface) !important;
    color: var(--fw-text) !important;
    border: 1px solid var(--fw-border) !important;
}
footer {
    background-color: var(--fw-bg) !important;
    border-top: 1px solid var(--fw-border) !important;
}
"@

$pythonCode = @"
css_content = '''$cssContent'''
homepage = env['ir.ui.view'].search([('key', '=', 'website.homepage')])
home_arch = '''<t t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="s_title" style="padding: 120px 0; background: #0a0a0a;">
                <div class="container">
                    <span style="color: #ff6b1a; font-weight: 800; text-transform: uppercase; letter-spacing: 0.1em;">FraWo Smart Media</span>
                    <h1 style="font-size: clamp(3rem, 8vw, 6rem); font-weight: 900; line-height: 1.0; margin: 20px 0;">Ton, Licht und<br/>gute Stimmung.</h1>
                    <p style="font-size: 1.25rem; color: #a0a09e; max-width: 600px; margin-bottom: 40px;">Wir bringen die Technik, die deinen Abend unvergesslich macht. Vom runden Geburtstag bis zur Gartenparty.</p>
                    <a href="/contactus" style="display: inline-block; background: #f0f0ee; color: #0a0a0a; padding: 18px 36px; font-weight: 800; text-decoration: none; text-transform: uppercase; letter-spacing: 0.05em;">Projekt anfragen</a>
                </div>
            </section>
            <div class="oe_structure"></div>
        </div>
    </t>
</t>'''
homepage.write({'arch': home_arch})

# Force CSS into the Global Layout
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
print("SUCCESS: Global Design Forced")
"@

$pyBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pythonCode))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$pyBase64" | base64 -d > /tmp/force_full_design.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http < /tmp/force_full_design.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Forcing Global Dark Mode Design (with &amp; fix)..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Full design forced."

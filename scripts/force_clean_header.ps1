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
    margin: 0 !important; padding: 0 !important;
}
/* Force hide Odoo junk */
header, #oe_main_menu_wrapper, .o_main_navbar, .o_header_mobile, .o_header_standard {
    display: none !important;
    height: 0 !important;
    visibility: hidden !important;
}
.fw-custom-header {
    background: rgba(10, 10, 10, 0.95);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--fw-border);
    position: fixed;
    top: 0; left: 0; width: 100%; z-index: 99999;
    padding: 20px 0;
}
.fw-nav {
    max-width: 1200px; margin: 0 auto; padding: 0 40px;
    display: flex; justify-content: space-between; align-items: center;
}
.fw-logo { font-weight: 900; font-size: 1.8rem; color: white; text-decoration: none; letter-spacing: -0.03em; }
.fw-logo span { color: var(--fw-accent); }
.fw-menu { display: flex; gap: 40px; }
.fw-menu a { color: #888; text-decoration: none; font-weight: 800; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.2em; transition: all 0.3s ease; }
.fw-menu a:hover { color: var(--fw-accent); }
.fw-hero { padding-top: 180px !important; }
"@

$pythonCode = @"
css_content = '''$cssContent'''
layout_override = env['ir.ui.view'].search([('key', '=', 'website.frawo_global_css')])
layout_id = env['ir.ui.view'].search([('key', '=', 'website.layout')], limit=1).id

arch = f'''
<data>
    <xpath expr="//head" position="inside">
        <style>{css_content}</style>
    </xpath>
    <xpath expr="//div[@id='wrapwrap']" position="after">
        <div class="fw-custom-header">
            <div class="fw-nav">
                <a href="/" class="fw-logo">FRAWO<span>.</span></a>
                <div class="fw-menu">
                    <a href="/">Home</a>
                    <a href="/b2b">B2B</a>
                    <a href="/contactus">Kontakt</a>
                </div>
            </div>
        </div>
    </xpath>
</data>'''

layout_override.write({'arch': arch})
env.cr.commit()
"@

$pyBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pythonCode))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$pyBase64" | base64 -d > /tmp/force_clean_header.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=__ROTATED_SECRET__ --no-http < /tmp/force_clean_header.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Forcing Header Outside wrapwrap..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Design replaced."

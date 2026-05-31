$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$pythonCode = @"
# Odoo Shell Script
homepage = env['ir.ui.view'].search([('key', '=', 'website.homepage')])
arch = '''<t t-name="website.homepage">
    <t t-call="website.layout">
        <div id="wrap" class="oe_structure">
            <section class="s_title" data-snippet="s_title" data-name="Title" style="background-color: #0a0a0a; color: white; padding: 100px 0;">
                <div class="container">
                    <h1 style="font-size: 4rem; font-weight: 900;">FraWo</h1>
                    <p class="lead">Ton, Licht und gute Stimmung.</p>
                </div>
            </section>
        </div>
    </t>
</t>'''
homepage.write({'arch': arch})
env.cr.commit()
print("SUCCESS: Homepage updated via Odoo Shell")
"@

$pyBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($pythonCode))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$pyBase64" | base64 -d > /tmp/restore_home.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T web odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http < /tmp/restore_home.py'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Restoring homepage via Odoo Shell (safe method)..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Deployment complete."

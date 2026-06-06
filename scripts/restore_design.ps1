$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$cssContent = @"
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap');
:root { --fw-bg: #0a0a0a; --fw-surface: #141414; --fw-text: #f0f0ee; --fw-accent: #ff6b1a; --fw-border: #2a2a2a; }
body, #wrapwrap { background-color: var(--fw-bg) !important; color: var(--fw-text) !important; font-family: 'Inter', sans-serif !important; }
#wrap { background-color: var(--fw-bg) !important; }
header#top, footer { background-color: var(--fw-bg) !important; border-color: var(--fw-border) !important; color: var(--fw-text) !important; }
.fw-hero { min-height: 60vh; display: flex; flex-direction: column; justify-content: center; background: var(--fw-bg); padding: 60px 20px; }
.fw-h1 { font-size: 3.5rem; font-weight: 900; line-height: 1.1; margin-bottom: 1rem; }
.fw-lead { font-size: 1.2rem; color: #a0a09e; margin-bottom: 2rem; }
.fw-btn { display: inline-block; background: var(--fw-text); color: var(--fw-bg) !important; padding: 14px 28px; font-weight: 800; text-decoration: none !important; }
"@

# Stripped XML (no root t-name)
$homeXml = @"
<t t-call="website.layout">
    <div id="wrap" class="oe_structure oe_empty">
        <style>
            $cssContent
        </style>
        <section class="fw-hero">
            <div class="container">
                <h1 class="fw-h1">Ton, Licht und gute Stimmung.</h1>
                <p class="fw-lead">Wir bringen die Technik fÃ¼r deine Party.</p>
                <a href="/contactus" class="fw-btn">Projekt anfragen</a>
            </div>
        </section>
    </div>
</t>
"@

$sql = @"
set client_encoding to 'utf8';
begin;
update ir_ui_view
set arch_db = jsonb_build_object('en_US', '$($homeXml.Replace("'", "''"))', 'de_DE', '$($homeXml.Replace("'", "''"))')
where key = 'website.homepage';
commit;
"@

$sqlBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sql))

$remote = @"
qm guest exec 220 -- bash -c 'echo "$sqlBase64" | base64 -d > /tmp/restore_v3.sql'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T db psql -U odoo -d FraWo_GbR < /tmp/restore_v3.sql'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Restoring design with stripped QWeb XML..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Deployment complete."

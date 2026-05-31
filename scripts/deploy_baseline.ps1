$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"

$sqlFile = Join-Path $PSScriptRoot "deploy_v3.sql"
$sqlContent = @"
begin;

-- Update Homepage view with oe_structure to keep it editable
update ir_ui_view
set arch_db = '{"en_US": "<t name=\"Homepage\" t-name=\"website.homepage\"><t t-call=\"website.layout\"><div id=\"wrap\" class=\"oe_structure oe_empty\"></div></t></t>"}'::jsonb
where key = 'website.homepage';

-- Reset Custom CSS to something minimal but working
update ir_ui_view
set arch_db = '{"en_US": "<style>body { background: #0a0a0a !important; color: #f0f0ee !important; font-family: sans-serif; }</style>"}'::jsonb
where key = 'website.user_custom_css';

commit;
"@
[System.IO.File]::WriteAllText($sqlFile, $sqlContent)

$sqlBase64 = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($sqlContent))

# We send the SQL via base64 to avoid all shell escaping issues
$remote = @"
qm guest exec 220 -- bash -c 'echo "$sqlBase64" | base64 -d > /tmp/deploy_v3.sql'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose exec -T db psql -U odoo -d FraWo_GbR < /tmp/deploy_v3.sql'
qm guest exec 220 -- bash -lc 'cd /opt/homeserver2027/stacks/odoo && docker-compose restart web'
"@

Write-Host "Deploying minimal baseline to restore design..."
& $proxmoxExec -RemoteCommand $remote -SshHost "anker-pve"
Write-Host "Baseline deployed."

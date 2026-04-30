param()
$ErrorActionPreference = "Stop"

Write-Host "=" -NoNewline
1..69 | ForEach-Object { Write-Host "=" -NoNewline }
Write-Host ""
Write-Host "FraWo Website v3.5 - Final Deployment"
Write-Host "=" -NoNewline
1..69 | ForEach-Object { Write-Host "=" -NoNewline }
Write-Host "`n"

$repoRoot = Split-Path -Parent $PSScriptRoot
$docsDir = Join-Path $repoRoot "DOCS"

# Read v3.5 files
Write-Host "[1/3] Reading v3.5 files..."
$cssFile = Join-Path $docsDir "ODOO_GLOBAL_CSS_V3.5.css"
$homepageFile = Join-Path $docsDir "ODOO_HOMEPAGE_V3.5_READY_TO_USE.html"

if (-not (Test-Path $cssFile)) {
    Write-Host "   [X] CSS file not found: $cssFile"
    exit 1
}

if (-not (Test-Path $homepageFile)) {
    Write-Host "   [X] Homepage file not found: $homepageFile"
    exit 1
}

$cssContent = Get-Content -Path $cssFile -Raw -Encoding UTF8
$homepageContent = Get-Content -Path $homepageFile -Raw -Encoding UTF8

Write-Host "   [OK] Files loaded"

# Create Python deployment script
Write-Host "`n[2/3] Creating deployment script..."

$pythonScript = @"
import xmlrpc.client
import os
import sys

url = 'http://172.21.0.3:8069'
db = 'FraWo_GbR'
username = 'wolf@frawo-tech.de'
password = os.environ.get('ODOO_RPC_PASSWORD', '')

if not password:
    print('[X] No password found in ODOO_RPC_PASSWORD')
    sys.exit(1)

print('[1/2] Deploying Global CSS...')
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print('[X] Authentication failed')
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Deploy CSS
css_content = '''$($cssContent.Replace("'", "''"))'''
website_ids = models.execute_kw(db, uid, password, 'website', 'search', [[]], {'limit': 1})
models.execute_kw(db, uid, password, 'website', 'write', [website_ids, {
    'custom_code_head': f'<style>{css_content}</style>'
}])
print('   [OK] Global CSS deployed')

# Deploy Homepage
print('[2/2] Deploying Homepage...')
homepage_content = '''$($homepageContent.Replace("'", "''"))'''
homepage_arch = f'''<?xml version="1.0"?>
<odoo>
    <template id="homepage" name="FraWo Homepage v3.5">
        <t t-call="website.layout">
            <div id="wrap" class="oe_structure">
                {homepage_content}
            </div>
        </t>
    </template>
</odoo>
'''

view_ids = models.execute_kw(db, uid, password, 'ir.ui.view', 'search',
    [[('key', '=', 'website.homepage')]])

if view_ids:
    models.execute_kw(db, uid, password, 'ir.ui.view', 'write', [view_ids, {
        'arch_db': homepage_arch,
    }])
    print(f'   [OK] Homepage updated (ID: {view_ids[0]})')
else:
    view_id = models.execute_kw(db, uid, password, 'ir.ui.view', 'create', [{
        'name': 'FraWo Homepage v3.5',
        'key': 'website.homepage',
        'type': 'qweb',
        'arch_db': homepage_arch,
    }])
    print(f'   [OK] Homepage created (ID: {view_id})')

print('')
print('=' * 70)
print('[OK] DEPLOYMENT SUCCESSFUL!')
print('=' * 70)
print('')
print('Visit: https://www.frawo-tech.de')
print('')
"@

$tempScript = Join-Path $env:TEMP "frawo_deploy_v3_5.py"
$pythonScript | Out-File -FilePath $tempScript -Encoding UTF8

Write-Host "   [OK] Script created: $tempScript"

# Execute on Proxmox via SSH
Write-Host "`n[3/3] Executing on Proxmox..."

$sshCmd = @"
export ODOO_RPC_PASSWORD='Wolf2024!Frawo' && \
pct exec 220 -- su - odoo -s /bin/bash -c 'cd /usr/lib/python3/dist-packages && python3 -' < `"$($tempScript.Replace('\', '/'))`"
"@

try {
    ssh root@100.69.179.87 $sshCmd

    Write-Host "`n"
    Write-Host "=" -NoNewline
    1..69 | ForEach-Object { Write-Host "=" -NoNewline }
    Write-Host ""
    Write-Host "[OK] Deployment Complete!"
    Write-Host "=" -NoNewline
    1..69 | ForEach-Object { Write-Host "=" -NoNewline }
    Write-Host "`n"

} catch {
    Write-Host "`n[X] Deployment failed: $_"
    exit 1
}

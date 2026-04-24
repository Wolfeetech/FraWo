param()
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$proxmoxExec = Join-Path $PSScriptRoot "proxmox_windows_ssh_exec.ps1"
$websiteDir = Join-Path $repoRoot "Codex\website"
$injectScriptTpl = Join-Path $repoRoot "scripts\business\inject_website_redesign.py"

Write-Host "Reading website redesign files..."
$cssContent = Get-Content -Path (Join-Path $websiteDir "frawo_custom_css.css") -Raw -Encoding UTF8
$homeContent = Get-Content -Path (Join-Path $websiteDir "frawo_homepage_blocks.html") -Raw -Encoding UTF8
$b2bContent = Get-Content -Path (Join-Path $websiteDir "frawo_b2b_blocks.html") -Raw -Encoding UTF8
$b2cContent = Get-Content -Path (Join-Path $websiteDir "frawo_b2c_blocks.html") -Raw -Encoding UTF8
$contactContent = Get-Content -Path (Join-Path $websiteDir "frawo_contactus.html") -Raw -Encoding UTF8

Write-Host "Reading images..."
$imgDir = Join-Path $repoRoot "lifeboat\assets"
$b64AboutConsole = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $imgDir "about-console.jpg")))
$b64HeroBodensee = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $imgDir "hero-bodensee.jpg")))
$b64ReferenceEvent = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $imgDir "reference-event.jpg")))
$b64ServiceAudio = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $imgDir "service-audio.jpg")))
$b64ServiceStage = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $imgDir "service-stage.jpg")))
$b64Logo = [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $imgDir "logo.png")))

Write-Host "Reading python template..."
$pyContent = Get-Content -Path $injectScriptTpl -Raw -Encoding UTF8

Write-Host "Replacing placeholders..."
# Escape quotes for python multiline string (replace """ with \"\"\")
$pyContent = $pyContent.Replace("__CSS_CONTENT__", $cssContent.Replace('"""', '\"\"\"'))
$pyContent = $pyContent.Replace("__HOME_CONTENT__", $homeContent.Replace('"""', '\"\"\"'))
$pyContent = $pyContent.Replace("__B2B_CONTENT__", $b2bContent.Replace('"""', '\"\"\"'))
$pyContent = $pyContent.Replace("__B2C_CONTENT__", $b2cContent.Replace('"""', '\"\"\"'))
$pyContent = $pyContent.Replace("__CONTACT_CONTENT__", $contactContent.Replace('"""', '\"\"\"'))

Write-Host "Uploading images one by one using 60KB chunks..."
$images = @{
    "about-console.jpg" = $b64AboutConsole
    "hero-bodensee.jpg" = $b64HeroBodensee
    "reference-event.jpg" = $b64ReferenceEvent
    "service-audio.jpg" = $b64ServiceAudio
    "service-stage.jpg" = $b64ServiceStage
    "logo.png" = $b64Logo
}

$chunkSize = 60000

foreach ($img in $images.GetEnumerator()) {
    $imgName = $img.Key
    $imgB64 = $img.Value
    Write-Host "Uploading $imgName in chunks..."
    
    # 1. Clear the file on VM 220
    & $proxmoxExec -RemoteCommand "qm guest exec 220 -- bash -c `"rm -f /tmp/$imgName.b64`""
    
    # 2. Append chunks
    for ($i = 0; $i -lt $imgB64.Length; $i += $chunkSize) {
        $len = [Math]::Min($chunkSize, $imgB64.Length - $i)
        $chunk = $imgB64.Substring($i, $len)
        & $proxmoxExec -RemoteCommand "qm guest exec 220 -- bash -c `"echo -n '$chunk' >> /tmp/$imgName.b64`""
    }

    # 3. Copy to Odoo
    & $proxmoxExec -RemoteCommand "qm guest exec 220 -- bash -c 'docker cp /tmp/$imgName.b64 odoo-web-1:/tmp/$imgName.b64'"
    
    # 4. Create python deploy script
    $pyImgContent = @"
Attachment = env['ir.attachment']
with open('/tmp/$imgName.b64', 'r') as f:
    b64_data = f.read()

att = Attachment.search([('name', '=', '$imgName'), ('res_model', '=', 'ir.ui.view')], limit=1)
if not att:
    Attachment.create({
        'name': '$imgName',
        'type': 'binary',
        'datas': b64_data,
        'public': True,
        'res_model': 'ir.ui.view',
        'mimetype': 'image/png' if '$imgName'.endswith('.png') else 'image/jpeg',
    })
else:
    att.write({'datas': b64_data})
env.cr.commit()
"@
    
    $pyImgB64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($pyImgContent))
    $remoteImgCmd = "qm guest exec 220 -- bash -c `"echo '$pyImgB64' | base64 -d > /tmp/deploy_img.py; docker exec -i odoo-web-1 odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http < /tmp/deploy_img.py`""
    & $proxmoxExec -RemoteCommand $remoteImgCmd
}

Write-Host "Encoding script..."
# Now remove the image base64s from the main script since they are already uploaded!
# The main script will just ensure_image via search, without needing the base64 data.
$pyContent = $pyContent.Replace('"""__B64_ABOUT_CONSOLE__"""', "False")
$pyContent = $pyContent.Replace('"""__B64_HERO_BODENSEE__"""', "False")
$pyContent = $pyContent.Replace('"""__B64_REFERENCE_EVENT__"""', "False")
$pyContent = $pyContent.Replace('"""__B64_SERVICE_AUDIO__"""', "False")
$pyContent = $pyContent.Replace('"""__B64_SERVICE_STAGE__"""', "False")
$pyContent = $pyContent.Replace('"""__B64_LOGO__"""', "False")

$pyBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($pyContent))

$remoteCommand = @"
qm guest exec 220 -- bash -c "echo '$pyBase64' | base64 -d > /tmp/deploy_website.py; docker exec -i odoo-web-1 odoo shell -d FraWo_GbR --db_host=db --db_user=odoo --db_password=odoo_db_pass_final_v1 --no-http < /tmp/deploy_website.py"
"@

Write-Host "Executing on VM 220..."
& $proxmoxExec -RemoteCommand $remoteCommand
Write-Host "Done!"

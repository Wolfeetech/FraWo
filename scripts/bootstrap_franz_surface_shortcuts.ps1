param(
  [string]$TargetRoot = "",
  [switch]$IncludeMobileLinks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($TargetRoot)) {
  $desktopPath = [Environment]::GetFolderPath("Desktop")
  $TargetRoot = Join-Path $desktopPath "FRAWO Franz"
}

function Ensure-Directory {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Write-InternetShortcut {
  param(
    [string]$Path,
    [string]$Url
  )

  $content = @"
[InternetShortcut]
URL=$Url
"@
  Set-Content -LiteralPath $Path -Value $content -Encoding ASCII
}

$links = @(
  @{ Name = "00 - FRAWO Start.url"; Url = "http://portal.hs27.internal/franz/" },
  @{ Name = "01 - Nextcloud.url"; Url = "http://cloud.hs27.internal/" },
  @{ Name = "02 - Nextcloud Eingang.url"; Url = "http://cloud.hs27.internal/apps/files/?dir=/Paperless/Eingang" },
  @{ Name = "03 - Paperless.url"; Url = "http://paperless.hs27.internal/accounts/login/" },
  @{ Name = "04 - Odoo.url"; Url = "http://odoo.hs27.internal/web/login" },
  @{ Name = "05 - Vault.url"; Url = "https://vault.hs27.internal/" }
)

if ($IncludeMobileLinks) {
  $links += @(
    @{ Name = "20 - Franz Mobil Start.url"; Url = "http://100.99.206.128:8447/franz/" }
  )
}

Ensure-Directory -Path $TargetRoot

Get-ChildItem -LiteralPath $TargetRoot -Filter "*.url" -File -ErrorAction SilentlyContinue |
  Remove-Item -Force -ErrorAction Stop

foreach ($link in $links) {
  $path = Join-Path $TargetRoot $link.Name
  Write-InternetShortcut -Path $path -Url $link.Url
}

Write-Host "target_root=$TargetRoot"
Write-Host "shortcuts_created=$($links.Count)"
foreach ($link in $links) {
  Write-Host "shortcut=$($link.Name)"
}
Write-Host "status=ready"

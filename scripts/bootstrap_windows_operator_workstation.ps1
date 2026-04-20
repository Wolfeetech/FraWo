param(
  [string]$OpsShortcutFolderName = "FRAWO Ops",
  [switch]$IncludeFranzLinks
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$opsRoot = Join-Path $desktopPath $OpsShortcutFolderName
$workspaceBootstrap = Join-Path $PSScriptRoot "bootstrap_windows_workspace.ps1"
$franzBootstrap = Join-Path $PSScriptRoot "bootstrap_franz_surface_shortcuts.ps1"
$workspaceAlias = Join-Path ([Environment]::GetFolderPath("UserProfile")) ".gemini\antigravity\brain\Homeserver_2027_Ops_Workspace"

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

function Write-ShellShortcut {
  param(
    [string]$Path,
    [string]$TargetPath,
    [string]$WorkingDirectory,
    [string]$Arguments = "",
    [string]$Description = ""
  )

  $shell = New-Object -ComObject WScript.Shell
  $shortcut = $shell.CreateShortcut($Path)
  $shortcut.TargetPath = $TargetPath
  $shortcut.WorkingDirectory = $WorkingDirectory
  if (-not [string]::IsNullOrWhiteSpace($Arguments)) {
    $shortcut.Arguments = $Arguments
  }
  if (-not [string]::IsNullOrWhiteSpace($Description)) {
    $shortcut.Description = $Description
  }
  $shortcut.Save()
}

& $workspaceBootstrap

Ensure-Directory -Path $opsRoot

Get-ChildItem -LiteralPath $opsRoot -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Extension -in ".url", ".lnk" } |
  Remove-Item -Force -ErrorAction Stop

$urlShortcuts = @(
  @{ Name = "01 - Portal.url"; Url = "http://portal.hs27.internal/" },
  @{ Name = "02 - Nextcloud.url"; Url = "http://cloud.hs27.internal/" },
  @{ Name = "03 - Paperless.url"; Url = "http://paperless.hs27.internal/accounts/login/" },
  @{ Name = "04 - Odoo.url"; Url = "http://odoo.hs27.internal/web/login" },
  @{ Name = "05 - Vault.url"; Url = "https://vault.hs27.internal/" }
)

foreach ($item in $urlShortcuts) {
  Write-InternetShortcut -Path (Join-Path $opsRoot $item.Name) -Url $item.Url
}

$powershellExe = Join-Path $env:SystemRoot "System32\WindowsPowerShell\v1.0\powershell.exe"
$linkShortcuts = @(
  @{
    Name = "00 - Workspace.lnk"
    TargetPath = $workspaceAlias
    WorkingDirectory = $workspaceAlias
    Arguments = ""
    Description = "Homeserver 2027 workspace alias"
  },
  @{
    Name = "10 - Toolbox SSH.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\Toolbox-SSH.ps1`""
    Description = "Open Toolbox SSH session"
  },
  @{
    Name = "11 - PVE SSH.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\PVE-SSH.ps1`""
    Description = "Open Proxmox SSH session"
  },
  @{
    Name = "12 - Anker SSH.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\Anker-SSH.ps1`""
    Description = "Open Anker SSH session"
  },
  @{
    Name = "20 - Workspace Sync.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\scripts\auto_sync_workspace.ps1`""
    Description = "Review and sync workspace"
  },
  @{
    Name = "21 - Workstation Update.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\scripts\update_windows_operator_workstation.ps1`""
    Description = "Run controlled workstation package updates"
  },
  @{
    Name = "22 - Workstation Audit.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\scripts\tools\workstation_operator_audit.ps1`""
    Description = "Generate local workstation audit"
  },
  @{
    Name = "23 - Credential Scan.lnk"
    TargetPath = $powershellExe
    WorkingDirectory = $repoRoot
    Arguments = "-NoLogo -ExecutionPolicy Bypass -File `"$repoRoot\scripts\tools\repo_credential_scan.ps1`""
    Description = "Scan repo for credential debt"
  }
)

foreach ($item in $linkShortcuts) {
  Write-ShellShortcut `
    -Path (Join-Path $opsRoot $item.Name) `
    -TargetPath $item.TargetPath `
    -WorkingDirectory $item.WorkingDirectory `
    -Arguments $item.Arguments `
    -Description $item.Description
}

if ($IncludeFranzLinks) {
  & $franzBootstrap -IncludeMobileLinks
}

Write-Host "repo_root=$repoRoot"
Write-Host "workspace_alias=$workspaceAlias"
Write-Host "ops_shortcut_root=$opsRoot"
Write-Host "ops_shortcuts_created=$($urlShortcuts.Count + $linkShortcuts.Count)"
Write-Host "franz_links_created=$($IncludeFranzLinks.IsPresent)"
Write-Host "status=ready"

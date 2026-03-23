param(
  [string]$WorkspaceName = "Homeserver 2027 Ops Workspace",
  [string]$WorkspaceAliasName = "Homeserver_2027_Ops_Workspace",
  [string]$DesktopShortcutName = "Homeserver 2027 Workspace"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$userHome = [Environment]::GetFolderPath("UserProfile")
$desktopPath = [Environment]::GetFolderPath("Desktop")
$aliasRoot = Join-Path $userHome ".gemini\antigravity\brain"
$aliasPath = Join-Path $aliasRoot $WorkspaceAliasName
$shortcutPath = Join-Path $desktopPath ($DesktopShortcutName + ".lnk")

function Ensure-Directory {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Path $Path -Force | Out-Null
  }
}

function Ensure-WorkspaceAlias {
  param(
    [string]$AliasPath,
    [string]$TargetPath
  )

  if (Test-Path -LiteralPath $AliasPath) {
    $resolvedAlias = (Resolve-Path -LiteralPath $AliasPath).Path
    if ($resolvedAlias -eq $TargetPath) {
      return
    }

    $aliasItem = Get-Item -LiteralPath $AliasPath -Force
    if (($aliasItem.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
      Remove-Item -LiteralPath $AliasPath -Force
    } else {
      throw "Alias path already exists and is not a junction or symlink: $AliasPath"
    }
  }

  New-Item -ItemType Junction -Path $AliasPath -Target $TargetPath | Out-Null
}

function Write-DesktopShortcut {
  param(
    [string]$ShortcutPath,
    [string]$TargetPath,
    [string]$WorkingDirectory,
    [string]$Description
  )

  $shell = New-Object -ComObject WScript.Shell
  $shortcut = $shell.CreateShortcut($ShortcutPath)
  $shortcut.TargetPath = $TargetPath
  $shortcut.WorkingDirectory = $WorkingDirectory
  $shortcut.Description = $Description
  $shortcut.Save()
}

Ensure-Directory -Path $aliasRoot
Ensure-WorkspaceAlias -AliasPath $aliasPath -TargetPath $repoRoot
Write-DesktopShortcut `
  -ShortcutPath $shortcutPath `
  -TargetPath $aliasPath `
  -WorkingDirectory $aliasPath `
  -Description $WorkspaceName

Write-Host "workspace_name=$WorkspaceName"
Write-Host "workspace_repo_root=$repoRoot"
Write-Host "workspace_alias=$aliasPath"
Write-Host "desktop_shortcut=$shortcutPath"
Write-Host "status=ready"

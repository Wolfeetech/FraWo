param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$workspaceAlias = Join-Path ([Environment]::GetFolderPath("UserProfile")) ".gemini\antigravity\brain\Homeserver_2027_Ops_Workspace"
$opsFolder = Join-Path $desktopPath "FRAWO Ops"
$artifactRoot = Join-Path $repoRoot "artifacts\workstation_audit"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$artifactDir = Join-Path $artifactRoot $timestamp
$reportPath = Join-Path $artifactDir "workstation_audit.md"
$wingetRawPath = Join-Path $artifactDir "winget_upgrade.txt"
$processRawPath = Join-Path $artifactDir "blocked_processes.txt"

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

function Test-ShortcutFolder {
  param([string]$Path)

  if (-not (Test-Path -LiteralPath $Path)) {
    return @{
      Exists = $false
      Count = 0
    }
  }

  $items = Get-ChildItem -LiteralPath $Path -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Extension -in ".url", ".lnk" }
  return @{
    Exists = $true
    Count = @($items).Count
  }
}

function Get-TrackedRootMarkdownCount {
  return @(Get-ChildItem -LiteralPath $repoRoot -File -Filter *.md).Count
}

function Invoke-SafeCommand {
  param(
    [scriptblock]$Script,
    [string]$Fallback = "unavailable"
  )

  try {
    return & $Script
  } catch {
    return $Fallback
  }
}

$opsState = Test-ShortcutFolder -Path $opsFolder
$rootMarkdownCount = Get-TrackedRootMarkdownCount
$gitStatus = git -C $repoRoot status --short
$gitBranch = git -C $repoRoot status --short --branch | Select-Object -First 1
$sshCheck = Invoke-SafeCommand -Script { ssh -o BatchMode=yes -F (Join-Path $repoRoot "Codex\ssh_config") toolbox "echo ok" }
$blockedProcesses = Get-Process -ErrorAction SilentlyContinue |
  Where-Object { $_.ProcessName -match 'chrome|msedge|Antigravity|AnyDesk|Docker Desktop|com.docker|obs64|wireguard|winget|msiexec' } |
  Select-Object ProcessName, Id, StartTime, MainWindowTitle
$blockedProcesses | Out-File -LiteralPath $processRawPath -Encoding utf8

$wingetUpgrade = Invoke-SafeCommand -Script { winget upgrade } -Fallback "winget upgrade failed"
$wingetUpgrade | Out-File -LiteralPath $wingetRawPath -Encoding utf8

$lines = @(
  "# Workstation Audit",
  "",
  "- Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
  "- Repo root: $repoRoot",
  "- Git branch: $gitBranch",
  "- Workspace alias exists: $(Test-Path -LiteralPath $workspaceAlias)",
  "- Workspace desktop shortcut exists: $(Test-Path -LiteralPath (Join-Path $desktopPath 'Homeserver 2027 Workspace.lnk'))",
  "- Ops folder exists: $($opsState.Exists)",
  "- Ops shortcut count: $($opsState.Count)",
  "- Root markdown files: $rootMarkdownCount",
  "- Toolbox SSH batch check: $sshCheck",
  "",
  "## Git Status",
  ""
)

if ($gitStatus) {
  $lines += ($gitStatus | ForEach-Object { "- $_" })
} else {
  $lines += "- working_tree=clean"
}

$lines += @(
  "",
  "## Raw Artifacts",
  "",
  "- blocked processes: artifacts/workstation_audit/$timestamp/blocked_processes.txt",
  "- winget upgrade output: artifacts/workstation_audit/$timestamp/winget_upgrade.txt"
)

$lines | Set-Content -LiteralPath $reportPath -Encoding utf8

Write-Host "report_path=$reportPath"
Write-Host "blocked_processes_path=$processRawPath"
Write-Host "winget_upgrade_path=$wingetRawPath"
Write-Host "status=ready"

param(
  [switch]$IncludeBrowsers,
  [switch]$IncludeInteractiveApps,
  [int]$WingetTimeoutSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$updates = @(
  @{
    Id = "Bitwarden.CLI"
    Label = "Bitwarden CLI"
    Processes = @()
    Enabled = $true
  },
  @{
    Id = "WireGuard.WireGuard"
    Label = "WireGuard"
    Processes = @("wireguard")
    Enabled = $true
  },
  @{
    Id = "OBSProject.OBSStudio"
    Label = "OBS Studio"
    Processes = @("obs64")
    Enabled = $true
  },
  @{
    Id = "Google.Chrome.EXE"
    Label = "Google Chrome"
    Processes = @("chrome")
    Enabled = $IncludeBrowsers.IsPresent
  },
  @{
    Id = "Microsoft.Edge"
    Label = "Microsoft Edge"
    Processes = @("msedge")
    Enabled = $IncludeBrowsers.IsPresent
  },
  @{
    Id = "Google.Antigravity"
    Label = "Antigravity"
    Processes = @("Antigravity")
    Enabled = $IncludeInteractiveApps.IsPresent
  },
  @{
    Id = "AnyDesk.AnyDesk"
    Label = "AnyDesk"
    Processes = @("AnyDesk")
    Enabled = $IncludeInteractiveApps.IsPresent
  },
  @{
    Id = "Docker.DockerDesktop"
    Label = "Docker Desktop"
    Processes = @("Docker Desktop", "com.docker.backend", "com.docker.build")
    Enabled = $IncludeInteractiveApps.IsPresent
  },
  @{
    Id = "Microsoft.WSL"
    Label = "Windows Subsystem for Linux"
    Processes = @("wsl", "wslservice")
    Enabled = $IncludeInteractiveApps.IsPresent
  }
)

function Get-RunningProcessNames {
  Get-Process -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName -Unique
}

function Invoke-WingetUpgrade {
  param(
    [string]$Id,
    [int]$TimeoutSeconds
  )

  $safeId = ($Id -replace '[^A-Za-z0-9]+', '_')
  $token = [guid]::NewGuid().ToString("N")
  $stdoutPath = Join-Path $env:TEMP "winget_${safeId}_${token}.stdout.log"
  $stderrPath = Join-Path $env:TEMP "winget_${safeId}_${token}.stderr.log"
  $args = @(
    "upgrade",
    "--id", $Id,
    "--accept-source-agreements",
    "--accept-package-agreements",
    "--silent",
    "--disable-interactivity"
  )

  try {
    $process = Start-Process -FilePath "winget" -ArgumentList $args -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru -WindowStyle Hidden
    $finished = $process.WaitForExit($TimeoutSeconds * 1000)

    if (-not $finished) {
      Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
      $stdout = if (Test-Path $stdoutPath) { Get-Content -Raw $stdoutPath } else { "" }
      $stderr = if (Test-Path $stderrPath) { Get-Content -Raw $stderrPath } else { "" }
      $text = (($stdout, $stderr) -join [Environment]::NewLine).Trim()
      return @{
        Status = "timed_out"
        ExitCode = -1
        Output = $text
      }
    }

    $stdout = if (Test-Path $stdoutPath) { Get-Content -Raw $stdoutPath } else { "" }
    $stderr = if (Test-Path $stderrPath) { Get-Content -Raw $stderrPath } else { "" }
    $exitCode = $process.ExitCode
    $text = (($stdout, $stderr) -join [Environment]::NewLine).Trim()
  }
  finally {
    Remove-Item -LiteralPath $stdoutPath, $stderrPath -ErrorAction SilentlyContinue
  }

  if ($text -match "Kein.*Upgrade gefunden|keine neueren Paketversionen|No available upgrade found|No newer package versions are available") {
    return @{
      Status = "up_to_date"
      ExitCode = 0
      Output = $text
    }
  }

  if ($exitCode -eq 0) {
    return @{
      Status = "updated"
      ExitCode = 0
      Output = $text
    }
  }

  if ($text -match "abgebrochen|aborted|cancelled|canceled") {
    return @{
      Status = "aborted"
      ExitCode = $exitCode
      Output = $text
    }
  }

  return @{
    Status = "failed"
    ExitCode = $exitCode
    Output = $text
  }
}

$running = Get-RunningProcessNames
$summary = New-Object System.Collections.Generic.List[string]

foreach ($update in $updates) {
  if (-not $update.Enabled) {
    $summary.Add("skipped=$($update.Id):disabled_by_default")
    continue
  }

  $blockers = @($update.Processes | Where-Object { $running -contains $_ })
  if ($blockers.Count -gt 0) {
    $summary.Add("skipped=$($update.Id):blocked_by_processes=$($blockers -join ',')")
    continue
  }

  Write-Host "updating=$($update.Id)"
  $result = Invoke-WingetUpgrade -Id $update.Id -TimeoutSeconds $WingetTimeoutSeconds
  $summary.Add("result=$($update.Id):status=$($result.Status):exit_code=$($result.ExitCode)")
}

$summary | ForEach-Object { Write-Host $_ }

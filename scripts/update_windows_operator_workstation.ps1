param(
  [switch]$IncludeBrowsers,
  [switch]$IncludeInteractiveApps,
  [int]$WingetTimeoutSeconds = 180
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$updates = @(
  @{
    Id = "Docker.DockerDesktop"
    Label = "Docker Desktop"
    Processes = @("Docker Desktop", "com.docker.backend", "com.docker.build")
    Enabled = $true
  },
  @{
    Id = "RaspberryPiFoundation.RaspberryPiImager"
    Label = "Raspberry Pi Imager"
    Processes = @("RaspberryPiImager")
    Enabled = $true
  },
  @{
    Id = "Apple.Bonjour"
    Label = "Bonjour"
    Processes = @()
    Enabled = $true
  },
  @{
    Id = "Wibu-Systems.CodeMeterRuntimeKit"
    Label = "CodeMeter Runtime Kit"
    Processes = @("CodeMeter", "CodeMeterCC")
    Enabled = $true
  },
  @{
    Id = "dorssel.usbipd-win"
    Label = "usbipd-win"
    Processes = @("usbipd")
    Enabled = $true
  },
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
    Id = "Microsoft.VCRedist.2010.x86"
    Label = "Microsoft Visual C++ 2010 x86 Redistributable"
    Processes = @()
    Enabled = $true
  },
  @{
    Id = "Microsoft.VCRedist.2015+.x64"
    Label = "Microsoft Visual C++ 2015-2022 x64 Redistributable"
    Processes = @()
    Enabled = $true
  },
  @{
    Id = "XP9KHM4BK9FZ7Q"
    Label = "Microsoft Visual Studio Code (User)"
    Processes = @("Code")
    Enabled = $true
  },
  @{
    Id = "Microsoft.Teams"
    Label = "Microsoft Teams"
    Processes = @("Teams", "ms-teams")
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
    Id = "Microsoft.WSL"
    Label = "Windows Subsystem for Linux"
    Processes = @("wsl", "wslservice")
    Enabled = $IncludeInteractiveApps.IsPresent
  }
)

function Get-RunningProcessNames {
  Get-Process -ErrorAction SilentlyContinue | Select-Object -ExpandProperty ProcessName -Unique
}

function Stop-NewMsiexecProcesses {
  param([int[]]$KnownProcessIds)

  $known = @($KnownProcessIds | Where-Object { $_ -is [int] })
  $newMsiexec = Get-Process -Name "msiexec" -ErrorAction SilentlyContinue | Where-Object { $known -notcontains $_.Id }
  foreach ($process in $newMsiexec) {
    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
  }
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
  $knownMsiexecIds = @(Get-Process -Name "msiexec" -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id)

  try {
    $process = Start-Process -FilePath "winget" -ArgumentList $args -RedirectStandardOutput $stdoutPath -RedirectStandardError $stderrPath -PassThru -WindowStyle Hidden
    $finished = $process.WaitForExit($TimeoutSeconds * 1000)

    if (-not $finished) {
      Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
      $stdout = if (Test-Path $stdoutPath) { Get-Content -Raw $stdoutPath } else { "" }
      $stderr = if (Test-Path $stderrPath) { Get-Content -Raw $stderrPath } else { "" }
      $text = (($stdout, $stderr) -join [Environment]::NewLine).Trim()
      Stop-NewMsiexecProcesses -KnownProcessIds $knownMsiexecIds

      if ($text -match "Administrator an|Administrator prompt|run as administrator|requires elevation|Prompt erwartet") {
        return @{
          Status = "requires_elevation"
          ExitCode = -2
          Output = $text
        }
      }

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

  if ($text -match "Administrator an|Administrator prompt|run as administrator|requires elevation|Prompt erwartet") {
    Stop-NewMsiexecProcesses -KnownProcessIds $knownMsiexecIds
    return @{
      Status = "requires_elevation"
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

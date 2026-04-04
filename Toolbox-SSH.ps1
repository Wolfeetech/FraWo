param(
  [string]$ComputerName = "toolbox",
  [string]$FallbackIp = "100.99.206.128",
  [string]$Username = "root"
)

function Test-SshPort {
  param([string]$Target)

  try {
    return Test-NetConnection -ComputerName $Target -Port 22 -InformationLevel Quiet -WarningAction SilentlyContinue
  } catch {
    return $false
  }
}

$target = $ComputerName
if (-not (Test-SshPort -Target $target)) {
  if (Test-SshPort -Target $FallbackIp) {
    $target = $FallbackIp
  } else {
    Write-Host "Toolbox ist aktuell nicht per SSH erreichbar." -ForegroundColor Yellow
    exit 2
  }
}

ssh -o "StrictHostKeyChecking=accept-new" "$Username@$target"

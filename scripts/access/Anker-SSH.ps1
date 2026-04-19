param(
  [string]$ComputerName = "proxmox-anker",
  [string]$FallbackIp = "100.69.179.87",
  [string]$Username = "root"
)

$ssh = "C:\Windows\System32\OpenSSH\ssh.exe"
$sshConfig = Join-Path $PSScriptRoot "Codex\ssh_config"

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
    Write-Host "Proxmox-Anker ist aktuell nicht per SSH erreichbar." -ForegroundColor Yellow
    exit 2
  }
}

& $ssh -F $sshConfig "$Username@$target"

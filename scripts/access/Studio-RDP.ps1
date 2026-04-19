param(
  [string]$ComputerName = "wolfstudiopc.tail150400.ts.net",
  [string]$FallbackIp = "100.98.31.60",
  [string]$Username = ""
)

function Test-RdpPort {
  param([string]$Target)

  try {
    return Test-NetConnection -ComputerName $Target -Port 3389 -InformationLevel Quiet -WarningAction SilentlyContinue
  } catch {
    return $false
  }
}

$target = $ComputerName
if (-not (Test-RdpPort -Target $target)) {
  if (Test-RdpPort -Target $FallbackIp) {
    $target = $FallbackIp
  } else {
    Write-Host "RDP auf Studio-PC ist aktuell nicht erreichbar." -ForegroundColor Yellow
    Write-Host "Geprueft wurden: $ComputerName und $FallbackIp (Port 3389)." -ForegroundColor Yellow
    Write-Host "Wahrscheinliche Ursache: RDP/Firewall auf wolfstudiopc ist noch nicht freigeschaltet." -ForegroundColor Yellow
    exit 2
  }
}

if ($Username) {
  cmdkey /generic:"TERMSRV/$target" /user:$Username | Out-Null
}

$rdpFile = Join-Path $env:TEMP "wolfstudiopc-tailnet.rdp"
@"
full address:s:$target
prompt for credentials on client:i:1
administrative session:i:1
authentication level:i:2
enablecredsspsupport:i:1
redirectclipboard:i:1
redirectprinters:i:0
redirectsmartcards:i:0
screen mode id:i:2
use multimon:i:0
"@ | Set-Content -Path $rdpFile -Encoding ASCII

Start-Process -FilePath "mstsc.exe" -ArgumentList "`"$rdpFile`""

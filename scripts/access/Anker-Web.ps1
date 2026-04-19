param(
  [string]$PrimaryUrl = "https://proxmox-anker:8006",
  [string]$FallbackUrl = "https://100.69.179.87:8006"
)

function Test-TcpPort {
  param(
    [string]$HostName,
    [int]$Port
  )

  try {
    $client = [System.Net.Sockets.TcpClient]::new()
    $iar = $client.BeginConnect($HostName, $Port, $null, $null)
    if (-not $iar.AsyncWaitHandle.WaitOne(3000, $false)) {
      $client.Close()
      return $false
    }
    $client.EndConnect($iar)
    $client.Close()
    return $true
  } catch {
    return $false
  }
}

$uri = [Uri]$PrimaryUrl
$targetUrl = $PrimaryUrl
if (-not (Test-TcpPort -HostName $uri.Host -Port $uri.Port)) {
  $fallbackUri = [Uri]$FallbackUrl
  if (Test-TcpPort -HostName $fallbackUri.Host -Port $fallbackUri.Port) {
    $targetUrl = $FallbackUrl
  } else {
    Write-Host "Proxmox Anker ist aktuell nicht ueber Port 8006 erreichbar." -ForegroundColor Yellow
    exit 2
  }
}

Start-Process $targetUrl

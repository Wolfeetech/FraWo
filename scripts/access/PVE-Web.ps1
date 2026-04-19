param(
  [string]$PrimaryUrl = "https://pve:8006",
  [string]$FallbackUrl = "https://100.91.20.116:8006"
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
    Write-Host "PVE-Webinterface ist aktuell nicht erreichbar." -ForegroundColor Yellow
    Write-Host "Geprueft wurden: $PrimaryUrl und $FallbackUrl." -ForegroundColor Yellow
    exit 2
  }
}

Start-Process $targetUrl

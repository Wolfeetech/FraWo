param(
  [switch]$Background,
  [switch]$Verify
)

$sshArgs = @(
  '-N',
  'hs27-surface-portal'
)

if ($Verify) {
  $existing = Get-CimInstance Win32_Process | Where-Object {
    $_.Name -eq 'ssh.exe' -and $_.CommandLine -match 'hs27-surface-portal'
  }
  foreach ($process in $existing) {
    Stop-Process -Id $process.ProcessId -Force
  }

  $process = Start-Process -FilePath 'ssh' -ArgumentList $sshArgs -PassThru -WindowStyle Hidden
  Start-Sleep -Seconds 3

  try {
    $status = & curl.exe -sS -o NUL -w '%{http_code}' http://127.0.0.1:27827/
    $html = & curl.exe -sS http://127.0.0.1:27827/
    $titleMatch = [regex]::Match($html, '<title>([^<]+)</title>')
    $title = if ($titleMatch.Success) { $titleMatch.Groups[1].Value } else { '-' }

    Write-Output "surface_portal_tunnel_http=$status"
    Write-Output "surface_portal_tunnel_title=$title"
    if ($status -eq '200') {
      Write-Output 'surface_portal_tunnel_status=verified'
    } else {
      Write-Output 'surface_portal_tunnel_status=failed'
      exit 1
    }
  } finally {
    if ($process -and -not $process.HasExited) {
      Stop-Process -Id $process.Id -Force
    }
  }
} elseif ($Background) {
  Start-Process -FilePath 'ssh' -ArgumentList $sshArgs -WindowStyle Hidden | Out-Null
  Write-Output 'surface_portal_tunnel=started_background'
  Write-Output 'surface_portal_local_url=http://127.0.0.1:27827/'
} else {
  & ssh @sshArgs
}

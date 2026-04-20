$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$artifactDir = Join-Path $repoRoot "artifacts\workstation_alpha_tunnel"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$logFile = Join-Path $artifactDir "tunnel_alpha_$timestamp.log"
$errFile = Join-Path $artifactDir "tunnel_alpha_$timestamp.err"
$target = "http://10.1.0.22:8069"

New-Item -ItemType Directory -Path $artifactDir -Force | Out-Null

Write-Host "Starting Alpha Tunnel to $target..."
Write-Host "log_file=$logFile"
Write-Host "err_file=$errFile"
Start-Process -FilePath "cloudflared.exe" -ArgumentList "tunnel --url $target" -NoNewWindow -RedirectStandardOutput $logFile -RedirectStandardError $errFile
Start-Sleep -Seconds 15
Get-Content $logFile

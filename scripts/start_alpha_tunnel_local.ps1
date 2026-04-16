$logFile = "C:\Users\StudioPC\Workspace\FraWo\tunnel_alpha.log"
$errFile = "C:\Users\StudioPC\Workspace\FraWo\tunnel_alpha.err"
$target = "http://10.1.0.22:8069"

Write-Host "Starting Alpha Tunnel to $target..."
Start-Process -FilePath "cloudflared.exe" -ArgumentList "tunnel --url $target" -NoNewWindow -RedirectStandardOutput $logFile -RedirectStandardError $errFile
Start-Sleep -Seconds 15
Get-Content $logFile

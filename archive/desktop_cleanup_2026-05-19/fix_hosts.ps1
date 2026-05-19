# Fix outdated Tailscale IP in hosts file
# Old IP: 100.99.206.128
# New IP: 100.82.26.53 (toolbox)

$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$content = Get-Content $hostsPath
$newContent = $content -replace '100\.99\.206\.128', '100.82.26.53'
Set-Content -Path $hostsPath -Value $newContent -Force

Write-Host "Hosts file updated successfully!"
Write-Host "Old IP: 100.99.206.128"
Write-Host "New IP: 100.82.26.53"

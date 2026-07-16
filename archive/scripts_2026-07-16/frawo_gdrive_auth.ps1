# FraWo rclone Google Drive Auth
$tokenFile = "$env:TEMP\frawo_gdrive_token.json"

Write-Host "FraWo Google Drive Auth" -ForegroundColor Cyan
Write-Host "Account: w.prinz1101@gmail.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "Browser oeffnet sich gleich..." -ForegroundColor Green

$rcloneBin = "C:\Users\StudioPC\AppData\Local\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe\rclone-v1.74.2-windows-amd64\rclone.exe"
$result = & $rcloneBin authorize "drive" --drive-use-trash=false 2>&1

$tokenLine = $result | Where-Object { $_ -match '"access_token"' } | Select-Object -Last 1

if (-not $tokenLine) {
    $joined = $result -join "`n"
    $match = [regex]::Match($joined, '\{"access_token[^}]+\}')
    if ($match.Success) { $tokenLine = $match.Value }
}

if ($tokenLine) {
    $tokenLine | Out-File -FilePath $tokenFile -Encoding utf8
    Write-Host ""
    Write-Host "[OK] Token gespeichert: $tokenFile" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Ausgabe von rclone authorize:" -ForegroundColor Yellow
    $result | ForEach-Object { Write-Host $_ }
    $result -join "`n" | Out-File -FilePath $tokenFile -Encoding utf8
    Write-Host "Datei: $tokenFile" -ForegroundColor Gray
}

Write-Host "Weiter in Claude Code." -ForegroundColor Cyan

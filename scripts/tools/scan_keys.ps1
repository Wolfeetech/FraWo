$sshRoot = Join-Path $HOME ".ssh"
if (-not (Test-Path -LiteralPath $sshRoot)) {
    throw "SSH directory not found: $sshRoot"
}

$keys = Get-ChildItem -Path $sshRoot -File | Where-Object { -not $_.Name.EndsWith(".pub") -and -not $_.Name.Contains("known") -and -not $_.Name.Contains("config") }

foreach ($key in $keys) {
    Write-Host "Testing key: $($key.FullName)"
    ssh -o StrictHostKeyChecking=no -i $key.FullName -o BatchMode=yes frawo@100.106.67.127 'whoami'
}

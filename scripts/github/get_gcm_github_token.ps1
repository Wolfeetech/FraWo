$ErrorActionPreference = 'Stop'

$credentialInput = "protocol=https`nhost=github.com`nusername=Wolfeetech`n`n"
$credLines = $credentialInput | git credential fill
$tokenLine = $credLines | Where-Object { $_ -like 'password=*' } | Select-Object -First 1

if (-not $tokenLine) {
  throw 'No GitHub token/password available from Git Credential Manager.'
}

$token = $tokenLine.Substring('password='.Length)
if ([string]::IsNullOrWhiteSpace($token)) {
  throw 'Empty GitHub token/password from Git Credential Manager.'
}

$token

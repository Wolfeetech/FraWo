[CmdletBinding()]
param(
    [string]$BootstrapPath = "$env:LOCALAPPDATA\Homeserver2027\bootstrap\vaultwarden_admin_token.txt",
    [string]$AdminUrl = "https://vault.hs27.internal/admin"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $BootstrapPath)) {
    throw "Bootstrap path not found: $BootstrapPath"
}

$token = [System.IO.File]::ReadAllText($BootstrapPath).Trim()
if ([string]::IsNullOrWhiteSpace($token)) {
    throw "Bootstrap token is empty: $BootstrapPath"
}

$cookiePath = Join-Path $env:TEMP "vaultwarden_admin_cookie.txt"
if (Test-Path $cookiePath) {
    Remove-Item $cookiePath -Force
}

& curl.exe -k -s -c $cookiePath --data-urlencode "token=$token" $AdminUrl | Out-Null
$html = & curl.exe -k -s -b $cookiePath $AdminUrl
Remove-Item $cookiePath -Force -ErrorAction SilentlyContinue

if ($html -match "Admin Settings" -or $html -match "SMTP Settings" -or (($html -match "Vaultwarden Admin Panel") -and ($html -notmatch "Enter admin token"))) {
    Write-Output "vaultwarden_admin_login_ready=yes"
    exit 0
}

Write-Output "vaultwarden_admin_login_ready=no"
exit 1

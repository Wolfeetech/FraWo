[CmdletBinding()]
param(
    [string]$Username = ""
)

$ErrorActionPreference = "Stop"

function Convert-ToWslPath {
    param(
        [Parameter(Mandatory = $true)]
        [string]$WindowsPath
    )

    $resolved = (Resolve-Path $WindowsPath).Path
    $drive = $resolved.Substring(0, 1).ToLowerInvariant()
    $rest = $resolved.Substring(2).Replace("\", "/")
    return "/mnt/$drive$rest"
}

$workspaceRoot = Split-Path -Parent $PSScriptRoot
$workspaceWslPath = Convert-ToWslPath -WindowsPath $workspaceRoot
$runtimeVarsPath = Join-Path $workspaceRoot "ansible\inventory\group_vars\all\mail_runtime.local.yml"

if ([string]::IsNullOrWhiteSpace($Username) -and (Test-Path $runtimeVarsPath)) {
    $configuredUser = Select-String -Path $runtimeVarsPath -Pattern '^\s*homeserver_mail_smtp_auth_username:\s*(.+?)\s*$' | Select-Object -First 1
    if ($configuredUser) {
        $Username = $configuredUser.Matches[0].Groups[1].Value.Trim()
    }
}

if ([string]::IsNullOrWhiteSpace($Username) -or $Username -eq "webmaster@example.tld") {
    throw "Setze zuerst den echten SMTP-Login in ansible\\inventory\\group_vars\\all\\mail_runtime.local.yml oder uebergib -Username."
}

$previousEnabled = $env:HOMESERVER_MAIL_APP_SMTP_ENABLED
$previousUser = $env:HOMESERVER_MAIL_SMTP_AUTH_USERNAME
$previousPassword = $env:HOMESERVER_MAIL_SMTP_PASSWORD

$securePassword = Read-Host -AsSecureString "STRATO SMTP Passwort fuer $Username"
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)

try {
    $plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    if ([string]::IsNullOrWhiteSpace($plainPassword)) {
        throw "Kein SMTP-Passwort eingegeben."
    }

    $env:HOMESERVER_MAIL_APP_SMTP_ENABLED = "true"
    $env:HOMESERVER_MAIL_SMTP_AUTH_USERNAME = $Username
    $env:HOMESERVER_MAIL_SMTP_PASSWORD = $plainPassword

    $bashCommand = "cd `"$workspaceWslPath`" && make app-smtp-deploy && make app-smtp-check"
    & bash -lc $bashCommand
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}
finally {
    if ($null -ne $bstr -and $bstr -ne [IntPtr]::Zero) {
        [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
    }

    if ($null -eq $previousEnabled) {
        Remove-Item Env:HOMESERVER_MAIL_APP_SMTP_ENABLED -ErrorAction SilentlyContinue
    } else {
        $env:HOMESERVER_MAIL_APP_SMTP_ENABLED = $previousEnabled
    }

    if ($null -eq $previousUser) {
        Remove-Item Env:HOMESERVER_MAIL_SMTP_AUTH_USERNAME -ErrorAction SilentlyContinue
    } else {
        $env:HOMESERVER_MAIL_SMTP_AUTH_USERNAME = $previousUser
    }

    if ($null -eq $previousPassword) {
        Remove-Item Env:HOMESERVER_MAIL_SMTP_PASSWORD -ErrorAction SilentlyContinue
    } else {
        $env:HOMESERVER_MAIL_SMTP_PASSWORD = $previousPassword
    }
}

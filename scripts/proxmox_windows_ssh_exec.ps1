param(
    [string]$RemoteCommand,

    [string]$RemoteCommandBase64,

    [string]$SshHost = "proxmox-anker"
)

if (-not $RemoteCommandBase64) {
    if (-not $RemoteCommand) {
        throw "Either -RemoteCommand or -RemoteCommandBase64 is required."
    }
    $RemoteCommandBase64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($RemoteCommand))
}

$payload = $RemoteCommandBase64
$remoteShell = "bash -lc 'base64 -d | bash'"

$root = Split-Path -Parent $PSScriptRoot
$sshConfig = Join-Path $root "Codex\ssh_config"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Output $payload -NoEnumerate | & ssh -T -o BatchMode=yes -F $sshConfig $SshHost $remoteShell
exit $LASTEXITCODE

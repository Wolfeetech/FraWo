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
$remoteShell = "bash -lc 'echo $payload | base64 -d | bash'"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
& ssh -T -o BatchMode=yes -o StrictHostKeyChecking=accept-new $SshHost $remoteShell
exit $LASTEXITCODE
